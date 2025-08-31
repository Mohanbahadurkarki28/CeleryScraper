from celery import shared_task
from .scrapers import scrape_all_providers
import logging

logger = logging.getLogger(__name__)

@shared_task
def scrape_hosting_plans_task():
    logger.info("Starting hosting plans scrape via Celery...")
    try:
        all_plans = scrape_all_providers()
        logger.info(f"Scraped {len(all_plans)} plans successfully.")
    except Exception as e:
        logger.error(f"Error scraping hosting plans: {e}")
