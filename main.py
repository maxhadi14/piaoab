from config import Config 
import time
import telebot, re
from telebot import types
from datetime import datetime
from threading import Thread
from kvsqlite.sync import Client
 
bot = telebot.TeleBot(Config.TG_BOT_TOKEN, num_threads=90, skip_pending=True, parse_mode='html')
db = Client('data.sqlite')
c = -1001636427761
back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('⦅ رجوع ⦆', callback_data='back'))
logs = ['creator', 'member', 'administrator']
def force(user_id, channel):
  b = bot.get_chat_member(chat_id=c, user_id=user_id)
  if str(b.status) in logs:
    return True
  else:
    return False
def find_available_hours(timestamp):

    available_hours = [timestamp + (i * 3600) for i in range(0, 7)] 
    e = []
    for i in available_hours:
        t = int(i)
        tnow = datetime.fromtimestamp(t).strftime('%-I')
        d = db.get('worker')
        if d and str(d) == str(tnow):
            continue
        else:
            e.append(i)
    
    return e 

def handle_request(chat_id, link, text, selected_hour):

    user = bot.get_chat(c)
    if db.exists('lastid'):
        id = db.get('lastid')
        try:
            bot.delete_message(c, id)
        except: pass
    if db.exists('lastid_'):
        id = db.get('lastid_')
        try:
            bot.delete_message(c, id)
        except: pass
    
    z = bot.send_message(chat_id=c, text=f'{link}')
    z_ = bot.send_message(chat_id=c, text=text, reply_to_message_id=z.message_id)
    d = db.get('worker')
    if str(d) == str(selected_hour):
        db.delete('worker')
    user_info = db.get(str(chat_id))
    user_info['promotions']= []
    
    db.set(str(chat_id), user_info)
    db.set('lastid', z.message_id)
    db.set('lastid_', z_.message_id)
    bot.send_message(chat_id=chat_id, text=f"تم نشر تمويلك بنجاح!\nhttps://t.me/{user.username}/{z.message_id} .")
    return
def check_hour():
    while True:
        current_hour = datetime.fromtimestamp(time.time()).strftime('%-I')
        keys = db.keys()
        for key in keys:
            user_info = db.get(key[0])
            try:
                promotions = user_info['promotions'][-1]
            except:
                continue
            try:
                promotions = datetime.fromtimestamp(promotions).strftime('%-I')
            except: continue
            
            if promotions == current_hour:
                print(promotions, current_hour)
                link = user_info['link']
                text = user_info['text']
                handle_request(key[0], link, text, promotions)

       
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = str(message.from_user.id)
    keys = types.InlineKeyboardMarkup(row_width=2)
    btn1, btn2, btn3, btn4, btn5 = types.InlineKeyboardButton('⦅ طلب تمويل جديد ⦆', callback_data='newpromote'), types.InlineKeyboardButton('⦅ تمويلاتي ⦆', callback_data='mypromote'), types.InlineKeyboardButton('⦅ حسابك ⦆', callback_data='acc'), types.InlineKeyboardButton('⦅ شروط الاستخدام ⦆', callback_data='tos'), types.InlineKeyboardButton('⦅ لشراء تمويل ⦆', callback_data='pay')
    keys.add(btn1)
    keys.add(btn3, btn2)
    keys.add(btn4)
    keys.add(btn5)
    if re.findall('/start (.*)', message.text):
        join_user = message.from_user.id
        to_user = int(message.text.split("/start ")[1])
        if join_user == to_user:
            start(message)
        if not db.exists(f"{join_user}"):
            someinfo = db.get(f"{to_user}")
            if join_user in someinfo['users']:
                start(message)
                return
            else:
                dd = 175
                someinfo['users'].append(join_user)
                someinfo['coin'] = int(someinfo['coin'])  + dd
                info = {
                    'link': None,
                    'coin': 0,
                    'text': None,
                    'promotions': [],
                    'users': [],
                    'id': message.from_user.id
                }
                db.set(f'{join_user}', info)
                db.set(f'{to_user}', someinfo)
                bot.send_message(chat_id=to_user, text='فات شخص لرابط دعوتك، واخذت 175 أرصدة ..')
                start(message)
                
        else:
            start(message)
    try: 
        s = force(user_id=chat_id, channel=c)
    except:
        s = True
    if not s:
        i = bot.get_chat(c).username
        bot.reply_to(message, f'عذرا يجب عليك الاشتراك بقناة البوت:\n- @{i} .\n⎯ ⎯ ⎯ ⎯\nاشترك وأرسل [/start] ..')
        return
    if not db.exists(chat_id):   
        user_info = {
            'link': None,
            'coin': 0,
            'text': None,
            'promotions': [],
            'users': [],
            'id': message.from_user.id
        } 
        db.set(chat_id, user_info)
        bot.reply_to(message, '<strong>اهلا بك عزيزي،\nيمكنك طلب تمويلات من هذا البوت!</strong>\n- أقرء شروط الاستخدام قبل ان تقوم بالتمويل لضمان حقك!', reply_markup=keys)
        return
    else:
        bot.reply_to(message, '<strong>اهلا بك عزيزي،\nيمكنك طلب تمويلات من هذا البوت!</strong>\n- أقرء شروط الاستخدام قبل ان تقوم بالتمويل لضمان حقك!', reply_markup=keys)
        return
        

