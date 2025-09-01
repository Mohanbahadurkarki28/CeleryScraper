from celery import shared_task, chord
from decimal import Decimal
from datetime import datetime
import logging
from .models import HostingPlan, HostingPlanSnapshot
from .scrapers import scrape_host_plans

logger = logging.getLogger(__name__)

# Global dict to track timings
SCRAPE_TIMINGS = {}


def save_scraped_data(scraped_data):
    """Save scraped data into HostingPlan & HostingPlanSnapshot tables."""
    for plan in scraped_data:
        provider_name = plan["provider_name"]
        plan_name = plan["plan_name"]
        new_price = plan.get("price", Decimal("0.00"))

        # Get or create the hosting plan
        hosting_plan, created = HostingPlan.objects.get_or_create(
            provider_name=provider_name,
            plan_name=plan_name,
            defaults={
                "hosting_type": plan.get("hosting_type", ""),
                "price": new_price,
                "storage": plan.get("storage", ""),
                "bandwidth": plan.get("bandwidth", ""),
                "url": plan.get("url", ""),
            },
        )

        # Create snapshot if new plan or price changed
        if created:
            HostingPlanSnapshot.objects.create(
                hosting_plan=hosting_plan,
                price=new_price
            )
        else:
            latest_snapshot = HostingPlanSnapshot.objects.filter(
                hosting_plan=hosting_plan
            ).order_by('-created_at').first()

            if not latest_snapshot or latest_snapshot.price != new_price:
                HostingPlanSnapshot.objects.create(
                    hosting_plan=hosting_plan,
                    price=new_price
                )
                hosting_plan.price = new_price
                hosting_plan.save()
                logger.info(f"💰 Price changed for {plan_name}: Snapshot saved ✅")


@shared_task
def scrape_hosting_plans_task():
    """Main task to scrape all providers in parallel using Celery Chord."""
    providers = [
        ("Babal Host", "https://babal.host/"),
        ("WebHost Nepal", "https://www.webhostnepal.com/hosting"),
        ("Himalayan Host", "https://www.himalayanhost.com/store/web-hosting-nepal"),
        ("Siteground Host", "https://world.siteground.com/web-hosting.htm"),
    ]

    start_time = datetime.now()
    SCRAPE_TIMINGS["start"] = start_time
    logger.info(f"🚀 Starting parallel scraping at {start_time}...")

    try:
        # Execute subtasks in parallel and process results after completion
        job = chord(
            (scrape_single_provider_task.s(provider, url) for provider, url in providers)
        )(process_scraped_results.s())

        logger.info("📌 Chord created successfully. Tasks dispatched!")
        return job.id  # Return task ID for monitoring

    except Exception as e:
        logger.error(f"❌ Error starting scraping: {e}")
        raise e


@shared_task
def scrape_single_provider_task(provider_name, url):
    """Scrape a single hosting provider."""
    start_time = datetime.now()
    logger.info(f"⏳ [{provider_name}] Scraping started at: {start_time}")

    try:
        scraped_data = scrape_host_plans(provider_name, url)
    except Exception as e:
        logger.error(f"❌ Error scraping {provider_name}: {e}")
        scraped_data = []

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info(f"✅ [{provider_name}] Finished at {end_time} ({duration:.2f} sec)")
    return scraped_data


@shared_task
def process_scraped_results(results):
    """Callback to process results after parallel scraping."""
    logger.info(f"📦 Received {len(results)} scraping results. Saving data...")

    # Save data from all providers
    for provider_data in results:
        save_scraped_data(provider_data)

    # Calculate total duration
    end_time = datetime.now()
    start_time = SCRAPE_TIMINGS.get("start", end_time)
    total_duration = (end_time - start_time).total_seconds()

    logger.info(f"✅ All scraped data saved successfully!")
    logger.info(f"⏱️ TOTAL SCRAPING TIME: {total_duration:.2f} seconds")

    return {
        "status": "success",
        "providers": len(results),
        "duration": total_duration,
    }
