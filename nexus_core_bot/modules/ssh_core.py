import subprocess

def create_ssh_account(user, password, days):
    cmd = f"useradd -e $(date -d '{days} days' +'%Y-%m-%d') -s /bin/false -M {user} && echo '{user}:{password}' | chpasswd"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        return True, f"✅ <b>COMPTE SSH CRÉÉ</b>\n\n👤 User: <code>{user}</code>\n🔑 Pass: <code>{password}</code>\n⏳ Jours: {days}"
    return False, f"❌ Échec:\n<code>{res.stderr}</code>"

def list_ssh_accounts():
    cmd = "awk -F: '($3 >= 1000 && $1 != \"nobody\") {print $1}' /etc/passwd"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    users = res.stdout.strip().split('\n')
    if not users or users == ['']: return "📋 Aucun compte SSH trouvé."
    
    msg = "📋 <b>LISTE DES COMPTES SSH:</b>\n\n"
    for u in users:
        exp_cmd = f"chage -l {u} | grep 'Account expires' | cut -d ':' -f 2"
        exp_date = subprocess.run(exp_cmd, shell=True, capture_output=True, text=True).stdout.strip()
        msg += f"👤 <code>{u}</code> - Expire: <i>{exp_date}</i>\n"
    return msg
