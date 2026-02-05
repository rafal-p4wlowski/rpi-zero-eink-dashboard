#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import sys
import time
import subprocess
import json
import argparse

# ==============================================================================
# KONFIGURACJA
# ==============================================================================
# Lista dostępnych programów
PROGRAMS = {
    "weather_clock.py": "Zegar Minutowy (Standard)",
    "weather_clock_seconds.py": "Zegar Sekundowy (Demo)",
    "image_display.py": "Pokaz Slajdów",
    "scrolling_text.py": "Przewijany Tekst"
}

# Plik przechowujący ostatni stan
STATE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "state.json")
DEFAULT_PROGRAM = "weather_clock.py"

# ==============================================================================
# FUNKCJE STANU (ZAPIS/ODCZYT)
# ==============================================================================
def load_last_program():
    """Odczytuje z pliku nazwę ostatnio używanego programu."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                prog = data.get("last_program", DEFAULT_PROGRAM)
                # Sprawdź czy program nadal istnieje w naszej liście
                if prog in PROGRAMS:
                    return prog
        except Exception as e:
            print(f"Błąd odczytu stanu: {e}")
    return DEFAULT_PROGRAM

def save_last_program(program_name):
    """Zapisuje nazwę programu do pliku."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({"last_program": program_name}, f)
    except Exception as e:
        print(f"Błąd zapisu stanu: {e}")

# ==============================================================================
# FUNKCJE SYSTEMOWE
# ==============================================================================
def clear_console():
    os.system('clear')

def kill_running_programs():
    """Zabija wszystkie programy z listy PROGRAMS."""
    current_script = os.path.basename(__file__)
    
    for script_name in PROGRAMS.keys():
        if script_name == current_script:
            continue
        try:
            # Wyciszamy błędy, jeśli proces nie istnieje
            os.system(f"pkill -f {script_name} > /dev/null 2>&1")
        except Exception:
            pass
    
    time.sleep(0.5)

def launch_program(script_name):
    """Uruchamia program w tle i zapisuje to w stanie."""
    
    # 1. Ścieżka do pliku
    script_dir = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"BŁĄD: Nie znaleziono pliku {script_path}")
        return

    # 2. Zapisz wybór (żeby po restarcie wstał ten sam)
    save_last_program(script_name)

    # 3. Uruchomienie w tle (detached)
    print(f"--> Uruchamianie: {PROGRAMS[script_name]}...")
    try:
        subprocess.Popen(["python3", script_path], 
                         cwd=script_dir,
                         stdout=open(os.devnull, 'w'), 
                         stderr=open(os.devnull, 'w'),
                         preexec_fn=os.setpgrp)
    except Exception as e:
        print(f"Nie udało się uruchomić: {e}")

# ==============================================================================
# GŁÓWNA PĘTLA
# ==============================================================================
def main():
    # Obsługa argumentów (dla autostartu)
    parser = argparse.ArgumentParser()
    parser.add_argument("--boot", action="store_true", help="Tryb autostartu (bez menu)")
    args = parser.parse_args()

    # --- TRYB BOOT (AUTOSTART) ---
    if args.boot:
        print("Tryb BOOT: Przywracanie ostatniego programu...")
        kill_running_programs()
        last_prog = load_last_program()
        launch_program(last_prog)
        sys.exit(0) # Kończymy działanie launchera, program działa w tle

    # --- TRYB MENU (INTERAKTYWNY) ---
    while True:
        clear_console()
        print("========================================")
        print("   RPI ZERO 2 W - E-INK LAUNCHER")
        print("========================================")
        
        last_prog = load_last_program()
        print(f"Aktualnie ustawiony: {last_prog}\n")
        
        prog_list = list(PROGRAMS.items())
        for idx, (filename, label) in enumerate(prog_list):
            prefix = "*" if filename == last_prog else " "
            print(f" {prefix} {idx + 1}. {label}")
        
        print("\n 9. ZATRZYMAJ WSZYSTKO")
        print(" 0. Wyjście")
        print("========================================")
        
        choice = input("Wybór: ")

        if choice == '0':
            sys.exit()
            
        elif choice == '9':
            kill_running_programs()
            print("Zatrzymano.")
            time.sleep(1)
            
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(prog_list):
                    selected_file = prog_list[idx][0]
                    kill_running_programs()
                    launch_program(selected_file)
                    time.sleep(1)
                    # Nie wychodzimy z menu, żeby widzieć że się udało
                else:
                    print("Błędny numer.")
                    time.sleep(1)
            except ValueError:
                time.sleep(1)

if __name__ == "__main__":
    main()