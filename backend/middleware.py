# your_app/middleware.py
import requests
from django.http import HttpResponseForbidden

class UserLocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user's IP address
        ip = self.get_client_ip(request)
        
        # Get user's location (country, city, latitude, and longitude)
        country, city, latitude, longitude = self.get_geo_from_ip(ip)
        
        # Block users from Nigeria
        if country == 'NG':  # 'NG' is the ISO country code for Nigeria
            return HttpResponseForbidden('Site not available in your region' )
        
        # Store the location in the request
        request.user_location = {
            'ip': ip,
            'country': country,
            'city': city,
            'latitude': latitude,
            'longitude': longitude,
        }
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_geo_from_ip(self, ip):
        try:
            # Using ipinfo.io API to get location
            response = requests.get(f"https://ipinfo.io/{ip}/geo", timeout=5)
            data = response.json()
            
            country = data.get('country', '')  # Get the country
            city = data.get('city', '')        # Get the city
            location = data.get('loc', '')     # loc is a string like "latitude,longitude"
            if location:
                latitude, longitude = location.split(',')
                return country, city, float(latitude), float(longitude)
        except requests.RequestException:
            pass
        return None, None, None, None
