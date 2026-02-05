#!/bin/bash

# Kolory dla czytelności
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}==================================================${NC}"
echo -e "${CYAN}   RPI E-INK DASHBOARD - INSTALATOR AUTOMATYCZNY  ${NC}"
echo -e "${CYAN}==================================================${NC}"

# 1. Sprawdzenie uprawnień
USER_HOME=$(eval echo ~${SUDO_USER})
PROJECT_DIR=$(pwd)

echo -e "${GREEN}[1/6] Aktualizacja systemu (to może chwilę potrwać)...${NC}"
sudo apt update && sudo apt full-upgrade -y

echo -e "${GREEN}[2/6] Instalacja zależności systemowych i Python...${NC}"
# Dodano 'git' oraz zamieniono 'libtiff5' na 'libtiff6' (dla nowszych systemów)
# Dodano 'libtiff-dev' jako zabezpieczenie
sudo apt install -y python3-pip python3-pil python3-numpy python3-requests python3-rpi.gpio python3-spidev git libopenjp2-7 libtiff6 libtiff-dev fonts-dejavu

echo -e "${GREEN}[3/6] Generowanie polskich znaków (Locale)...${NC}"
# Automatyczne odkomentowanie pl_PL.UTF-8 w /etc/locale.gen
if grep -q "# pl_PL.UTF-8 UTF-8" /etc/locale.gen; then
    echo "Odblokowywanie języka polskiego..."
    sudo sed -i 's/# pl_PL.UTF-8 UTF-8/pl_PL.UTF-8 UTF-8/' /etc/locale.gen
    sudo locale-gen
    echo "Polskie locale wygenerowane."
else
    echo "Polskie locale wygląda na już aktywne."
fi

echo -e "${GREEN}[4/6] Konfiguracja sprzętowa (Włączanie SPI)...${NC}"
# Używamy raspi-config w trybie non-interactive do włączenia SPI
sudo raspi-config nonint do_spi 0
echo "Interfejs SPI włączony."

echo -e "${GREEN}[5/6] Dodawanie aliasu 'menu' do .bashrc...${NC}"
BASHRC="$USER_HOME/.bashrc"
ALIAS_CMD="alias menu='python3 $PROJECT_DIR/src/launcher.py'"

if grep -q "alias menu=" "$BASHRC"; then
    echo "Alias 'menu' już istnieje."
else
    echo "$ALIAS_CMD" >> "$BASHRC"
    echo "Alias dodany. Będzie dostępny po ponownym zalogowaniu."
fi

echo -e "${GREEN}[6/6] Konfiguracja Autostartu (CRON)...${NC}"
# Komenda do crona z opóźnieniem 20s i logowaniem błędów
CRON_CMD="@reboot /bin/sleep 20 && /usr/bin/python3 $PROJECT_DIR/src/launcher.py --boot > $USER_HOME/launcher.log 2>&1"

# Sprawdź czy zadanie już istnieje, żeby nie dublować
EXISTING_CRON=$(crontab -l 2>/dev/null)
if echo "$EXISTING_CRON" | grep -q "launcher.py --boot"; then
    echo "Autostart jest już skonfigurowany w CRON."
else
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "Dodano zadanie do CRON."
fi

echo -e "${GREEN}[FINISH] Nadawanie uprawnień wykonywalności...${NC}"
chmod +x src/*.py

echo -e "${CYAN}==================================================${NC}"
echo -e "${CYAN}   INSTALACJA ZAKOŃCZONA SUKCESEM!                ${NC}"
echo -e "${CYAN}==================================================${NC}"
echo "1. Wpisz 'source ~/.bashrc' aby używać komendy 'menu' od razu."
echo "2. Zrestartuj system ('sudo reboot'), aby przetestować autostart i locale."
echo ""
read -p "Czy chcesz zrestartować system teraz? (t/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[TtYy]$ ]]
then
    sudo reboot
fi