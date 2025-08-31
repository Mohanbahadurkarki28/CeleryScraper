import json
from django.shortcuts import get_object_or_404, render
from .models import HostingPlan, HostingPlanSnapshot
import re

def home(request):
    query = request.GET.get("q", "").strip()

    # limit length to prevent abuse
    if len(query) > 100:
        query = query[:100]

    # optional: only allow alphanumeric + spaces
    if not re.match(r'^[\w\s-]*$', query):  
        query = ""

    plans = HostingPlan.objects.all()

    if query:
        plans = plans.filter(
            plan_name__icontains=query
        ) | plans.filter(
            provider_name__icontains=query
        )

    return render(request, "plans/home.html", {
        "plans": plans,
        "query": query
    })



def provider_detail(request, pk):
    plan = get_object_or_404(HostingPlan, pk=pk)
    return render(request, "plans/provider_detail.html", {"plan": plan})


def provider_weekly_chart(request, pk):
    plan = get_object_or_404(HostingPlan, pk=pk)
    snapshots = HostingPlanSnapshot.objects.filter(
        hosting_plan=plan
    ).order_by("created_at")

    # Extract prices safely
    prices, dates = [], []
    for snap in snapshots:
        cleaned = re.sub(r"[^\d.]", "", snap.price or "")
        try:
            prices.append(float(cleaned) if cleaned else 0)
        except ValueError:
            prices.append(0)
        dates.append(snap.created_at.strftime("%Y-%m-%d %H:%M"))

    chart_data_json = json.dumps({
        "labels": dates,
        "prices": prices,
    })

    return render(request, "plans/provider_weekly_chart.html", {
        "plan": plan,
        "chart_data_json": chart_data_json,
    })

from django.http import JsonResponse
from .tasks import scrape_hosting_plans_task

def run_scraper(request):
    scrape_hosting_plans_task.delay() 
    return JsonResponse({"status": "started", "message": "Scraper task has been triggered!"})