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
# import requests
# from bs4 import BeautifulSoup

# url = "https://schemes.vikaspedia.in/viewcontent/schemesall/schemes-for-farmers?lgn=en"
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')

# schemes = []
# for item in soup.select('.portal-title a'):
#     title = item.get_text(strip=True)
#     link = item['href']
#     schemes.append({'title': title, 'url': link})

# print(schemes)

# import requests
# from bs4 import BeautifulSoup

# url = "https://schemes.vikaspedia.in/viewcontent/schemesall/schemes-for-farmers?lgn=en"
# headers = {"User-Agent": "Mozilla/5.0"}

# response = requests.get(url, headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')

# for link in soup.select('.portal-title a'):
#     title = link.get_text(strip=True)
#     href = link.get('href')
#     full_link = f"https://schemes.vikaspedia.in{href}"
#     print(f"{title} - {full_link}")

# import requests
# import json
 
 
# url = "https://data.vikaspedia.in/api/public/content/page-content?ctx=/schemesall/schemes-for-farmers&lgn=en"
 
 
# try:
#     response = requests.get(url)
#     response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
 
 
#     data = response.json()
 
 
#     # Print the formatted JSON data
#     print(json.dumps(data, indent=4))
 
 
#     # Example: Accessing the scheme name
 
 
# except requests.exceptions.RequestException as e:
#     print(f"Request failed: {e}")
# except json.JSONDecodeError as e:
#     print(f"JSON decoding failed: {e}")

import requests,json
 
API_KEY = '579b464db66ec23bdd0000019ecc0f38a3ba40c87b425aad8495528e'
RESOURCE_ID = '1467e3cc-6804-4664-85e0-4424b56fcba5'
params = {
        "api-key": API_KEY,
        "format": "json",
       
        "limit": 500,
    }

url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
response = requests.get(url, params=params)
data = response.json()
print(data)
