from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging
from decimal import Decimal, InvalidOperation
import re

from .models import HostingPlan, HostingPlanSnapshot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def clean_plan_name(plan_name):
    """Trim plan_name at first full stop or max 20 characters."""
    if not plan_name:
        return "Unknown Plan"
    if '.' in plan_name:
        plan_name = plan_name.split('.')[0]
    return plan_name.strip()[:20]



def clean_price(price_text):
    """Extract a clean numeric price from any format like '$2.99/mo' or 'NPR 350 / month'."""
    if not price_text:
        return Decimal("0.00")
    price_text = price_text.replace(",", "")  # Remove thousands separator
    price_match = re.search(r"(\d+(\.\d{1,2})?)", price_text)
    if price_match:
        try:
            return Decimal(price_match.group(1))
        except InvalidOperation:
            return Decimal("0.00")
    return Decimal("0.00")



def normalize_price(value):
    value = str(value).strip()
    value = re.sub(r"[^\d.]", "", value)
    return Decimal(value) if value else None



def scrape_host_plans(
    provider_name,
    url,
    price_selector=".price, .plan, .payment, .hosting, .hostingplan, .priceplan",
):
    """Scrapes hosting plans from a provider's URL."""
    scraped_plans = []
    logger.info(f"Starting scrape for {provider_name}...")

    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.get(url)

    try:
        price_elements = driver.find_elements(By.CSS_SELECTOR, price_selector)
        logger.info(f"Found {len(price_elements)} price elements for {provider_name}.")

        for price_el in price_elements:
            try:
                container = price_el.find_element(By.XPATH, "../../..")
                plan_name = None

                # Extract plan name from headers/divs
                for tag in ["h3", "h2", "div"]:
                    try:
                        elem = container.find_element(By.TAG_NAME, tag)
                        text = elem.text.strip()
                        if text:
                            plan_name = clean_plan_name(text)
                            break
                    except NoSuchElementException:
                        continue

                # Get and clean price
                price_text = price_el.text.strip()
                clean_price_value = clean_price(price_text)

                plan_data = {
                    "provider_name": provider_name,
                    "plan_name": plan_name or "Unknown Plan",
                    "hosting_type": "Cloud Hosting",
                    "price": clean_price_value,
                    "storage": "Unlimited",
                    "bandwidth": "Unlimited",
                    "url": url,
                }
                scraped_plans.append(plan_data)

            except Exception as e:
                logger.warning(f"Skipping a plan for {provider_name} due to error: {e}")

        logger.info(f"Scraped {len(scraped_plans)} plans for {provider_name}.")

    finally:
        driver.quit()

    return scraped_plans



def save_scraped_plan(plan_data):
    """Save scraped plan to DB; snapshot only if price changed."""
    plan, created = HostingPlan.objects.get_or_create(
        provider_name=plan_data["provider_name"],
        plan_name=plan_data["plan_name"],
        defaults={
            "hosting_type": plan_data.get("hosting_type", ""),
            "price": plan_data["price"],
            "storage": plan_data.get("storage", ""),
            "bandwidth": plan_data.get("bandwidth", ""),
            "api_available": plan_data.get("api_available", False),
            "notes": plan_data.get("notes", ""),
            "url": plan_data.get("url", ""),
        },
    )

    if created:
        # New plan → always add initial snapshot
        HostingPlanSnapshot.objects.create(
            hosting_plan=plan,
            price=plan_data["price"]
        )
    else:
        # Existing plan → check if price changed
        latest_snapshot = HostingPlanSnapshot.objects.filter(hosting_plan=plan).order_by('-created_at').first()
        if not latest_snapshot or latest_snapshot.price != plan_data["price"]:
            HostingPlanSnapshot.objects.create(
                hosting_plan=plan,
                price=plan_data["price"]
            )
            plan.price = plan_data["price"]
            plan.save()
            logger.info(f"Price changed for {plan.plan_name} → Snapshot saved ✅")



def scrape_all_providers():
    """Scrape all providers and save results in DB."""
    all_plans = []

    providers = [
        ("Babal Host", "https://babal.host/"),
        ("WebHost Nepal", "https://www.webhostnepal.com/hosting"),
        ("Himalayan Host", "https://www.himalayanhost.com/store/web-hosting-nepal"),
        ("Siteground Host", "https://world.siteground.com/web-hosting.htm"),
    ]

    for provider_name, url in providers:
        scraped = scrape_host_plans(provider_name, url)
        all_plans.extend(scraped)

        # Save each plan in DB
        for plan in scraped:
            save_scraped_plan(plan)

    return all_plans
