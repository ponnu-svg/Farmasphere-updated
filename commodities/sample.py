# from django.shortcuts import render
# from django.http import JsonResponse
# import requests


# API_KEY = '579b464db66ec23bdd0000019ecc0f38a3ba40c87b425aad8495528e'
# RESOURCE_ID = '8b68ae56-84cf-4728-a0a6-1be11028dea7'

# params = {
#         "api-key": API_KEY,
#         "format": "json",
#         "limit": 500,
#     }
# url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

# response = requests.get(url, params=params)
# print(response.json())
import requests
from bs4 import BeautifulSoup

url = "https://schemes.vikaspedia.in/viewcontent/schemesall/schemes-for-farmers?lgn=en"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

schemes = []
for item in soup.select('.portal-title a'):
    title = item.get_text(strip=True)
    link = item['href']
    schemes.append({'title': title, 'url': link})

print(schemes)
