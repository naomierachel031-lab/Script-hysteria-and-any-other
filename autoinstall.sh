#!/bin/bash

echo "===================================================="
echo "    DÉMARRAGE DE L'INSTALLATION PERSONNALISÉE       "
echo "===================================================="

# 1. Correction réseau (Le correctif absolu contre les écrans noirs)
echo "[+] Désactivation stricte de l'IPv6 et forçage IPv4 au niveau du noyau..."
echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf
echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

# 2. Mise en place de l'attaque Man-in-the-Middle locale
echo "[+] Injection des intercepteurs réseau..."
cat << 'EOF' > /usr/local/bin/wget
#!/bin/bash
NEW_ARGS=()
for arg in "$@"; do
    if [[ "$arg" == *"dotywrt/doty"* ]]; then
        arg="${arg//dotywrt\/doty/tchindaazice\/script-hysteria-and-any-other}"
    fi
    NEW_ARGS+=("$arg")
done
/usr/bin/wget "${NEW_ARGS[@]}"
EOF
chmod +x /usr/local/bin/wget

cat << 'EOF' > /usr/local/bin/curl
#!/bin/bash
NEW_ARGS=()
for arg in "$@"; do
    if [[ "$arg" == *"dotywrt/doty"* ]]; then
        arg="${arg//dotywrt\/doty/tchindaazice\/script-hysteria-and-any-other}"
    fi
    NEW_ARGS+=("$arg")
done
/usr/bin/curl "${NEW_ARGS[@]}"
EOF
chmod +x /usr/local/bin/curl

export PATH="/usr/local/bin:$PATH"

# 3. Lancement du binaire principal 
echo "[+] Téléchargement et exécution du moteur d'installation..."
/usr/bin/wget -4 -qO /root/doty.sh https://raw.githubusercontent.com/tchindaazice/script-hysteria-and-any-other/main/doty.sh
chmod +x /root/doty.sh
/root/doty.sh

# 4. Nettoyage de l'environnement
echo "[+] Suppression des intercepteurs réseau..."
rm -f /usr/local/bin/wget /usr/local/bin/curl
hash -r

echo "===================================================="
echo "   INSTALLATION ET RÉPARATION TERMINÉES AVEC SUCCÈS "
echo "===================================================="
