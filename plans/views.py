import json
import re
from datetime import timedelta
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.http import JsonResponse
from collections import defaultdict
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import HostingPlan, HostingPlanSnapshot
from .tasks import scrape_hosting_plans_task


def home(request):
    query = request.GET.get("q", "").strip()

    # Prevent abuse by limiting query length
    if len(query) > 100:
        query = query[:100]

    # Allow only safe characters
    if not re.match(r'^[\w\s-]*$', query):
        query = ""

    # Fetch hosting plans
    plans = HostingPlan.objects.all()

    # If there's a search query, filter plans
    if query:
        plans = plans.filter(
            plan_name__icontains=query
        ) | plans.filter(
            provider_name__icontains=query
        )

    # Group plans by provider
    providers = defaultdict(list)
    for plan in plans:
        providers[plan.provider_name].append(plan)

    return render(request, "plans/home.html", {
        "providers": dict(providers),
        "query": query,
    })


def provider_detail(request, pk):
    plan = get_object_or_404(HostingPlan, pk=pk)
    return render(request, "plans/provider_detail.html", {"plan": plan})


def provider_price_chart(request, pk):
    """
    Renders the price history chart page.
    """
    plan = get_object_or_404(HostingPlan, pk=pk)
    return render(request, "plans/provider_price_chart.html", {"plan": plan})



def run_scraper(request):
    scrape_hosting_plans_task.delay()
    return JsonResponse({"status": "started", "message": "Scraper task has been triggered!"})


def plan_details(request, plan_id, index):
    plan = get_object_or_404(HostingPlan, id=plan_id)
    snapshots = plan.snapshots.all().order_by("created_at")

    try:
        snapshot = snapshots[index]
    except IndexError:
        return render(request, "plans/plan_detail_view.html", {
            "plan": plan,
            "error": "Invalid snapshot index."
        })

    context = {
        "plan": plan,
        "date": snapshot.created_at.strftime("%Y-%m-%d %H:%M"),
        "price": snapshot.price,
        "pkg": plan.plan_name,
        "features": f"Type: {plan.hosting_type}, Storage: {plan.storage}, Bandwidth: {plan.bandwidth}, API: {'Yes' if plan.api_available else 'No'}",
    }
    return render(request, "plans/plan_detail_view.html", context)


import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta
from plans.models import HostingPlan, HostingPlanSnapshot

# views.py
def price_history(request, plan_id):
    import re
    from django.utils.timezone import now, timedelta
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    from .models import HostingPlan, HostingPlanSnapshot

    plan = get_object_or_404(HostingPlan, id=plan_id)
    date_range = request.GET.get("range", "30d")
    snapshots = HostingPlanSnapshot.objects.filter(hosting_plan=plan).order_by("created_at")

    # Filter by date range
    if date_range == "7d":
        snapshots = snapshots.filter(created_at__gte=now() - timedelta(days=7))
    elif date_range == "30d":
        snapshots = snapshots.filter(created_at__gte=now() - timedelta(days=30))

    data = []
    for s in snapshots:
        # Clean price
        clean_price = re.sub(r"[^\d.]", "", str(s.price))
        try:
            price_value = float(clean_price)
        except ValueError:
            price_value = 0

        data.append({
            "id": s.id,  # ✅ Added snapshot ID here
            "created_at": s.created_at.strftime("%Y-%m-%d"),
            "price": price_value
        })

    return JsonResponse(data, safe=False)


from django.shortcuts import render, get_object_or_404
from .models import HostingPlanSnapshot

# views.py
from django.shortcuts import get_object_or_404, render
from .models import HostingPlanSnapshot

def snapshot_detail(request, snapshot_id):
    snapshot = get_object_or_404(HostingPlanSnapshot, id=snapshot_id)
    return render(request, "plans/snapshot_detail.html", {"snapshot": snapshot})
