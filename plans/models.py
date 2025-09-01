from django.db import models


class HostingPlan(models.Model):
    provider_name = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=100)
    hosting_type = models.CharField(max_length=50)
    price = models.CharField(max_length=10, null=True, blank=True)    
    storage = models.CharField(max_length=50)
    bandwidth = models.CharField(max_length=50)
    api_available = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=200, null=True)

    def __str__(self):
        return f"{self.provider_name} - {self.plan_name}"


class HostingPlanSnapshot(models.Model):
    hosting_plan = models.ForeignKey('HostingPlan', on_delete=models.CASCADE)
    price = models.CharField(max_length=10, null=True, blank=True )
    created_at = models.DateTimeField(auto_now_add=True) 
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.hosting_plan.provider_name} - {self.hosting_plan.plan_name} @ {self.price} ({self.created_at})"
