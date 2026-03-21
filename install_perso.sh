#!/bin/bash
# Lien direct vers votre propre dépôt GitHub
GITHUB_RAW="https://raw.githubusercontent.com/tchindaazice/script-hysteria-and-any-other/main"

echo "Téléchargement de vos fichiers d'installation d'origine..."

# 1. Télécharger vos anciens protocoles disparus (ZIVPN et UDP)
wget -q -O /usr/local/bin/setup_zivpn $GITHUB_RAW/core/setup_zivpn.sh
wget -q -O /usr/local/bin/setup_udp $GITHUB_RAW/core/setup_udp.sh

# 2. Télécharger les protocoles de base depuis VOTRE dépôt (Xray, SSH, etc.)
wget -q -O /usr/local/bin/setup_xray $GITHUB_RAW/core/xray.sh
wget -q -O /usr/local/bin/setup_ssh $GITHUB_RAW/core/sshws.sh

# 3. Télécharger votre ancien Menu qui contient toutes les options
wget -q -O /usr/local/bin/menu $GITHUB_RAW/menu/menu.sh

# Rendre tous les fichiers exécutables
chmod +x /usr/local/bin/setup_zivpn /usr/local/bin/setup_udp /usr/local/bin/setup_xray /usr/local/bin/setup_ssh /usr/local/bin/menu

echo "Exécution des installations..."
# Lancement des scripts pour configurer les protocoles sur le serveur
/usr/local/bin/setup_xray
/usr/local/bin/setup_ssh
/usr/local/bin/setup_zivpn
/usr/local/bin/setup_udp

echo "Installation terminée avec succès depuis votre dépôt ! Tapez 'menu' pour afficher l'interface."
