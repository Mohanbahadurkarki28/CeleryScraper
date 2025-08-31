from django.contrib import admin
from .models import HostingPlan

@admin.register(HostingPlan)
class HostingPlanAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'plan_name', 'hosting_type', 'price', 'storage', 'bandwidth', 'api_available')
    list_filter = ('provider_name', 'hosting_type', 'api_available')
    search_fields = ('provider_name', 'plan_name')
