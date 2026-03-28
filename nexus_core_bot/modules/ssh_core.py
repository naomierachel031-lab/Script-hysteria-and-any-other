import subprocess
import os
from datetime import datetime, timedelta

def get_file(path, default="NON_DEFINI"):
    try:
        with open(path, 'r') as f: return f.read().strip()
    except:
        return default

def create_ssh_account(user, password, days):
    cmd = f"useradd -e $(date -d '{days} days' +'%Y-%m-%d') -s /bin/false -M {user} && echo '{user}:{password}' | chpasswd"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if res.returncode == 0:
        exp_date = (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
        
        # Récupération des variables d'environnement du serveur
        domain = get_file('/etc/xray/domain', 'votre-domaine.com')
        pub_key = get_file('/etc/slowdns/server.pub', 'PUB_KEY_NOT_FOUND')
        ns_domain = get_file('/etc/slowdns/nsdomain', 'NS_DOMAIN_NOT_FOUND')
        myip = subprocess.getoutput("wget -qO- ipv4.icanhazip.com")
        
        # Formatage miroir de ton terminal Bash
        msg = (
            f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┃ <b>SSH ACCOUNT DETAILS</b>\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
            f"👤 <b>Username:</b> <code>{user}</code>\n"
            f"🔑 <b>Password:</b> <code>{password}</code>\n"
            f"⏳ <b>Expiry Date:</b> {exp_date}\n"
            f"🖥️ <b>Host/IP:</b> {myip}\n"
            f"🌐 <b>Domain:</b> {domain}\n"
            f"📛 <b>NS Domain:</b> {ns_domain}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 <b>UDP Custom:</b>\n"
            f"<code>{domain}:1-65535@{user}:{password}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🐌 <b>Slow DNS:</b>\n"
            f"PUB: <code>{pub_key}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>Payload WS:</b>\n"
            f"<code>GET / HTTP/1.1[crlf]Host: {domain}[crlf]Upgrade: websocket[crlf][crlf]</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔌 <b>Ports:</b> OpenSSH(22), Dropbear(109,143), UDPGW(7100-7900), WS(80,443)\n"
        )
        return True, msg
    return False, f"❌ Échec de la création:\n<code>{res.stderr}</code>"

def list_ssh_accounts():
    cmd = "awk -F: '($3 >= 1000 && $1 != \"nobody\") {print $1}' /etc/passwd"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    users = res.stdout.strip().split('\n')
    if not users or users == ['']: return "📋 Aucun compte SSH trouvé."
    
    msg = "📋 <b>LISTE DES COMPTES SSH:</b>\n\n"
    for u in users:
        exp_cmd = f"chage -l {u} | grep 'Account expires' | awk -F': ' '{{print $2}}'"
        exp_date = subprocess.run(exp_cmd, shell=True, capture_output=True, text=True).stdout.strip()
        msg += f"👤 <code>{u}</code> - Expire: <i>{exp_date}</i>\n"
    return msg
