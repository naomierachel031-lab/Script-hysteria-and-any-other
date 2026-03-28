import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import subprocess

# --- CHARGEMENT DE LA CONFIGURATION ---
CONFIG_FILE = '/etc/nexus_bot/config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config()
if not config:
    print("Erreur: Fichier config introuvable. Lancez l'installation depuis le menu Bash.")
    exit(1)

BOT_TOKEN = config.get('bot_token')
SUPER_ADMIN = int(config.get('super_admin'))
bot = telebot.TeleBot(BOT_TOKEN)

# --- FONCTION DE SÉCURITÉ ---
def is_admin(user_id):
    cfg = load_config()
    if user_id == SUPER_ADMIN:
        return True
    if user_id in cfg.get('admins', []):
        return True
    return False

# --- GÉNÉRATEUR DE MENU PRINCIPAL ---
def main_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton("🔐 SSH / OVPN", callback_data="menu_ssh")
    b2 = InlineKeyboardButton("⚡ VLESS", callback_data="menu_vless")
    b3 = InlineKeyboardButton("🚀 VMESS", callback_data="menu_vmess")
    b4 = InlineKeyboardButton("🛡️ TROJAN", callback_data="menu_trojan")
    b5 = InlineKeyboardButton("👑 GESTION ADMINS", callback_data="menu_admins")
    b6 = InlineKeyboardButton("📊 STATUT VPS", callback_data="menu_status")
    markup.add(b1, b2, b3, b4)
    markup.add(b5, b6)
    return markup

# --- COMMANDE /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Accès refusé. Vous n'êtes pas autorisé sur le système Nexus.")
        return
    
    welcome_text = (
        "<b>🟢 NEXUS TUNNEL PRO - C2 SERVER</b>\n"
        "<i>Système de commandement en ligne.</i>\n\n"
        "Sélectionnez un module ci-dessous :"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=main_menu_keyboard())

# --- GESTIONNAIRE DE BOUTONS (CALLBACKS) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Accès refusé.")
        return

    if call.data == "menu_ssh":
        # Sous-menu SSH (Exemple)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("➕ Créer un compte", callback_data="action_create_ssh"),
            InlineKeyboardButton("📋 Liste des comptes", callback_data="action_list_ssh"),
            InlineKeyboardButton("🔙 Retour Accueil", callback_data="action_home")
        )
        bot.edit_message_text("<b>Module SSH / OVPN</b>\nChoisissez une action :", 
                              chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              parse_mode="HTML", 
                              reply_markup=markup)
                              
    elif call.data == "action_home":
        bot.edit_message_text("<b>🟢 NEXUS TUNNEL PRO - C2 SERVER</b>\nSélectionnez un module :", 
                              chat_id=call.message.chat.id, 
                              message_id=call.message.message_id, 
                              parse_mode="HTML", 
                              reply_markup=main_menu_keyboard())

# Lancement perpétuel
if __name__ == "__main__":
    print("NEXUS BOT DÉMARRÉ...")
    bot.infinity_polling()
