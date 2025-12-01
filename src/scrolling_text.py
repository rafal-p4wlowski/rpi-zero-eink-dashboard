#!/usr/bin/python3
# -*- coding:utf-8 -*-

import time
import common # Import wspólny
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# 1. KONFIGURACJA UŻYTKOWNIKA
# ==============================================================================
ROTATE_DISPLAY = True
SCROLL_TEXT = " To jest przykładowy tekst przewijany na ekranie e-ink. "  # Dodaj spacje na końcach dla odstępu
FONT_SIZE = 90          # Rozmiar czcionki
SCROLL_STEP = 25        # Szybkość (piksele na klatkę) - im więcej tym szybciej
REFRESH_SEC = 120       # Pełne czyszczenie co 120 sekund (usuwanie duchów)

# ==============================================================================
# 2. GŁÓWNA PĘTLA PROGRAMU
# ==============================================================================
def main():
    # Inicjalizacja sterownika z common
    epd_driver = common.get_epd_driver()
    epd = epd_driver.EPD()
    
    try:
        # Ładowanie czcionki
        try:
            # Używamy pogrubionej, żeby tekst był wyraźniejszy przy ruchu
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', FONT_SIZE)
        except:
            font = ImageFont.load_default()

        common.init_display(epd)

        # Wymiary logiczne (dla V4 width to height fizyczny)
        dw, dh = epd.height, epd.width
        
        # Obliczanie wymiarów tekstu
        dummy = ImageDraw.Draw(Image.new('1', (1,1)))
        bbox = dummy.textbbox((0,0), SCROLL_TEXT, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Pozycja Y (środek w pionie)
        y = (dh - text_h) // 2
        
        # Pozycja X startowa
        x = dw

        # Baza dla Partial Refresh
        base = Image.new('1', (dw, dh), 255)
        if ROTATE_DISPLAY: base = base.rotate(180)
        
        # Inicjalizacja trybu partial
        print("System: Przygotowanie trybu płynnego...")
        epd.displayPartBaseImage(epd.getbuffer(base))
        
        last_clean = time.time()

        print(f"Start przewijania: {SCROLL_TEXT}")

        while True:
            # 1. Okresowe czyszczenie ekranu (tylko co REFRESH_SEC)
            # To zapobiega nagromadzaniu się "szumów" (ghosting)
            if time.time() - last_clean > REFRESH_SEC:
                print("System: Czyszczenie artefaktów (Full Refresh)...")
                epd.init()
                epd.Clear(0xFF)
                epd.displayPartBaseImage(epd.getbuffer(base))
                epd.init()
                last_clean = time.time()

            # 2. Rysowanie klatki
            img = Image.new('1', (dw, dh), 255)
            draw = ImageDraw.Draw(img)

            # --- LOGIKA NIESKOŃCZONEJ PĘTLI ---
            # Rysujemy tekst pierwszy raz w pozycji X
            draw.text((x, y), SCROLL_TEXT, font=font, fill=0)

            # Jeśli tekst wjechał na ekran tak głęboko, że po prawej jest pusto...
            # ...rysujemy go DRUGI raz zaraz za pierwszym
            if x + text_w < dw:
                draw.text((x + text_w, y), SCROLL_TEXT, font=font, fill=0)

            # 3. Obrót
            if ROTATE_DISPLAY: img = img.rotate(180)

            # 4. Wyświetlenie (Szybkie, Częściowe)
            epd.displayPartial(epd.getbuffer(img))

            # 5. Przesunięcie
            x -= SCROLL_STEP

            # RESET BEZ MIGNIĘCIA:
            # Gdy pierwszy napis wyjedzie całkowicie w lewo (x < -text_w),
            # drugi napis jest dokładnie w miejscu, gdzie byłby pierwszy, gdyby x=0.
            # Więc po cichu przesuwamy X o długość tekstu. Oko tego nie zauważy.
            if x <= -text_w:
                x += text_w

            # Brak time.sleep() lub bardzo mały, aby uzyskać maksymalną płynność
            # e-ink i tak ma fizyczne ograniczenie odświeżania

    except KeyboardInterrupt:
        print("\nWyjście...")
    finally:
        epd.init()
        epd.sleep()

if __name__ == "__main__":
    main()