import requests, json

USER = "il_tuo_username_geonames"   # registrati gratis su geonames.org
url = f"http://api.geonames.org/citiesJSON?north=90&south=-90&east=180&west=-180&maxRows=1000&username={USER}"
r = requests.get(url)
data = r.json()

cities = []
for g in data['geonames']:
    cities.append({
        "name": g['name'],
        "lat": float(g['lat']),
        "lon": float(g['lng']),
        "country": g.get('countryName', ''),
        "country_code": g.get('countrycode', '')
    })

with open('cities.json', 'w', encoding='utf-8') as f:
    json.dump(cities, f, indent=2, ensure_ascii=False)

print(f"Salvate {len(cities)} città con paese.")