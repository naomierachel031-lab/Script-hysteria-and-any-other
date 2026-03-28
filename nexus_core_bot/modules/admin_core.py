import json

CONFIG_FILE = '/etc/nexus_bot/config.json'

def get_config():
    with open(CONFIG_FILE, 'r') as f: return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f: json.dump(cfg, f, indent=4)

def list_admins():
    cfg = get_config()
    admins = cfg.get('admins', [])
    super_admin = cfg.get('super_admin')
    
    msg = f"👑 <b>SUPER ADMIN :</b>\n<code>{super_admin}</code>\n\n"
    msg += "👮‍♂️ <b>ADMINISTRATEURS DÉLÉGUÉS :</b>\n"
    if not admins:
        msg += "<i>Aucun administrateur secondaire.</i>"
    else:
        for a in admins: msg += f"▪️ <code>{a}</code>\n"
    return msg

def is_super_admin(user_id):
    return user_id == get_config().get('super_admin')

def approve_new_admin(admin_id):
    cfg = get_config()
    admin_id = int(admin_id)
    if admin_id in cfg.get('admins', []) or admin_id == cfg.get('super_admin'):
        return False, "Déjà administrateur."
    cfg.setdefault('admins', []).append(admin_id)
    save_config(cfg)
    return True, "Approuvé."

def remove_admin(admin_id):
    cfg = get_config()
    admin_id = int(admin_id)
    if admin_id == cfg.get('super_admin'):
        return False, "Le Super Admin ne peut pas être supprimé."
    if admin_id in cfg.get('admins', []):
        cfg['admins'].remove(admin_id)
        save_config(cfg)
        return True, "Administrateur révoqué."
    return False, "ID introuvable."
