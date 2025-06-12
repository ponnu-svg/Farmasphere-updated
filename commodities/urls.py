from django.urls import path
from . import views

urlpatterns = [
    path('commodities/', views.agricultural_commodities, name='commodities'),
    path('fetch-commodity-data/', views.fetch_commodity_data, name='fetch_commodity_data'),
    
]
