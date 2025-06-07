from django.shortcuts import render
from django.http import JsonResponse
import requests

API_KEY = '579b464db66ec23bdd0000019ecc0f38a3ba40c87b425aad8495528e'
RESOURCE_ID = '9ef84268-d588-465a-a308-a864a43d0070'

def agricultural_commodities(request):
    return render(request, "commodities/commodities.html")

def fetch_filters(request):
    """
    Return unique commodities and markets for a given state.
    """
    state = request.GET.get("state")
    if not state:
        return JsonResponse({"error": "State is required."}, status=400)

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[state]": state,
        "limit": 500,
    }

    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        records = data.get("records", [])

        commodities = sorted(set(r.get("commodity") for r in records if r.get("commodity")))
        markets = sorted(set(r.get("market") for r in records if r.get("market")))

        # Also extract unique dates (arrival_date) if you want to show date picker options
        dates = sorted(set(r.get("arrival_date") for r in records if r.get("arrival_date")))

        return JsonResponse({
            "commodities": commodities,
            "markets": markets,
            "dates": dates
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch data from API.", "details": str(e)}, status=500)


def fetch_commodity_data(request):
    state = request.GET.get("state")
    date = request.GET.get("date")
    commodity = request.GET.get("commodity")
    market = request.GET.get("market")
    limit = request.GET.get("limit", 100)

    if not state:
        return JsonResponse({"error": "State is required."}, status=400)

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[state]": state,
        "limit": limit
    }

    # Only add filters if they are provided (non-empty)
    if commodity:
        params["filters[commodity]"] = commodity
    if market:
        params["filters[market]"] = market

    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        records = data.get("records", [])

        # Filter by date if provided
        if date:
            records = [r for r in records if r.get("arrival_date") == date]

        # Extract unique commodities and markets from the filtered records
        commodities = sorted(set(r.get("commodity") for r in records if r.get("commodity")))
        markets = sorted(set(r.get("market") for r in records if r.get("market")))

        return JsonResponse({
            "records": records,
            "commodities": commodities,
            "markets": markets
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch data from API.", "details": str(e)}, status=500)