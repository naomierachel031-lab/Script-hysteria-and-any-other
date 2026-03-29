#!/bin/bash
clear
LN='\e[34m'
NC='\e[0m'
GR='\e[32m'
RD='\e[31m'
SERVER_HOST="https://raw.githubusercontent.com/naomierachel031-lab/Script-hysteria-and-any-other/main"

echo -e "${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${GR}       MISE À JOUR OTA (OVER-THE-AIR)             ${NC}${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "\n [*] Connexion au dépôt GitHub central..."
echo -e " [*] Déploiement des modules..."

# Liste absolue de tous les scripts du menu (y compris les nouveaux)
MODULES=(dns zivpn expiry domain iptools menu socks ssh status trojan vless vmess netguard port log tgbot uninstall update)

for script in "${MODULES[@]}"; do
    wget -q -O "/usr/local/sbin/$script" "${SERVER_HOST}/menu/${script}.sh"
    chmod +x "/usr/local/sbin/$script"
    echo -e "  -> Module $script [OK]"
done

echo -e "\n ${GR}[+] Mise à jour OTA terminée avec succès !${NC}"

# === CORRECTIF : SSH Port 8080 uniquement via Stunnel ===
echo -e "\n${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${GR}      CORRECTIF SSH PORT 8080 (Stunnel)           ${NC}${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e " [*] Application du correctif Stunnel SSH (port 8080 uniquement)..."

# Déployer le script core setup_ssh pour les nouvelles installations
if wget -q -O /usr/bin/setup_ssh "${SERVER_HOST}/core/sshws.sh"; then
    chmod +x /usr/bin/setup_ssh
    echo -e "  -> Script setup_ssh déployé [OK]"
else
    echo -e "  -> ${RD}Échec du téléchargement de setup_ssh${NC}"
fi

CONF_FILE="/etc/stunnel5/stunnel5.conf"
if [ -f "$CONF_FILE" ]; then
    STUNNEL_CHANGED=0
    # Supprimer le bloc [openssh-80] s'il existe (port 80 réservé à Nginx)
    if grep -q "\[openssh-80\]" "$CONF_FILE"; then
        sed -i '/^\[openssh-80\]/{N;N;d}' "$CONF_FILE"
        echo -e "  -> Conflit port 80 supprimé de Stunnel [OK]"
        STUNNEL_CHANGED=1
    fi
    # Ajouter [openssh-8080] si absent
    if ! grep -q "\[openssh-8080\]" "$CONF_FILE"; then
        printf '\n[openssh-8080]\naccept = 8080\nconnect = 127.0.0.1:22\n' >> "$CONF_FILE"
        echo -e "  -> Port 8080 ajouté à Stunnel [OK]"
        STUNNEL_CHANGED=1
    else
        echo -e "  -> Port 8080 déjà configuré [OK]"
    fi
    if [ "$STUNNEL_CHANGED" -eq 1 ]; then
        systemctl restart stunnel5 && echo -e "  -> Stunnel5 redémarré [OK]" || \
            echo -e "  -> ${RD}Avertissement : échec du redémarrage de Stunnel5${NC}"
        systemctl restart ssh && echo -e "  -> SSH redémarré [OK]" || true
    fi
else
    echo -e "  -> ${RD}Fichier stunnel5.conf introuvable, correctif ignoré.${NC}"
fi

echo -e "\n${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${GR}              NOTES DE MISE À JOUR                ${NC}${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "  ${GR}✔${NC} SSH accessible sur le port 8080 via Stunnel (SSL)"
echo -e "  ${GR}✔${NC} Port 80 réservé exclusivement à Nginx (pas de conflit SSH)"
echo -e "  ${GR}✔${NC} Aucun impact sur les autres protocoles (Xray, DNS, etc.)"
echo -e "  ${GR}✔${NC} Correctif compatible avec les installations existantes"

sleep 2
menu
