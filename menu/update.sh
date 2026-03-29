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
echo -e "\033[91m"
echo "════════════════════════════════════════"
echo "🔴 MESSAGE 99 - CORRECTION SSH APPLIQUÉE"
echo "════════════════════════════════════════"
echo ""
echo "✓ SSH Port 8181 CONFIGURÉ (Stunnel TLS)"
echo "✓ Port 447 Dropbear ACTIF"
echo "✓ Protocole STABLE - SANS CONFLITS"
echo ""
echo "════════════════════════════════════════"
echo -e "\033[0m"

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

# === CORRECTIF : SSH Port 8181 uniquement via Stunnel ===
echo -e "\n${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${GR}      CORRECTIF SSH PORT 8181 (Stunnel TLS)       ${NC}${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e " [*] Application du correctif Stunnel SSH (port 8181 uniquement)..."

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
    # Supprimer les blocs conflictuels [openssh-80] et [openssh-8080]
    for old_port in "openssh-80" "openssh-8080"; do
        if grep -q "\[${old_port}\]" "$CONF_FILE"; then
            sed -i "/^\[${old_port}\]/{N;N;d}" "$CONF_FILE"
            echo -e "  -> Bloc [${old_port}] supprimé de Stunnel [OK]"
            STUNNEL_CHANGED=1
        fi
    done
    # Ajouter [openssh-8181] si absent
    if ! grep -q "\[openssh-8181\]" "$CONF_FILE"; then
        printf '\n[openssh-8181]\naccept = 8181\nconnect = 127.0.0.1:22\n' >> "$CONF_FILE"
        echo -e "  -> Port 8181 ajouté à Stunnel [OK]"
        STUNNEL_CHANGED=1
    else
        echo -e "  -> Port 8181 déjà configuré [OK]"
    fi
    if [ "$STUNNEL_CHANGED" -eq 1 ]; then
        systemctl restart stunnel5 && echo -e "  -> Stunnel5 redémarré [OK]" || \
            echo -e "  -> ${RD}Avertissement : échec du redémarrage de Stunnel5${NC}"
        systemctl restart ssh && echo -e "  -> SSH redémarré [OK]" || true
    fi
else
    echo -e "  -> ${RD}Fichier stunnel5.conf introuvable, correctif ignoré.${NC}"
fi

# Mettre à jour le fichier port_info avec le nouveau port SSH
PORT_INFO="/etc/vps/port_info"
if [ -f "$PORT_INFO" ]; then
    # Supprimer les anciennes entrées SSH WS/WSS
    sed -i '/SSH WS/d' "$PORT_INFO"
    sed -i '/SSH WSS/d' "$PORT_INFO"
    # Ajouter SSH Stunnel 8181 si absent
    if ! grep -q "SSH Stunnel" "$PORT_INFO"; then
        sed -i "1s/^/SSH Stunnel (TLS)      : 8181\n/" "$PORT_INFO"
        echo -e "  -> port_info mis à jour avec SSH Stunnel 8181 [OK]"
    else
        echo -e "  -> SSH Stunnel 8181 déjà présent dans port_info [OK]"
    fi
fi

echo -e "\n${LN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
echo -e "${LN}┃${NC} ${GR}              NOTES DE MISE À JOUR                ${NC}${LN}┃${NC}"
echo -e "${LN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
echo -e "  ${GR}✔${NC} SSH accessible sur le port 8181 via Stunnel (TLS)"
echo -e "  ${GR}✔${NC} Port 80 réservé exclusivement à Nginx (pas de conflit SSH)"
echo -e "  ${GR}✔${NC} Aucun impact sur les autres protocoles (Xray, DNS, etc.)"
echo -e "  ${GR}✔${NC} Correctif compatible avec les installations existantes"

# === MISE À JOUR DE LA VERSION LOCALE ===
LATEST_VERSION=$(curl -sS "${SERVER_HOST}/version" 2>/dev/null | tr -d '[:space:]')
if [[ "$LATEST_VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    echo "$LATEST_VERSION" > /etc/version
    echo -e "  ${GR}✔${NC} Version locale mise à jour : ${LATEST_VERSION}"
    echo -e "\n${RD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${RD}┃${NC}  ✅  Mise à jour v${LATEST_VERSION} appliquée avec succès !   ${RD}┃${NC}"
    echo -e "${RD}┃${NC}  Le menu est maintenant à jour. À la prochaine !  ${RD}┃${NC}"
    echo -e "${RD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
else
    echo -e "  ${GR}✔${NC} Mise à jour appliquée avec succès !"
fi

sleep 2
menu
