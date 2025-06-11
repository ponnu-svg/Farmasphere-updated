from django.urls import path
from . import views

app_name = 'commodities'

urlpatterns = [
    path('commodities/', views.agricultural_commodities, name='home'),
    path('fetch-filters/', views.fetch_filters, name='fetch_filters'),
    path('fetch-commodity-data/', views.fetch_commodity_data, name='fetch_commodity_data'),
    path("schemes/", views.farmer_schemes_view, name="farmer_schemes"),
]
