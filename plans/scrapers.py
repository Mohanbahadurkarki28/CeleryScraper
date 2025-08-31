from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

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


def scrape_host_plans(
    provider_name,
    url,
    price_selector=".price, .plan, .payment, .hosting, .hostingplan, .priceplan",
):
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

                price_text = price_el.text.strip()
                plan_data = {
                    "provider_name": provider_name,
                    "plan_name": plan_name or "Unknown Plan",
                    "hosting_type": "Cloud Hosting",
                    "price": price_text.split('\n')[0] if price_text else "Look inside",
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

    # Only add snapshot if price changed
    latest = HostingPlanSnapshot.objects.filter(hosting_plan=plan).order_by('-created_at').first()
    if not latest or latest.price != plan_data["price"]:
        HostingPlanSnapshot.objects.create(
            hosting_plan=plan,
            price=plan_data["price"]
        )


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
