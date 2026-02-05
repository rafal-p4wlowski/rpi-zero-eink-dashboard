#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time
import locale
import requests
import common
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# 1. KONFIGURACJA
# ==============================================================================
ROTATE_DISPLAY = True
FULL_REFRESH_HOURS = 6
WEATHER_INTERVAL_MIN = 30
WEATHER_LAT = 52.2297
WEATHER_LON = 21.0122

try:
    locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')
except locale.Error:
    print("System: Brak locale 'pl_PL.UTF-8', używam domyślnego.")

WEATHER_DESC = {
    0: "Bezchmurnie", 1: "Lekkie zachm.", 2: "Czesciowe zachm.", 3: "Pochmurno",
    45: "Mgla", 48: "Szadz", 51: "Lekka mzawka", 53: "Mzawka", 55: "Gestwa mzawka",
    61: "Slaby deszcz", 63: "Deszcz", 65: "Ulewa", 71: "Slaby snieg", 73: "Snieg",
    75: "Sniezyca", 80: "Przelotny deszcz", 95: "Burza", 96: "Burza z gradem"
}

# ==============================================================================
# 2. FUNKCJE
# ==============================================================================
def fetch_weather():
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={WEATHER_LAT}"
           f"&longitude={WEATHER_LON}&current=temperature_2m,weather_code"
           f"&timezone=auto&models=ecmwf_ifs025")
    
    for attempt in range(1, 4):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data['current'].get('temperature_2m', '--')
                code = data['current'].get('weather_code', -1)
                desc = WEATHER_DESC.get(code, "Nieznana")
                # --- LOGOWANIE IDENTYCZNE JAK W DRUGIM PLIKU ---
                print(f"Pogoda: Pobrano ({temp}°C, {desc})")
                return f"{temp:.1f}°C", desc
        except Exception:
            time.sleep(2)
    print("Pogoda: Błąd pobierania.")
    return "--.-°C", "Błąd sieci"

def get_fonts():
    try:
        return {
            'time': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 55),
            'date': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22),
            'temp': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22),
            'desc': ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
        }
    except IOError:
        d = ImageFont.load_default()
        return {'time': d, 'date': d, 'temp': d, 'desc': d}

# ==============================================================================
# 3. MAIN
# ==============================================================================
def main():
    epd_driver = common.get_epd_driver()
    epd = epd_driver.EPD()
    fonts = get_fonts()
    
    weather_cache = ("--.-°C", "Start...")
    last_weather_time = 0
    last_full_refresh_hour = -1

    try:
        common.init_display(epd)
        
        base_image = Image.new('1', (epd.height, epd.width), 255)
        if ROTATE_DISPLAY: base_image = base_image.rotate(180)
        epd.displayPartBaseImage(epd.getbuffer(base_image))

        while True:
            now = datetime.now()
            
            # Pogoda
            if time.time() - last_weather_time > (WEATHER_INTERVAL_MIN * 60):
                weather_cache = fetch_weather()
                last_weather_time = time.time()
            
            temp_str, desc_str = weather_cache

            # Rysowanie
            image = Image.new('1', (epd.height, epd.width), 255)
            draw = ImageDraw.Draw(image)
            
            draw.rectangle((0, 0, epd.height-1, epd.width-1), outline=0)
            draw.text((5, 2), now.strftime("%d %B"), font=fonts['date'], fill=0)
            
            bbox = draw.textbbox((0,0), temp_str, font=fonts['temp'])
            draw.text((epd.height - (bbox[2]-bbox[0]) - 5, 2), temp_str, font=fonts['temp'], fill=0)
            draw.line((0, 28, epd.height-1, 28), fill=0)

            time_str = now.strftime("%H:%M")
            bbox = draw.textbbox((0,0), time_str, font=fonts['time'])
            time_x = (epd.height - (bbox[2]-bbox[0])) // 2
            draw.text((time_x, 30), time_str, font=fonts['time'], fill=0)

            desc_y = epd.width - 25
            draw.line((0, desc_y, epd.height-1, desc_y), fill=0)
            
            bbox = draw.textbbox((0,0), desc_str, font=fonts['desc'])
            desc_x = (epd.height - (bbox[2]-bbox[0])) // 2
            draw.text((desc_x, desc_y + 2), desc_str, font=fonts['desc'], fill=0)

            if ROTATE_DISPLAY: image = image.rotate(180)

            if now.hour % FULL_REFRESH_HOURS == 0 and now.hour != last_full_refresh_hour:
                print(f"System: Pełne czyszczenie ekranu...")
                epd.init()
                epd.display(epd.getbuffer(image))
                epd.init()
                epd.displayPartBaseImage(epd.getbuffer(image))
                last_full_refresh_hour = now.hour
            else:
                epd.displayPartial(epd.getbuffer(image))
                # --- LOGOWANIE STANU ---
                print(f"Zegar: {time_str}")

            time.sleep(60 - datetime.now().second + 0.1)

    except KeyboardInterrupt:
        print("\nWyjście: Przerwano przez użytkownika.")
    finally:
        print("System: Usypianie...")
        epd.init()
        epd.sleep()

if __name__ == "__main__":
    main()