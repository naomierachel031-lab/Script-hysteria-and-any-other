import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

CONFIG_FILE = '/etc/nexus_bot/config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, 'r') as f: return json.load(f)

config = load_config()
if not config: exit(1)

bot = telebot.TeleBot(config.get('bot_token'))
SUPER_ADMIN = int(config.get('super_admin'))

def is_admin(user_id):
    cfg = load_config()
    return user_id == SUPER_ADMIN or user_id in cfg.get('admins', [])

# --- MATRICE DU MENU PRINCIPAL ---
def main_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("01 • SSH/WS", callback_data="menu_ssh"),
        InlineKeyboardButton("02 • VMESS", callback_data="menu_vmess"),
        InlineKeyboardButton("03 • VLESS", callback_data="menu_vless"),
        InlineKeyboardButton("04 • TROJAN", callback_data="menu_trojan"),
        InlineKeyboardButton("05 • SOCKS", callback_data="menu_socks"),
        InlineKeyboardButton("06 • ZIVPN", callback_data="menu_zivpn"),
        InlineKeyboardButton("07 • DNS PANEL", callback_data="menu_dns"),
        InlineKeyboardButton("08 • DOMAIN", callback_data="menu_domain"),
        InlineKeyboardButton("09 • IPTOOLS", callback_data="menu_iptools"),
        InlineKeyboardButton("10 • VPS STATUS", callback_data="menu_status"),
        InlineKeyboardButton("11 • NETGUARD", callback_data="menu_netguard"),
        InlineKeyboardButton("12 • PORT INFO", callback_data="menu_port"),
        InlineKeyboardButton("13 • CLEAN LOGS", callback_data="menu_log"),
        InlineKeyboardButton("👑 GESTION ADMINS", callback_data="menu_admins"),
        InlineKeyboardButton("🔄 REBOOT VPS", callback_data="action_reboot")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Accès refusé.")
        return
    bot.send_message(message.chat.id, "<b>🟢 NEXUS TUNNEL PRO - C2 SERVER</b>\nSélectionnez un module :", parse_mode="HTML", reply_markup=main_menu_keyboard())

# --- RETOUR À L'ACCUEIL ---
@bot.callback_query_handler(func=lambda call: call.data == "action_home")
def home_callback(call):
    if not is_admin(call.from_user.id): return
    bot.edit_message_text("<b>🟢 NEXUS TUNNEL PRO - C2 SERVER</b>\nSélectionnez un module :", 
                          chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          parse_mode="HTML", reply_markup=main_menu_keyboard())

# --- ROUTEUR DYNAMIQUE DES SOUS-MENUS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def module_routing(call):
    if not is_admin(call.from_user.id): return
    
    # Extraction du nom du module (ex: "menu_ssh" devient "SSH")
    module = call.data.split("_")[1].upper()
    
    markup = InlineKeyboardMarkup(row_width=1)
    # Boutons générés automatiquement selon le module cliqué
    markup.add(
        InlineKeyboardButton(f"➕ Créer compte {module}", callback_data=f"add_{module.lower()}"),
        InlineKeyboardButton(f"📋 Liste des comptes", callback_data=f"list_{module.lower()}"),
        InlineKeyboardButton("🔙 Retour Accueil", callback_data="action_home")
    )
    
    # MODIFICATION DU MESSAGE SANS EN CRÉER UN NOUVEAU
    bot.edit_message_text(f"<b>Module {module}</b>\nChoisissez une action :", 
                          chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          parse_mode="HTML", reply_markup=markup)


# --- LOGIQUE DE CRÉATION SSH (STATE MACHINE) ---
@bot.callback_query_handler(func=lambda call: call.data == "add_ssh")
def add_ssh_start(call):
    if not is_admin(call.from_user.id): return
    bot.edit_message_text("⚙️ Module SSH activé.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    msg = bot.send_message(call.message.chat.id, "👤 <b>Étape 1/3</b>
Entrez le nom d'utilisateur SSH :", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_ssh_user)

def process_ssh_user(message):
    user = message.text
    msg = bot.send_message(message.chat.id, "🔑 <b>Étape 2/3</b>
Entrez le mot de passe :", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_ssh_pass, user)

def process_ssh_pass(message, user):
    password = message.text
    msg = bot.send_message(message.chat.id, "⏳ <b>Étape 3/3</b>
Entrez la durée (en jours) :", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_ssh_days, user, password)

def process_ssh_days(message, user, password):
    days = message.text
    if not days.isdigit():
        bot.send_message(message.chat.id, "❌ Le nombre de jours doit être un entier. Annulation.", reply_markup=main_menu_keyboard())
        return

    bot.send_message(message.chat.id, f"⚙️ Déploiement du compte <b>{user}</b> au niveau du noyau...", parse_mode="HTML")
    
    import subprocess
    # Exécution silencieuse en contournant l'interface bash interactive
    cmd = f"useradd -e $(date -d '{days} days' +'%Y-%m-%d') -s /bin/false -M {user} && echo '{user}:{password}' | chpasswd"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if res.returncode == 0:
        success_msg = f"✅ <b>COMPTE SSH FORGÉ AVEC SUCCÈS</b>

👤 Username : <code>{user}</code>
🔑 Password : <code>{password}</code>
⏳ Validité : {days} Jours"
        bot.send_message(message.chat.id, success_msg, parse_mode="HTML", reply_markup=main_menu_keyboard())
    else:
        bot.send_message(message.chat.id, f"❌ Échec de la création :
<code>{res.stderr}</code>", parse_mode="HTML", reply_markup=main_menu_keyboard())


if __name__ == "__main__":
    bot.infinity_polling()
