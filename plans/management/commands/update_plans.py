from django.core.management.base import BaseCommand
from plans.models import HostingPlan
from plans.scrapers import scrape_all_providers  # Your central scraper function
import types

class Command(BaseCommand):
    help = 'Scrapes all hosting provider websites and updates the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the scraping process...")

        all_scraped_plans = scrape_all_providers()

        if not all_scraped_plans:
            self.stdout.write(self.style.WARNING("No data was scraped. Check scraper functions."))
            return

        updated_count = 0
        created_count = 0

        # Helper function to safely extract plan data
        def get_plan_data(plan):
            if isinstance(plan, dict):
                return {
                    "provider_name": plan.get("provider_name", ""),
                    "plan_name": plan.get("plan_name", ""),
                    "price": plan.get("price", ""),
                    "hosting_type": plan.get("hosting_type", ""),
                    "storage": plan.get("storage", ""),
                    "bandwidth": plan.get("bandwidth", ""),
                    "url": plan.get("url", ""),
                }
            elif isinstance(plan, types.SimpleNamespace):
                return {
                    "provider_name": getattr(plan, "provider_name", ""),
                    "plan_name": getattr(plan, "plan_name", ""),
                    "price": getattr(plan, "price", ""),
                    "hosting_type": getattr(plan, "hosting_type", ""),
                    "storage": getattr(plan, "storage", ""),
                    "bandwidth": getattr(plan, "bandwidth", ""),
                    "url": getattr(plan, "url", ""),
                }
            else:
                return None  # Unknown type

        # Case 1: If it returns a dict
        if isinstance(all_scraped_plans, dict):
            for provider, plans in all_scraped_plans.items():
                for plan in plans:
                    data = get_plan_data(plan)
                    if not data:
                        continue  # skip unknown plan types
                    obj, created = HostingPlan.objects.update_or_create(
                        provider_name=data["provider_name"],
                        plan_name=data["plan_name"],
                        defaults={
                            "price": data["price"],
                            "hosting_type": data["hosting_type"],
                            "storage": data["storage"] or "unknown",
                            "bandwidth": data["bandwidth"],
                            "url": data["url"]
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

        # Case 2: If it returns a list
        elif isinstance(all_scraped_plans, list):
            for plan in all_scraped_plans:
                data = get_plan_data(plan)
                if not data:
                    continue  # skip unknown plan types
                obj, created = HostingPlan.objects.update_or_create(
                    provider_name=data["provider_name"],
                    plan_name=data["plan_name"],
                    defaults={
                        "price": data["price"],
                        "hosting_type": data["hosting_type"],
                        "storage": data["storage"] or "unknown",
                        "bandwidth": data["bandwidth"],
                        "url": data["url"]
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Scraping complete! Created: {created_count}, Updated: {updated_count}. ✅"
        ))
