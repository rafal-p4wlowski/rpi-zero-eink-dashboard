#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import time
import glob
import common
from PIL import Image, ImageSequence

# ==============================================================================
# 1. KONFIGURACJA UŻYTKOWNIKA
# ==============================================================================
ROTATE_DISPLAY = True          # True = obrót o 180 stopni
SLIDE_DURATION = 15            # Czas wyświetlania (sekundy)
IMG_FOLDER = '../assets'             # Nazwa folderu (względem tego pliku)

# ==============================================================================
# 2. GŁÓWNA PĘTLA PROGRAMU
# ==============================================================================
def main():
    # Inicjalizacja sterownika z common
    epd_driver = common.get_epd_driver()
    epd = epd_driver.EPD()
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    img_path_full = os.path.join(current_dir, IMG_FOLDER)

    try:
        common.init_display(epd)

        # Pobieranie listy plików
        exts = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        images = []
        for ext in exts:
            images.extend(glob.glob(os.path.join(img_path_full, ext)))
            images.extend(glob.glob(os.path.join(img_path_full, ext.upper())))
        
        images.sort()
        if not images:
            print(f"BŁĄD: Pusty folder {IMG_FOLDER}")
            return

        print(f"Znaleziono {len(images)} obrazów.")

        # Przygotowanie partial refresh
        base = Image.new('1', (epd.height, epd.width), 255)
        if ROTATE_DISPLAY: base = base.rotate(180)
        epd.displayPartBaseImage(epd.getbuffer(base))

        while True:
            for fpath in images:
                try:
                    print(f"Wyświetlam: {os.path.basename(fpath)}")
                    img = Image.open(fpath)

                    # GIF i Przezroczystość
                    if getattr(img, 'is_animated', False):
                        img = next(ImageSequence.Iterator(img))
                    
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        bg = Image.new('RGB', img.size, (255, 255, 255))
                        bg.paste(img.convert('RGBA'), (0, 0), img.convert('RGBA'))
                        img = bg
                    else:
                        img = img.convert('RGB')

                    # Skalowanie
                    tw, th = epd.height, epd.width
                    iw, ih = img.size
                    if iw > tw or ih > th:
                        ratio = min(tw/iw, th/ih)
                        img = img.resize((int(iw*ratio), int(ih*ratio)), Image.Resampling.LANCZOS)

                    # Centrowanie i wklejanie
                    canvas = Image.new('1', (tw, th), 255)
                    x = (tw - img.width) // 2
                    y = (th - img.height) // 2
                    canvas.paste(img.convert('1'), (x, y))

                    if ROTATE_DISPLAY: canvas = canvas.rotate(180)

                    epd.displayPartial(epd.getbuffer(canvas))
                    time.sleep(SLIDE_DURATION)

                except Exception as e:
                    print(f"Błąd pliku: {e}")

    except KeyboardInterrupt:
        print("\nWyjście...")
    finally:
        epd.init()
        epd.sleep()

if __name__ == "__main__":
    main()