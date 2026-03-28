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

if __name__ == "__main__":
    bot.infinity_polling()
