from django.shortcuts import render
from django.http import JsonResponse
import requests

API_KEY = '579b464db66ec23bdd0000019ecc0f38a3ba40c87b425aad8495528e'
RESOURCE_ID = '9ef84268-d588-465a-a308-a864a43d0070'
DEFAULT_STATE = "Maharashtra"

def agricultural_commodities(request):
    # Just render the page, no data sent initially
    return render(request, "commodities/commodities.html")

def fetch_commodity_data(request):
    state = request.GET.get("state")
    commodity = request.GET.get("commodity")
    market = request.GET.get("market")
    limit = request.GET.get("limit", 20)

    if not state:
        return JsonResponse({"error": "State is required."}, status=400)

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[state]": state,
        "limit": limit
    }
    if commodity:
        params["filters[commodity]"] = commodity
    if market:
        params["filters[market]"] = market

    url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        commodities = [
            {
                "state": item.get("state"),
                "market": item.get("market"),
                "commodity": item.get("commodity"),
                "min_price": item.get("min_price"),
                "max_price": item.get("max_price"),
                "modal_price": item.get("modal_price"),
                "date": item.get("arrival_date") or item.get("date")
            }
            for item in data.get("records", [])
        ]
        return JsonResponse({"commodities": commodities})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Failed to fetch data from API.", "details": str(e)}, status=500)
    


