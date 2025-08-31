from django.core.management.base import BaseCommand
from plans.models import HostingPlan
from plans.scrapers import scrape_all_providers # Import from your new scrapers file

class Command(BaseCommand):
    help = 'Scrapes all hosting provider websites and updates the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the scraping process...")

        # Get all scraped data from your central function
        all_scraped_data = scrape_all_providers()

        if not all_scraped_data:
            self.stdout.write(self.style.WARNING("No data was scraped. Check scraper functions."))
            return
        
        updated_count = 0
        created_count = 0

        # Loop through data and update the database
        for item in all_scraped_data:
            obj, created = HostingPlan.objects.update_or_create(
                provider_name=item.get("provider_name"),
                plan_name=item.get("plan_name"),
                defaults=item  
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Scraping complete! Created: {created_count}, Updated: {updated_count}. ✅"
        ))