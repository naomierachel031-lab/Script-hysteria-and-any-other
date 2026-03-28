import subprocess
import os
from datetime import datetime, timedelta

def get_file(path, default="NON_DEFINI"):
    try:
        with open(path, 'r') as f: return f.read().strip()
    except:
        return default

def create_zivpn_account(user, password, days):
    db_file = '/etc/zivpn/user.db'
    conf_file = '/etc/zivpn/config.json'
    
    if not os.path.exists(conf_file):
        return False, "❌ Fichier config ZIVPN introuvable. Le VPS est-il bien configuré ?"
        
    # Vérification des doublons
    try:
        with open(db_file, 'r') as f:
            content = f.read()
            if user in content or password in content:
                return False, "❌ Nom d'utilisateur ou Mot de passe déjà utilisé."
    except: pass
    
    days = int(days)
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Injection dans le JSON ZIVPN (Simulation du SED)
    with open(conf_file, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if '"config": [' in line:
            new_lines.append(f'      "{password}",\n')
            
    with open(conf_file, 'w') as f:
        f.writelines(new_lines)
        
    # Ajout dans la base de données
    with open(db_file, 'a') as f:
        f.write(f"{user} {password} {exp_date}\n")
        
    subprocess.run("systemctl restart zivpn", shell=True)
    
    domain = get_file('/etc/xray/domain', 'votre-domaine.com')
    myip = subprocess.getoutput("wget -qO- ipv4.icanhazip.com")
    
    msg = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ <b>ZIVPN ACCOUNT DETAILS</b>\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"👤 <b>Username:</b> <code>{user}</code>\n"
        f"🔑 <b>Password:</b> <code>{password}</code>\n"
        f"⏳ <b>Expiry Date:</b> {exp_date}\n"
        f"🖥️ <b>IPV4:</b> <code>{myip}</code>\n"
        f"🌐 <b>Domain:</b> <code>{domain}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    return True, msg

def list_zivpn_accounts():
    db_file = '/etc/zivpn/user.db'
    if not os.path.exists(db_file): return "📋 Aucun compte ZIVPN trouvé."
    
    with open(db_file, 'r') as f:
        lines = f.readlines()
        
    if not lines: return "📋 Aucun compte ZIVPN trouvé."
    
    msg = "📋 <b>LISTE DES COMPTES ZIVPN:</b>\n\n"
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 3:
            msg += f"👤 <code>{parts[0]}</code> | Pass: <code>{parts[1]}</code> | Exp: <i>{parts[2]}</i>\n"
    return msg