def set_link(message):
    chat_id = str(message.from_user.id)
    user_info = db.get(chat_id)
    if message.text:
        if message.text == '/start':
            user_info = {
            'link': None,
            'text': None,
            'promotions': [],
            'id': message.from_user.id
            } 
            db.set(chat_id, user_info)
            return start(message)
        user_info['link'] = message.text
        db.set(chat_id, user_info)
        bot.reply_to(message, 'حسناً، ارسل الوصف، او نص تعريفي عن مجموعتك!')
        bot.register_next_step_handler(message, set_text)

def set_text(message):
    chat_id = str(message.from_user.id)
    user_info = db.get(chat_id)
    if not message.text: return
    if message.text == '/start':
        user_info = {
        'link': None,
        'text': None,
        'promotions': [],
        'id': message.from_user.id
        } 
        db.set(chat_id, user_info)
        return start(message)
    user_info['text'] = message.text
    db.set(chat_id, user_info)

    timestamp = int(time.time())
    available_hours = find_available_hours(timestamp)

    if not available_hours:
        bot.send_message(chat_id, "لايوجد اوقات فارغة حالياً .", reply_markup=back)
        user_info = None
        return
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        for hour in (available_hours):
            formatted_hour = datetime.fromtimestamp(hour).strftime('%-I %p')
            callback_data = f"select_hour:{hour}"
            print(callback_data)
            button = types.InlineKeyboardButton(text=formatted_hour.replace('AM', 'صباحا').replace('PM', 'مساءا'), callback_data=callback_data)
            keyboard.add(button)
        keyboard.add(types.InlineKeyboardButton('⦅ الغاء العملية ⦆', callback_data='cancel'))
        bot.send_message(chat_id=chat_id, text='اختر وقت للتمويل.. ', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call:True)
