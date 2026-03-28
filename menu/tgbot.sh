#!/bin/bash
clear
LN='\e[36m'
NC='\e[0m'
BG='\e[44m'
RD='\e[31m'
GR='\e[32m'

echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${BG}           INSTALLATION DE NEXUS BOT            ${NC} ${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e ""
echo -e " Ce module va relier votre serveur à Telegram."
echo -e " Vous deviendrez le SUPER ADMIN du système."
echo -e ""

read -p " ➔ Entrez le TOKEN du Bot (ex: 1234:ABCDef...) : " bot_token
if [[ -z "$bot_token" ]]; then
    echo -e "${RD}Erreur: Le Token est obligatoire.${NC}"
    sleep 2
    exit
fi

read -p " ➔ Entrez votre ID Telegram (ex: 123456789) : " admin_id
if [[ -z "$admin_id" ]]; then
    echo -e "${RD}Erreur: L'ID Admin est obligatoire.${NC}"
    sleep 2
    exit
fi

echo -e "\n${GR}[+] Configuration du système en cours...${NC}"
mkdir -p /etc/nexus_bot
cat <<JSON > /etc/nexus_bot/config.json
{
  "bot_token": "$bot_token",
  "super_admin": $admin_id,
  "admins": []
}
JSON

echo -e "${GR}[+] Installation des dépendances Python...${NC}"
apt-get install -y python3 python3-pip >/dev/null 2>&1
pip3 install pyTelegramBotAPI >/dev/null 2>&1

echo -e "${GR}[+] Base de données Super Admin verrouillée.${NC}"
echo -e "\n Appuyez sur ENTRÉE pour retourner au menu."
read
menu
