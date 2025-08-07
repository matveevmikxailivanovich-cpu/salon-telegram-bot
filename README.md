import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Настройка логирования

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

# ВСТАВЬТЕ ВАШ ТОКЕН ЗДЕСЬ! 👇

BOT_TOKEN = “YOUR_BOT_TOKEN_HERE”

print(“🚀 Запуск салон-бота…”)
print(f”🔑 Токен: {‘✅ Установлен’ if BOT_TOKEN != ‘YOUR_BOT_TOKEN_HERE’ else ‘❌ НЕ УСТАНОВЛЕН!’}”)

# Состояния пользователя

class UserState:
MAIN_MENU = “main_menu”
SELECTING_SERVICE = “selecting_service”
SELECTING_TIME = “selecting_time”
AWAITING_NAME = “awaiting_name”
AWAITING_PHONE = “awaiting_phone”

# 💅 ДАННЫЕ САЛОНА (можно изменить на свои)

SERVICES = {
“nails”: {
“name”: “💅 Ногтевой сервис”,
“services”: [
“Маникюр классический - 1500₽”,
“Маникюр аппаратный - 2000₽”,
“Покрытие гель-лак - 1200₽”,
“Дизайн ногтей - 800₽”,
“Педикюр - 2500₽”
],
“duration”: 90
},
“hair”: {
“name”: “💇‍♀️ Парикмахерские услуги”,
“services”: [
“Стрижка женская - 2500₽”,
“Стрижка мужская - 1800₽”,
“Окрашивание - 4500₽”,
“Укладка - 1500₽”,
“Мелирование - 6000₽”,
“Химическая завивка - 3500₽”
],
“duration”: 120
},
“makeup”: {
“name”: “💄 Перманентный макияж”,
“services”: [
“Брови (пудровые) - 8000₽”,
“Брови (волосковые) - 9000₽”,
“Губы - 12000₽”,
“Веки (стрелки) - 10000₽”
],
“duration”: 150
}
}

# 👩‍💻 МАСТЕРА (измените на своих)

MASTERS = {
“nails”: [“Анна Иванова”, “Мария Петрова”, “Екатерина Смирнова”],
“hair”: [“Елена Сидорова”, “Ольга Козлова”, “Татьяна Волкова”],
“makeup”: [“Светлана Николаева”, “Виктория Морозова”]
}

# ⏰ РАБОЧИЕ ЧАСЫ

WORK_HOURS = list(range(9, 19))  # 9:00 - 18:00

# 📞 КОНТАКТЫ САЛОНА (измените на свои)

SALON_INFO = {
“name”: “Салон красоты ‘Элеганс’”,
“phone”: “+7 (999) 123-45-67”,
“address”: “ул. Красоты, дом 10”,
“work_time”: “Пн-Сб: 9:00-18:00, Вс: выходной”,
“instagram”: “@elegance_salon”
}

class Database:
def **init**(self):
self.init_db()
print(“💾 База данных инициализирована”)

```
def init_db(self):
    """Инициализация базы данных"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица записей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_type TEXT,
            master TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def is_user_registered(self, user_id: int) -> bool:
    """Проверка, зарегистрирован ли пользователь"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(self, user_id: int, name: str, phone: str):
    """Регистрация нового пользователя"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO users (user_id, name, phone) VALUES (?, ?, ?)',
        (user_id, name, phone)
    )
    conn.commit()
    conn.close()
    print(f"👤 Зарегистрирован пользователь: {name}")

def create_appointment(self, user_id: int, service_type: str, master: str, date: str, time: str):
    """Создание записи"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO appointments (user_id, service_type, master, appointment_date, appointment_time) VALUES (?, ?, ?, ?, ?)',
        (user_id, service_type, master, date, time)
    )
    conn.commit()
    conn.close()
    print(f"📅 Создана запись: {master} на {date} {time}")

def get_user_appointments(self, user_id: int) -> List[Dict]:
    """Получение записей пользователя"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, service_type, master, appointment_date, appointment_time 
           FROM appointments 
           WHERE user_id = ? AND status = "active" 
           ORDER BY appointment_date, appointment_time''',
        (user_id,)
    )
    appointments = cursor.fetchall()
    conn.close()
    
    result = []
    for apt in appointments:
        result.append({
            'id': apt[0],
            'service_type': apt[1],
            'master': apt[2],
            'date': apt[3],
            'time': apt[4]
        })
    return result

def is_time_available(self, master: str, date: str, time: str) -> bool:
    """Проверка доступности времени"""
    conn = sqlite3.connect('salon_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id FROM appointments 
           WHERE master = ? AND appointment_date = ? AND appointment_time = ? AND status = "active"''',
        (master, date, time)
    )
    result = cursor.fetchone()
    conn.close()
    return result is None
```