def handler_calls(call):
    chat_id = str(call.from_user.id)

    try: 
        s = force(user_id=chat_id, channel=c)
    except:
        s = True
    if not s:
        i = bot.get_chat(c).username
        bot.edit_message_text(text=f'عذرا يجب عليك الاشتراك بقناة البوت:\n- @{i} .\n⎯ ⎯ ⎯ ⎯\nاشترك وأرسل [/start] ..', chat_id=chat_id, message_id=call.message.id)
        return
    if call.data == 'acc':
        link = None
        coin = db.get(chat_id)['coin']
        try:
            x = bot.get_me()
            username = x.username
            id = call.from_user.id
            link = f'https://t.me/{username}?start={id}'
        except: pass
        bot.edit_message_text(text=f'معلومات حسابك:\n- نقاطك: <strong>{coin}</strong> .\n- رابط الدعوه: <code>{link}</code> .\n~~~~~~~~~~~', chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        return
    if call.data == 'back':
        keys = types.InlineKeyboardMarkup(row_width=2)
        btn1, btn2, btn3, btn4, btn5 = types.InlineKeyboardButton('⦅ طلب تمويل جديد ⦆', callback_data='newpromote'), types.InlineKeyboardButton('⦅ تمويلاتي ⦆', callback_data='mypromote'), types.InlineKeyboardButton('⦅ حسابك ⦆', callback_data='acc'), types.InlineKeyboardButton('⦅ شروط الاستخدام ⦆', callback_data='tos'), types.InlineKeyboardButton('⦅ لشراء تمويل ⦆', callback_data='pay')
        keys.add(btn1)
        keys.add(btn3, btn2)
        keys.add(btn4)
        keys.add(btn5)
        bot.edit_message_text(text='<strong>اهلا بك عزيزي،\nيمكنك طلب تمويلات من هذا البوت!</strong>\n- أقرء شروط الاستخدام قبل ان تقوم بالتمويل لضمان حقك!',chat_id=chat_id, message_id=call.message.id, reply_markup=keys)
        return
    if call.data == 'pay':
        r = '''
-︙مرحبا اذا لم تستطع تجميع النقاط عن طريق رابط الدعوه.
-︙الحل ف الحل الوحيد هو شراء تمويل من المطور. 
-︙ملحوظه نحن غير مسؤولون عن اي عمليات بيع من اي شخص اخر.
-︙التواصل يمكنك التواصل مع المطور من هنا @UP_UO لشراء تمويل.
-︙اخيرا شكرا لكم علي ثقتكم بنا.
        '''
        bot.edit_message_text(text=r, chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        return    
    if call.data == 'back':
        keys = types.InlineKeyboardMarkup(row_width=2)
        btn1, btn2, btn3, btn4, btn5 = types.InlineKeyboardButton('⦅ طلب تمويل جديد ⦆', callback_data='newpromote'), types.InlineKeyboardButton('⦅ تمويلاتي ⦆', callback_data='mypromote'), types.InlineKeyboardButton('⦅ حسابك ⦆', callback_data='acc'), types.InlineKeyboardButton('⦅ شروط الاستخدام ⦆', callback_data='tos'), types.InlineKeyboardButton('⦅ لشراء تمويل ⦆', callback_data='pay')
        keys.add(btn1)
        keys.add(btn3, btn2)
        keys.add(btn4)
        keys.add(btn5)
        bot.edit_message_text(text='<strong>اهلا بك عزيزي،\nيمكنك طلب تمويلات من هذا البوت!</strong>\n- أقرء شروط الاستخدام قبل ان تقوم بالتمويل لضمان حقك!',chat_id=chat_id, message_id=call.message.id, reply_markup=keys)
        return
    if call.data == 'tos':
        r = '''
-︙عند اختيار احد الاوقات لا يمكن تغيير الوقت.
-︙المحتوى الاباحي ممنوع من النشر في كل انواعه. 
-︙في حال وضع رساله وصف غبيه سوف يتم حظرك.
-︙عند تغيير الرابط لايمكنك ارجاع اموالك.
-︙الروابط فقط المقبوله.
        '''
        bot.edit_message_text(text=r, chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        return
    if call.data == 'mypromote':
        dat = db.get(chat_id)
        if len(dat['promotions']) < 1:
            bot.edit_message_text('لم تقم بأنشاء تمويل، او تم انتهاء التمويلات. ', chat_id=chat_id, message_id=call.message.id, reply_markup=back)
            return
        last = dat
        t = dat['promotions'][-1]
        text, link, h = last['text'], last['link'], datetime.fromtimestamp(t).strftime('%-I %p' )
        bot.edit_message_text(text=f'<strong>التمويل الجاري:</strong>\n- الرابط: {link} .\nالوصف: <code>{text}</code> .\n- وقت النشر: <strong>{h}</strong> .\n~~~~~~~~~~', chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        return
    if call.data == 'cancel':
        user_info = {
            'link': None,
            'text': None,
            'promotions': [],
            'id': call.from_user.id
        }
        db.set(chat_id, user_info)
        bot.edit_message_text(text='تمت العمليه بنجاح ..',chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        return
    if call.data == 'newpromote':
        d = db.get(chat_id)
        if len(d['promotions']) >0:
            key = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('⦅ الغاء التمويل ⦆', callback_data='cancel'))
            bot.edit_message_text(text='عندك تمويل جاري من قبل ..\nتبي تلغيه؟', chat_id=chat_id, message_id=call.message.id, reply_markup=key)
            return
        if d['coin'] < 5000:
          return bot.edit_message_text(text='نقاطك لاتكفي، تحتاج <strong>(5000)</strong> نقطة على الاقل ..', chat_id=chat_id, message_id=call.message.id, reply_markup=back)
        x = bot.edit_message_text(text='الان، ارسل رابط قناتك.. \n( اي رابط خطأ مامسوؤلين عنه! )', chat_id=chat_id, message_id=call.message.id)
        bot.register_next_step_handler(x, set_link)
        
    if call.data.startswith('select_hour:'):
        selected_hour = int(call.data.split(':')[1])
        user_info = db.get(chat_id)
    
        
        user_info['promotions'] = [selected_hour]
        db.set('worker', str(datetime.fromtimestamp(selected_hour).strftime('%-I')))
        Thread(target=check_hour).start()
        user_info['coin'] -=5000
        db.set(chat_id, user_info)
        dt = datetime.fromtimestamp(selected_hour).strftime('%-I %p')
        bot.edit_message_text(text=f'قمت بأختيار وقت التمويل: <strong>{dt}</strong> .\n<strong>سوف يتم نشر اعلانك في الوقت نفسه ..</strong>', message_id=call.message.id, chat_id=call.message.chat.id, reply_markup=back)
        return
@bot.message_handler(commands=['cast'])
def castting(m):
    if m.from_user.id == 5583496580:
        x = bot.reply_to(m, 'ارسل الي تبي تسوي له اذاعه ?')
        bot.register_next_step_handler(x, cast)
        return
@bot.message_handler(['stats'])
def stat(m):
    k = db.keys()
    bot.reply_to(m, f'عدد الاعضاء: {len(k)} ..')
@bot.message_handler(regexp='/add (.*)')
def e(m):
    id, coin = m.text.split('/add')[1].split('_')
    if m.from_user.id == 5583496580:
        d = db.get(id)
        try:
            d['coin']+=int(coin)
        except: return
        db.set(id, d)
        bot.reply_to(m, f'تمت بنجاح -> {id} + {coin} .')
        return
def cast(m):
    text = m
    if text:
        users = db.keys()
        z = 0
        for user in users:
            try:
                id = db.get(user[0])['id']
                bot.copy_message(id, m.from_user.id, m.id)
                z+=1
                time.sleep(1)
            except: continue
        bot.reply_to(m, f'تم ارسال لـ{z} .')
        return
bot.infinity_polling()