# Raspberry Pi Zero 2 W + E-ink Dashboard 🖥️

Kompleksowy dashboard dla wyświetlacza Waveshare e-Paper (2.13" V4) działający na Raspberry Pi Zero 2 W.
Projekt zawiera: menu (launcher), autostart, obsługę pogody, zegar oraz pokaz slajdów.

## 🌟 Funkcje

- **Launcher:** menu sterowania dostępne z terminala (komenda `menu`) oraz obsługa autostartu.
- **Zegar i Pogoda:** dane z Open-Meteo, data i godzina; częściowe odświeżanie aby zmniejszyć migotanie ekranu.
- **Pokaz slajdów:** wyświetlanie grafik z folderu `assets`.
- **Przewijany tekst:** demo płynnego przewijania tekstu na e-papierze.

## 📂 Struktura projektu (wybrane pliki)

```
.
├── install.sh              # Skrypt instalacyjny
├── README.md               # Ten plik
├── requirements.txt        # Wymagane pakiety Python
├── src/                    # Kody źródłowe
│   ├── launcher.py         # Menu / autostart
│   ├── common.py           # Wspólne ustawienia
│   ├── weather_clock.py    # Zegar i pogoda (bez sekund)
│   ├── weather_clock_seconds.py # Zegar i pogoda (z sekundami)
│   ├── scrolling_text.py   # Przewijany tekst
│   └── image_display.py    # Obsługa wyświetlania obrazów
├── assets/                 # Grafiki do pokazu slajdów
└── lib/                    # Sterowniki Waveshare
```

## 🛠 Wymagania sprzętowe

- Raspberry Pi Zero 2 W (inne modele RPi również powinny działać)
- Waveshare 2.13" e-Paper HAT (wersja V4)
- Karta SD z Raspberry Pi OS (zalecana: Lite)

## 🚀 Szybka instalacja
1. Zainstaluj Git (wymagane w wersji systemowej "Lite"):
```bash
sudo apt update
sudo apt install git -y
```
2. Sklonuj repozytorium:

```bash
git clone https://github.com/rafal-p4wlowski/rpi-zero-eink-dashboard.git
cd rpi-zero-eink-dashboard
```

2. Uruchom instalator:

```bash
chmod +x install.sh
./install.sh
```

Skrypt automatycznie zaktualizuje system, zainstaluje potrzebne pakiety, włączy SPI i skonfiguruje autostart.

3. Zrestartuj urządzenie po zakończeniu instalacji.

## 🎮 Uruchamianie i obsługa

- Po zalogowaniu przez SSH wpisz `menu` aby uruchomić interfejs wyboru trybu.
- Aby edytować ustawienia pogody, otwórz `src/weather_clock.py`, `src/weather_clock_seconds.py` i ustaw swoje współrzędne:

```python
WEATHER_LAT = 52.2297
WEATHER_LON = 21.0122
```

- Dodawanie zdjęć do pokazu slajdów: wrzuć pliki `.png` lub `.jpg` do folderu `assets/`.

## 🐛 Rozwiązywanie problemów

- Jeśli ekran nie działa po starcie, sprawdź log autostartu:

```bash
cat ~/launcher.log
```

- Upewnij się, że SPI jest włączone: `sudo raspi-config` → Interface Options → SPI.

## Jak to działa w praktyce

1. `git clone ...`
2. `./install.sh`
3. Poczekaj na zakończenie instalacji i zrestartuj RPi.
4. Po restarcie użyj `menu` aby sterować trybami wyświetlania.

---

Jeśli chcesz, mogę też: zaktualizować `requirements.txt`, dodać przykładowy `assets/` z grafikami albo przygotować krótki skrypt testowy sprawdzający SPI i połączenie z wyświetlaczem. Napisz, co preferujesz.