# Глобальные переменные

db = Database()
user_states = {}
user_data = {}

class SalonBot:
def **init**(self):
if BOT_TOKEN == ‘YOUR_BOT_TOKEN_HERE’:
print(“❌ ОШИБКА: Токен бота не установлен!”)
print(“📝 Откройте main.py и замените YOUR_BOT_TOKEN_HERE на ваш токен”)
raise ValueError(“Токен бота не настроен”)

```
    self.application = Application.builder().token(BOT_TOKEN).build()
    self.setup_handlers()
    print("⚙️ Обработчики команд настроены")

def setup_handlers(self):
    """Настройка обработчиков"""
    self.application.add_handler(CommandHandler("start", self.start_command))
    self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "Клиент"
    user_states[user_id] = UserState.MAIN_MENU
    
    print(f"👋 Новый пользователь: {username} (ID: {user_id})")
    
    welcome_text = (
        f"👋 Добро пожаловать в {SALON_INFO['name']}, {username}!\n\n"
        f"🌟 Я помогу вам:\n"
        f"• 📅 Записаться на процедуру\n"
        f"• 📋 Узнать цены на услуги\n"
        f"• 👩‍💻 Познакомиться с мастерами\n"
        f"• 🎯 Узнать об акциях\n\n"
        f"Что вас интересует?"
    )
    
    keyboard = [
        [InlineKeyboardButton("📅 Записаться на процедуру", callback_data="book")],
        [InlineKeyboardButton("📋 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton("👩‍💻 Наши мастера", callback_data="masters")],
        [InlineKeyboardButton("🎯 Акции и скидки", callback_data="promotions")],
        [InlineKeyboardButton("📱 Мои записи", callback_data="my_bookings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback кнопок"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    print(f"🔘 Пользователь {user_id} нажал: {data}")
    
    if data == "services":
        await self.show_services(query)
    elif data == "book":
        await self.start_booking(query)
    elif data == "masters":
        await self.show_masters(query)
    elif data == "promotions":
        await self.show_promotions(query)
    elif data == "my_bookings":
        await self.show_user_bookings(query)
    elif data.startswith("service_"):
        await self.select_service(query, data)
    elif data.startswith("date_"):
        await self.select_date(query, data)
    elif data.startswith("time_"):
        await self.select_time(query, data)
    elif data == "back_to_menu":
        await self.back_to_main_menu(query)

async def show_services(self, query):
    """Показать услуги и цены"""
    text = f"📋 **Услуги {SALON_INFO['name']}:**\n\n"
    
    for service_key, service_info in SERVICES.items():
        text += f"**{service_info['name']}**\n"
        for service in service_info['services']:
            text += f"• {service}\n"
        text += f"⏱ Продолжительность: {service_info['duration']} мин\n\n"
    
    text += f"📞 **Контакты:**\n"
    text += f"• Телефон: {SALON_INFO['phone']}\n"
    text += f"• Адрес: {SALON_INFO['address']}\n"
    text += f"• Время работы: {SALON_INFO['work_time']}\n"
    text += f"• Instagram: {SALON_INFO['instagram']}"
    
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def start_booking(self, query):
    """Начать процесс записи"""
    user_id = query.from_user.id
    user_states[user_id] = UserState.SELECTING_SERVICE
    
    text = "📅 **Запись на процедуру**\n\nВыберите тип услуги:"
    
    keyboard = [
        [InlineKeyboardButton("💅 Ногтевой сервис", callback_data="service_nails")],
        [InlineKeyboardButton("💇‍♀️ Парикмахерские услуги", callback_data="service_hair")],
        [InlineKeyboardButton("💄 Перманентный макияж", callback_data="service_makeup")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_service(self, query, callback_data):
    """Выбор услуги"""
    user_id = query.from_user.id
    service_type = callback_data.replace("service_", "")
    
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['service_type'] = service_type
    
    service_info = SERVICES[service_type]
    text = f"**{service_info['name']}**\n\n"
    text += "**Доступные услуги:**\n"
    for service in service_info['services']:
        text += f"• {service}\n"
    text += f"\n⏱ Время процедуры: {service_info['duration']} мин\n\n"
    text += "🔍 Проверяю свободное время..."
    
    # Генерируем доступные даты (исключаем воскресенье)
    available_dates = []
    for i in range(1, 15):  # 2 недели вперёд
        date = datetime.now() + timedelta(days=i)
        if date.weekday() < 6:  # Пн-Сб
            available_dates.append(date)
    
    if available_dates:
        text += "\n\n✅ **Есть свободные места!**\n📅 Выберите удобную дату:"
        
        keyboard = []
        # Показываем первые 7 дат
        for date in available_dates[:7]:
            date_str = date.strftime("%Y-%m-%d")
            date_display = date.strftime("%d.%m (%a)")
            # Переводим дни недели
            days_translate = {
                'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 
                'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб'
            }
            for eng, rus in days_translate.items():
                date_display = date_display.replace(eng, rus)
            
            keyboard.append([InlineKeyboardButton(date_display, callback_data=f"date_{date_str}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Выбрать другую услугу", callback_data="book")])
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        text += "\n\n❌ **Свободных мест нет**"
        keyboard = [[InlineKeyboardButton("🔄 Главное меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_date(self, query, callback_data):
    """Выбор даты"""
    user_id = query.from_user.id
    selected_date = callback_data.replace("date_", "")
    user_data[user_id]['date'] = selected_date
    
    service_type = user_data[user_id]['service_type']
    masters = MASTERS[service_type]
    
    # Форматируем дату
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d.%m.%Y (%A)")
    days_translate = {
        'Monday': 'понедельник', 'Tuesday': 'вторник', 'Wednesday': 'среда',
        'Thursday': 'четверг', 'Friday': 'пятница', 'Saturday': 'суббота'
    }
    for eng, rus in days_translate.items():
        formatted_date = formatted_date.replace(eng, rus)
    
    text = f"📅 **Дата:** {formatted_date}\n"
    text += f"💅 **Услуга:** {SERVICES[service_type]['name']}\n\n"
    text += "⏰ **Выберите время:**"
    
    keyboard = []
    available_count = 0
    
    # Проверяем доступность по времени
    for hour in WORK_HOURS:
        time_str = f"{hour:02d}:00"
        # Проверяем есть ли свободный мастер на это время
        available = any(db.is_time_available(master, selected_date, time_str) for master in masters)
        if available:
            keyboard.append([InlineKeyboardButton(f"🕐 {time_str}", callback_data=f"time_{time_str}")])
            available_count += 1
    
    if available_count > 0:
        text += f"\n\n✅ **Доступно {available_count} временных слотов**"
        keyboard.append([InlineKeyboardButton("🔙 Выбрать другую дату", callback_data=f"service_{service_type}")])
    else:
        text += "\n\n❌ **На эту дату все места заняты**"
        keyboard = [[InlineKeyboardButton("🔙 Выбрать другую дату", callback_data=f"service_{service_type}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_time(self, query, callback_data):
    """Выбор времени"""
    user_id = query.from_user.id
    selected_time = callback_data.replace("time_", "")
    user_data[user_id]['time'] = selected_time
    
    # Проверяем регистрацию пользователя
    if not db.is_user_registered(user_id):
        user_states[user_id] = UserState.AWAITING_NAME
        
        date_obj = datetime.strptime(user_data[user_id]['date'], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d.%m.%Y")
        
        text = (
            f"📝 **Почти готово!**\n\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {selected_time}\n"
            f"💅 Услуга: {SERVICES[user_data[user_id]['service_type']]['name']}\n\n"
            f"👤 **Для завершения записи введите ваше имя:**"
        )
        await query.edit_message_text(text, parse_mode='Markdown')
    else:
        await self.confirm_booking(query)

async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_states:
        await self.start_command(update, context)
        return
    
    state = user_states[user_id]
    print(f"📝 Пользователь {user_id} ввёл: {text} (состояние: {state})")
    
    if state == UserState.AWAITING_NAME:
        user_data[user_id]['name'] = text.strip()
        user_states[user_id] = UserState.AWAITING_PHONE
        
        await update.message.reply_text(
            f"👍 Приятно познакомиться, {text}!\n\n"
            f"📞 Теперь введите ваш номер телефона:"
        )
    
    elif state == UserState.AWAITING_PHONE:
        user_data[user_id]['phone'] = text.strip()
        
        # Регистрируем пользователя
        db.register_user(
            user_id, 
            user_data[user_id]['name'], 
            user_data[user_id]['phone']
        )
        
        await self.complete_booking(update)

async def confirm_booking(self, query):
    """Подтверждение записи для зарегистрированного пользователя"""
    user_id = query.from_user.id
    await self._finalize_booking(user_id, query)

async def complete_booking(self, update):
    """Завершение записи после регистрации"""
    user_id = update.effective_user.id
    await self._finalize_booking(user_id, update)
    user_states[user_id] = UserState.MAIN_MENU

async def _finalize_booking(self, user_id, update_or_query):
    """Финальное создание записи"""
    service_type = user_data[user_id]['service_type']
    date = user_data[user_id]['date']
    time = user_data[user_id]['time']
    
    # Найти свободного мастера
    masters = MASTERS[service_type]
    available_master = None
    for master in masters:
        if db.is_time_available(master, date, time):
            available_master = master
            break
    
    if available_master:
        # Создаём запись
        db.create_appointment(user_id, service_type, available_master, date, time)
        
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d.%m.%Y")
        
        text = (
            f"🎉 **ЗАПИСЬ ПОДТВЕРЖДЕНА!** 🎉\n\n"
            f"📋 **Детали записи:**\n"
            f"📅 Дата: {formatted_date}\n"
            f"⏰ Время: {time}\n"
            f"👩‍💻 Мастер: {available_master}\n"
            f"💅 Услуга: {SERVICES[service_type]['name']}\n"
            f"⏱ Длительность: {SERVICES[service_type]['duration']} мин\n\n"
            f"📍 **Адрес:** {SALON_INFO['address']}\n"
            f"📞 **Телефон:** {SALON_INFO['phone']}\n\n"
            f"💡 **Важно:**\n"
            f"• Приходите за 10 минут до времени записи\n"
            f"• За час придёт напоминание\n"
            f"• Для переноса/отмены звоните заранее\n\n"
            f"✨ Ждём вас в {SALON_INFO['name']}!"
        )
    else:
        text = (
            f"😔 **Извините!**\n\n"
            f"Это время уже занято другим клиентом.\n"
            f"Попробуйте выбрать другое время или дату."
        )
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update_or_query, 'edit_message_text'):
        await update_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update_or_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_masters(self, query):
    """Показать информацию о мастерах"""
    text = f"👩‍💻 **Мастера {SALON_INFO['name']}:**\n\n"
    
    for service_type, masters in MASTERS.items():
        service_name = SERVICES[service_type]['name']
        text += f"**{service_name}:**\n"
        for i, master in enumerate(masters, 1):
            text += f"{i}. {master}\n"
        text += "\n"
    
    text += "🌟 **О наших мастерах:**\n"
    text += "• Опыт работы от 3 лет\n"
    text += "• Регулярно проходят обучение\n" 
    text += "• Используют качественные материалы\n"
    text += "• Индивидуальный подход к каждому клиенту"
    
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_promotions(self, query):
    """Показать акции"""
    text = (
        f"🎯 **Акции {SALON_INFO['name']}:**\n\n"
        f"🌟 **НОВИНКА!** Скидка 25% на первое посещение\n"
        f"💅 **Комплекс:** Маникюр + педикюр = -20%\n"
        f"👯‍♀️ **Приведи подругу** и получи скидку 15%\n"
        f"🎂 **День рождения:** Скидка 30% в ваш день\n"
        f"💄 **Перманентный макияж:** 3-я процедура в подарок\n\n"
        f"🎁 **Специальное предложение этого месяца:**\n"
        f"Комплекс 'Преображение': стрижка + окрашивание + укладка\n"
        f"Вместо 8500₽ - всего 6000₽!\n\n"
        f"📞 **Подробности по телефону:**\n"
        f"{SALON_INFO['phone']}\n\n"
        f"⚠️ Акции не суммируются. Количество мест ограничено."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_user_bookings(self, query):
    """Показать записи пользователя"""
    user_id = query.from_user.id
    appointments = db.get_user_appointments(user_id)
    
    if appointments:
        text = "📱 **Ваши активные записи:**\n\n"
        for i, apt in enumerate(appointments, 1):
            service_name = SERVICES[apt['service_type']]['name']
            date_obj = datetime.strptime(apt['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            
            text += f"**{i}. {service_name}**\n"
            text += f"📅 {formatted_date} в {apt['time']}\n"
            text += f"👩‍💻 Мастер: {apt['master']}\n\n"
        
        text += f"📞 **Для изменения записи звоните:**\n{SALON_INFO['phone']}\n\n"
        text += "⚠️ Просим уведомлять об отмене минимум за 2 часа"
    else:
        text = (
            f"📱 **У вас пока нет активных записей**\n\n"
            f"📅 Хотите записаться на процедуру в {SALON_INFO['name']}?\n\n"
            f"У нас есть:\n"
            f"💅 Ногтевой серв
```