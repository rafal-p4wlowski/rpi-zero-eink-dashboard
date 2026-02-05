#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sys
import os
import time

# ==============================================================================
# 1. KONFIGURACJA WSPÓLNA (MODUŁ)
# ==============================================================================

def get_epd_driver():
    """
    Automatycznie znajduje ścieżki do bibliotek i zwraca obiekt sterownika ekranu.
    """
    # Aktualny katalog pliku common.py
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Możliwe lokalizacje folderu 'lib'
    libdir_local = os.path.join(current_dir, 'lib')                 # src/lib
    libdir_parent = os.path.join(os.path.dirname(current_dir), 'lib') # src/../lib

    found_path = None

    if os.path.exists(libdir_local):
        found_path = libdir_local
    elif os.path.exists(libdir_parent):
        found_path = libdir_parent
    
    if not found_path:
        print(f"BŁĄD KRYTYCZNY (common.py): Nie znaleziono folderu 'lib'!")
        print(f"Szukano w: \n1. {libdir_local}\n2. {libdir_parent}")
        sys.exit(1)

    # Dodaj znalezioną ścieżkę do sys.path
    sys.path.insert(0, found_path)

    try:
        from waveshare_epd import epd2in13_V4 as epd_driver
        return epd_driver
    except ImportError as e:
        # Obsługa błędu importu
        print("---------------------------------------------------------")
        print("BŁĄD IMPORTU STEROWNIKA (common.py)")
        print(f"Szczegóły błędu: {e}")
        print("---------------------------------------------------------")
        sys.exit(1)

def init_display(epd):
    """Pomocnicza funkcja do bezpiecznej inicjalizacji."""
    print("System: Inicjalizacja ekranu...")
    epd.init()
    # Wersja V4 wymaga czyszczenia na start
    epd.Clear(0xFF) 
    time.sleep(1)