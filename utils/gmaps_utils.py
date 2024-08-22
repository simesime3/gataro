import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=API_KEY) if API_KEY else None

def find_restaurants(locations):
    avg_lat = sum(location['lat'] for location in locations) / len(locations)
    avg_lng = sum(location['lng'] for location in locations) / len(locations)

    places_result = gmaps.places_nearby(
        location=(avg_lat, avg_lng), radius=1000, type='restaurant', open_now=True
    )
    return places_result
