import uuid
import base64
import subprocess
from datetime import datetime, timedelta
import os

XRAY_CONF = '/etc/xray/config.json'

def get_domain():
    try:
        with open('/etc/xray/domain', 'r') as f: return f.read().strip()
    except:
        return "votre-domaine.com"

def create_xray_account(protocol, user, days):
    if not os.path.exists(XRAY_CONF):
        return False, "❌ Fichier config Xray introuvable."
        
    days = int(days)
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    client_id = str(uuid.uuid4())
    domain = get_domain()
    
    # 1. LECTURE SÉCURISÉE (Pour ne pas effacer les commentaires Bash)
    with open(XRAY_CONF, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    injected = False
    
    # 2. INJECTION CHIRURGICALE STYLE "SED"
    for line in lines:
        new_lines.append(line)
        clean_line = line.strip()
        
        if protocol == 'vless':
            if clean_line == '#vless' or clean_line == '#vlessgrpc':
                new_lines.append(f'#& {user} {exp_date} {client_id}\n')
                new_lines.append(f'}},{{"id": "{client_id}","email": "{user}"\n')
                injected = True
                
        elif protocol == 'vmess':
            if clean_line == '#vmess' or clean_line == '#vmessgrpc':
                new_lines.append(f'### {user} {exp_date} {client_id}\n')
                new_lines.append(f'}},{{"id": "{client_id}","alterId": 0,"email": "{user}"\n')
                injected = True
                
        elif protocol == 'trojan':
            if clean_line == '#trojanws' or clean_line == '#trojangrpc':
                new_lines.append(f'#! {user} {exp_date} {client_id}\n')
                new_lines.append(f'}},{{"password": "{client_id}","email": "{user}"\n')
                injected = True

    if not injected:
        return False, f"❌ Balises Bash pour {protocol.upper()} introuvables."

    with open(XRAY_CONF, 'w') as f:
        f.writelines(new_lines)
        
    subprocess.run("systemctl restart xray", shell=True)
    
    # 3. GÉNÉRATION DES PAYLOADS EXACTS
    if protocol == 'vless':
        link_tls = f"vless://{client_id}@{domain}:443?path=/vless&security=tls&encryption=none&type=ws#{user}"
        link_ntls = f"vless://{client_id}@{domain}:80?path=/vless&encryption=none&type=ws#{user}"
        link_grpc = f"vless://{client_id}@{domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc#{user}"
        
    elif protocol == 'vmess':
        ws_tls = f'{{"v":"2","ps":"{user}","add":"{domain}","port":"443","id":"{client_id}","aid":"0","net":"ws","path":"/vmess","type":"none","host":"","tls":"tls"}}'
        ws_ntls = f'{{"v":"2","ps":"{user}","add":"{domain}","port":"80","id":"{client_id}","aid":"0","net":"ws","path":"/vmess","type":"none","host":"","tls":"none"}}'
        grpc = f'{{"v":"2","ps":"{user}","add":"{domain}","port":"443","id":"{client_id}","aid":"0","net":"grpc","path":"vmess-grpc","type":"none","host":"","tls":"tls"}}'
        
        link_tls = "vmess://" + base64.b64encode(ws_tls.encode('utf-8')).decode('utf-8')
        link_ntls = "vmess://" + base64.b64encode(ws_ntls.encode('utf-8')).decode('utf-8')
        link_grpc = "vmess://" + base64.b64encode(grpc.encode('utf-8')).decode('utf-8')
        
    elif protocol == 'trojan':
        link_tls = f"trojan://{client_id}@{domain}:443?path=/trws&security=tls&encryption=none&host={domain}&type=ws#{user}"
        link_ntls = f"trojan://{client_id}@{domain}:80?path=/trws&encryption=none&security=none&host={domain}&type=ws#{user}"
        link_grpc = f"trojan://{client_id}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni={domain}#{user}"

    # 4. FORMATAGE DE L'INTERFACE TELEGRAM
    msg = (
        f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃ <b>{protocol.upper()} ACCOUNT DETAILS</b>\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
        f"👤 <b>Username:</b> <code>{user}</code>\n"
        f"⏳ <b>Expired:</b> <code>{exp_date}</code>\n"
        f"🔑 <b>UUID/Pass:</b> <code>{client_id}</code>\n"
        f"🌐 <b>Domain:</b> <code>{domain}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>TLS (443) :</b>\n<code>{link_tls}</code>\n\n"
        f"🔗 <b>NTLS (80) :</b>\n<code>{link_ntls}</code>\n\n"
        f"🔗 <b>GRPC (443) :</b>\n<code>{link_grpc}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    return True, msg
