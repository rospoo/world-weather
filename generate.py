import json
import os
import glob
import requests

API_KEY = os.environ['OPENWEATHERMAP_API_KEY']
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'

# Lingue supportate (puoi modificarle)
LANGUAGES = ['it', 'en', 'fr', 'de', 'es', 'pt', 'ru', 'zh', 'ja', 'ar',
             'hi', 'bn', 'ko', 'tr', 'pl', 'nl', 'sv', 'no', 'da', 'fi']

# Traduzioni delle etichette fisse
TRANS = {
    'it': {'max': 'Temp. Max', 'min': 'Temp. Min', 'day': 'Giorno', 'title': 'Previsioni per'},
    'en': {'max': 'Max Temp', 'min': 'Min Temp', 'day': 'Day', 'title': 'Forecast for'},
    'fr': {'max': 'Temp. Max', 'min': 'Temp. Min', 'day': 'Jour', 'title': 'Prévisions pour'},
    'de': {'max': 'Max. Temp.', 'min': 'Min. Temp.', 'day': 'Tag', 'title': 'Vorhersage für'},
    'es': {'max': 'Temp. Máx.', 'min': 'Temp. Mín.', 'day': 'Día', 'title': 'Pronóstico para'},
    'pt': {'max': 'Temp. Máx.', 'min': 'Temp. Mín.', 'day': 'Dia', 'title': 'Previsão para'},
    'ru': {'max': 'Макс. темп.', 'min': 'Мин. темп.', 'day': 'День', 'title': 'Прогноз для'},
    'zh': {'max': '最高温度', 'min': '最低温度', 'day': '天', 'title': '天气预报'},
    'ja': {'max': '最高気温', 'min': '最低気温', 'day': '日', 'title': 'の天気予報'},
    'ar': {'max': 'درجة الحرار العظمى', 'min': 'درجة الحرار الصغرى', 'day': 'اليوم', 'title': 'توقعات لـ'},
    'hi': {'max': 'अधिकतम ताप', 'min': 'न्यूनतम ताप', 'day': 'दिन', 'title': 'के लिए पूर्वानुमान'},
    'bn': {'max': 'সর্বোচ্চ তাপ', 'min': 'সর্বনিম্ন তাপ', 'day': 'দিন', 'title': 'জন্য পূর্বাভাস'},
    'ko': {'max': '최고 기온', 'min': '최저 기온', 'day': '일', 'title': '에 대한 일기 예보'},
    'tr': {'max': 'Maks. Sıc.', 'min': 'Min. Sıc.', 'day': 'Gün', 'title': 'Hava Durumu'},
    'pl': {'max': 'Temp. Maks.', 'min': 'Temp. Min.', 'day': 'Dzień', 'title': 'Prognoza dla'},
    'nl': {'max': 'Max. Temp.', 'min': 'Min. Temp.', 'day': 'Dag', 'title': 'Weer voor'},
    'sv': {'max': 'Max. Temp.', 'min': 'Min. Temp.', 'day': 'Dag', 'title': 'Prognos för'},
    'no': {'max': 'Maks. Temp.', 'min': 'Min. Temp.', 'day': 'Dag', 'title': 'Værvarsel for'},
    'da': {'max': 'Maks. Temp.', 'min': 'Min. Temp.', 'day': 'Dag', 'title': 'Vejrudsigt for'},
    'fi': {'max': 'Maks. Lämpötila', 'min': 'Min. Lämpötila', 'day': 'Päivä', 'title': 'Ennuste kohteelle'}
}

# Carica città
with open('cities.json', 'r', encoding='utf-8') as f:
    cities = json.load(f)
print(f"Città caricate: {len(cities)}")

# Dizionario per i dati della homepage (meteo "corrente" ricavato dall'ultimo forecast)
home_weather = {}

for lang in LANGUAGES:
    print(f"\nGenerazione lingua: {lang}")
    # Pulisce i vecchi file
    for f in glob.glob(f'content/{lang}/cities/*.md'):
        os.remove(f)
    os.makedirs(f'content/{lang}/cities', exist_ok=True)

    homepage = [f'---\ntitle: "World Weather - {lang.upper()}"\n---\n\n## {TRANS[lang]["title"]} le città\n']
    homepage_links = []

    for city in cities:
        params = {
            'lat': city['lat'],
            'lon': city['lon'],
            'appid': API_KEY,
            'units': 'metric',
            'lang': lang,
            'cnt': 40
        }
        r = requests.get(BASE_URL, params=params)
        data = r.json()
        if data.get('cod') != '200':
            print(f"  Errore per {city['name']}: {data.get('message', '')}")
            continue

        # Raggruppa previsioni per giorno
        days = {}
        for entry in data['list']:
            date = entry['dt_txt'].split(' ')[0]
            if date not in days:
                days[date] = {'temps': [], 'icons': [], 'descriptions': []}
            days[date]['temps'].append(entry['main']['temp'])
            days[date]['icons'].append(entry['weather'][0]['icon'])
            days[date]['descriptions'].append(entry['weather'][0]['description'])

        # Dati "correnti" dal primo slot (il più vicino all'ora attuale)
        first_entry = data['list'][0]
        current_temp = round(first_entry['main']['temp'])
        current_icon = first_entry['weather'][0]['icon']
        current_desc = first_entry['weather'][0]['description']
        # Salva per la homepage (solo una volta, in inglese o neutro)
        if city['name'] not in home_weather:
            home_weather[city['name']] = {
                'temp': current_temp,
                'icon': current_icon,
                'description': current_desc,
                'country': city.get('country', ''),
                'country_code': city.get('country_code', '').upper()
            }

        # Slug per il file
        slug = city['name'].lower().replace(' ', '-').replace("'", "")
        t = TRANS[lang]
        md = f'---\ntitle: "{t["title"]} {city["name"]}"\noriginal_name: "{city["name"]}"\ncountry: "{city.get("country", "")}"\ncountry_code: "{city.get("country_code", "").upper()}"\n---\n\n'
        md += f'## {t["title"]} {city["name"]}\n\n'
        md += f'| {t["day"]} | {t["max"]} | {t["min"]} | Icona | Descrizione |\n'
        md += '|--------|-----------|-----------|-------|-------------|\n'

        for date, vals in days.items():
            max_temp = max(vals['temps'])
            min_temp = min(vals['temps'])
            icon = max(set(vals['icons']), key=vals['icons'].count)
            desc = max(set(vals['descriptions']), key=vals['descriptions'].count)
            icon_url = f'https://openweathermap.org/img/wn/{icon}@2x.png'
            md += f'| {date} | {max_temp:.1f}°C | {min_temp:.1f}°C | ![icona]({icon_url}) | {desc} |\n'

        with open(f'content/{lang}/cities/{slug}.md', 'w', encoding='utf-8') as f:
            f.write(md)

        homepage_links.append(f'- [{city["name"]}](/cities/{slug}/)')

    homepage.append('\n'.join(homepage_links))
    with open(f'content/{lang}/_index.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(homepage))

# Salva data/home_weather.json per la homepage
os.makedirs('data', exist_ok=True)
with open('data/home_weather.json', 'w', encoding='utf-8') as f:
    json.dump(home_weather, f, ensure_ascii=False, indent=2)

print(f"\nHomepage data generata per {len(home_weather)} città.\nFatto!")