import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hosting_project.settings")
django.setup()
from plans.models import HostingPlan

data = [
    {"provider_name": "Babal Host", "plan_name": "Starter", "hosting_type": "Shared", "price": "NPR 299/mo", "storage": "10GB", "bandwidth": "500GB", "api_available": True, "notes": "Local Nepali hosting", "url": "https://babal.host/"},

    {"provider_name": "Himalayan Host ", "plan_name": "Economy", "hosting_type": "Shared", "price": "NPR 299/mo", "storage": "15GB", "bandwidth": "500GB", "api_available": False, "notes": "Good for beginners", "url": "https://www.himalayanhost.com/store/web-hosting-nepal"},

    # {"provider_name": "WebHost Nepal", "plan_name": "Basic", "hosting_type": "Shared", "price": "NPR 399/mo", "storage": "20GB", "bandwidth": "1TB", "api_available": True, "notes": "Affordable for small websites", "url": "https://www.webhostnepal.com/hosting"},

    # {"provider_name": "NepaliHost", "plan_name": "Standard", "hosting_type": "VPS", "price": "NPR 599/mo", "storage": "50GB", "bandwidth": "2TB", "api_available": True, "notes": "VPS hosting in Nepal", "url": "https://iwebnepal.com.np/iweb-design/web-hosting/"},


    # {"provider_name": "Hostinger", "plan_name": "Premium", "hosting_type": "Shared", "price": "$2.99/mo", "storage": "100GB", "bandwidth": "Unlimited", "api_available": True, "notes": "Good for small websites", "url": "https://www.hostinger.com/pricing"},
    
    # {"provider_name": "Bluehost", "plan_name": "Basic", "hosting_type": "Shared", "price": "$3.95/mo", "storage": "50GB", "bandwidth": "Unmetered", "api_available": True, "notes": "Good for WordPress", "url": "https://www.bluehost.com/hosting/shared"},

    # {"provider_name": "SiteGround", "plan_name": "StartUp", "hosting_type": "Shared", "price": "$3.99/mo", "storage": "10GB", "bandwidth": "10,000 visits/mo", "api_available": True, "notes": "", "url": "https://world.siteground.com/web-hosting.htm"},

    # {"provider_name": "GoDaddy", "plan_name": "Economy", "hosting_type": "Shared", "price": "$5.99/mo", "storage": "100GB", "bandwidth": "Unmetered", "api_available": False, "notes": "", "url": "https://www.godaddy.com/en-ph/offers/hosting"},

    # {"provider_name": "DigitalOcean", "plan_name": "Basic", "hosting_type": "VPS", "price": "$5/mo", "storage": "25GB", "bandwidth": "1TB", "api_available": True, "notes": "Cloud server", "url": "https://www.digitalocean.com/pricing"},

    # {"provider_name": "AWS", "plan_name": "Free Tier EC2", "hosting_type": "Cloud", "price": "Free", "storage": "30GB", "bandwidth": "1GB", "api_available": True, "notes": "Scalable cloud", "url": "https://aws.amazon.com/ec2/pricing/"},

    # {"provider_name": "GCP", "plan_name": "f1-micro", "hosting_type": "Cloud", "price": "Free", "storage": "30GB", "bandwidth": "1GB", "api_available": True, "notes": "", "url": "https://cloud.google.com/pricing"},

    # {"provider_name": "Namecheap", "plan_name": "Stellar", "hosting_type": "Shared", "price": "$1.58/mo", "storage": "20GB", "bandwidth": "Unmetered", "api_available": False, "notes": "", "url": "https://www.namecheap.com/hosting/"},

    # {"provider_name": "Vultr", "plan_name": "Cloud Compute", "hosting_type": "VPS", "price": "$5/mo", "storage": "25GB", "bandwidth": "1TB", "api_available": True, "notes": "", "url": "https://www.vultr.com/pricing/"},

    # {"provider_name": "InMotion", "plan_name": "Hosting Launch", "hosting_type": "Shared", "price": "$2.49/mo", "storage": "50GB", "bandwidth": "Unlimited", "api_available": False, "notes": "Good for small to medium websites", "url": "https://www.inmotionhosting.com/vps-hosting"},

    # {"provider_name": "Liquid Web", "plan_name": "Managed VPS", "hosting_type": "VPS", "price": "$29/mo", "storage": "100GB", "bandwidth": "5TB", "api_available": True, "notes": "High-performance VPS for business", "url": "https://www.liquidweb.com/dedicated-server-hosting/"},
    
    # {"provider_name": "Kinsta", "plan_name": "Starter", "hosting_type": "Managed WordPress", "price": "$35/mo", "storage": "10GB", "bandwidth": "50GB", "api_available": True, "notes": "Premium WordPress hosting", "url": "https://kinsta.com/pricing/"},

]

for item in data:
    HostingPlan.objects.create(**item)


print("Data imported successfully........")
