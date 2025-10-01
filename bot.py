# -*- coding: utf-8 -*-
"""
TELEGRAM-БОТ САЛОНА КРАСОТЫ
Полная рабочая версия с административными командами
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3

# Проверка библиотеки
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
    print("✅ Библиотека telegram найдена")
except ImportError:
    print("❌ Установите: pip install python-telegram-bot==20.3")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ ВАШ ТОКЕН
BOT_TOKEN = "8215198856:AAFaeNBZnrKig1tU0VR74DoCTHdrXsRKV1U"

print("🤖 ЗАПУСК БОТА САЛОНА КРАСОТЫ")
print("🔑 Токен установлен")

# Список ID администраторов (замените на свои ID)
ADMIN_USER_IDS = [412594355, 987654321]  # Добавьте сюда ID администраторов

# Состояния
class UserState:
    MAIN_MENU = "main_menu"
    SELECTING_SERVICE = "selecting_service"
    AWAITING_NAME = "awaiting_name"
    AWAITING_PHONE = "awaiting_phone"
    ADMIN_SELECTING_DATE = "admin_selecting_date"

# Настройки салона
SERVICES = {
    "nails": {
        "name": "💅 Ногтевой сервис",
        "services": ["Маникюр - 1500₽", "Педикюр - 2000₽", "Гель-лак - 1200₽"],
        "duration": 90
    },
    "hair": {
        "name": "💇‍♀️ Парикмахерские услуги", 
        "services": ["Стрижка женская - 2500₽", "Окрашивание - 4500₽", "Укладка - 1500₽"],
        "duration": 120
    },
    "makeup": {
        "name": "💄 Перманентный макияж",
        "services": ["Брови - 8000₽", "Губы - 12000₽", "Веки - 10000₽"],
        "duration": 150
    }
}

MASTERS = {
    "nails": ["Анна Иванова", "Мария Петрова"],
    "hair": ["Елена Сидорова", "Ольга Козлова"],
    "makeup": ["Светлана Николаева"]
}

WORK_HOURS = list(range(9, 19))

SALON_INFO = {
    "name": "Салон красоты 'Элеганс'",
    "phone": "+7 (999) 123-45-67", 
    "address": "ул. Красоты, дом 10"
}

class Database:
    def __init__(self):
        self.init_db()
        print("💾 База данных готова")
    
    def init_db(self):
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                phone TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_type TEXT,
                master TEXT,
                appointment_date TEXT,
                appointment_time TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_user_registered(self, user_id: int) -> bool:
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def register_user(self, user_id: int, name: str, phone: str):
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO users (user_id, name, phone) VALUES (?, ?, ?)',
            (user_id, name, phone)
        )
        conn.commit()
        conn.close()
        print(f"👤 Зарегистрирован: {name}")
    
    def create_appointment(self, user_id: int, service_type: str, master: str, date: str, time: str):
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO appointments (user_id, service_type, master, appointment_date, appointment_time) VALUES (?, ?, ?, ?, ?)',
            (user_id, service_type, master, date, time)
        )
        conn.commit()
        conn.close()
        print(f"📅 Запись создана: {date} {time}")
    
    def get_user_appointments(self, user_id: int) -> List[Dict]:
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT service_type, master, appointment_date, appointment_time FROM appointments WHERE user_id = ? AND status = "active"',
            (user_id,)
        )
        appointments = cursor.fetchall()
        conn.close()
        
        result = []
        for apt in appointments:
            result.append({
                'service_type': apt[0],
                'master': apt[1],
                'date': apt[2],
                'time': apt[3]
            })
        return result
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """Получение всех записей на конкретную дату"""
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT a.*, u.name as user_name, u.phone 
               FROM appointments a 
               LEFT JOIN users u ON a.user_id = u.user_id 
               WHERE a.appointment_date = ? 
               ORDER BY a.appointment_time ASC''',
            (date,)
        )
        appointments = cursor.fetchall()
        conn.close()
        
        result = []
        for apt in appointments:
            result.append({
                'id': apt[0],
                'user_id': apt[1],
                'service_type': apt[2],
                'master': apt[3],
                'appointment_date': apt[4],
                'appointment_time': apt[5],
                'status': apt[6],
                'created_at': apt[7],
                'user_name': apt[8],
                'phone': apt[9]
            })
        return result
    
    def is_time_available(self, master: str, date: str, time: str) -> bool:
        conn = sqlite3.connect('salon_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM appointments WHERE master = ? AND appointment_date = ? AND appointment_time = ? AND status = "active"',
            (master, date, time)
        )
        result = cursor.fetchone()
        conn.close()
        return result is None

# Глобальные переменные
db = Database()
user_states = {}
user_data = {}

class SalonBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        print("⚙️ Обработчики настроены")
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("schedule", self.schedule_command))
        self.application.add_handler(CommandHandler("today", self.today_schedule))
        self.application.add_handler(CommandHandler("tomorrow", self.tomorrow_schedule))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "Гость"
        user_states[user_id] = UserState.MAIN_MENU
        
        print(f"👋 Пользователь: {username}")
        
        welcome_text = (
            f"👋 Добро пожаловать в {SALON_INFO['name']}, {username}!\n\n"
            f"🌟 Я помогу вам:\n"
            f"📅 Записаться на процедуру\n"
            f"📋 Узнать цены\n"
            f"👩‍💻 Познакомиться с мастерами\n\n"
            f"📍 {SALON_INFO['address']}\n"
            f"📞 {SALON_INFO['phone']}\n\n"
            f"Что вас интересует?"
        )
        
        # Проверяем, является ли пользователь администратором
        if user_id in ADMIN_USER_IDS:
            welcome_text += f"\n\n🔧 **Команды администратора:**\n"
            welcome_text += f"/schedule - расписание на дату\n"
            welcome_text += f"/today - расписание на сегодня\n"
            welcome_text += f"/tomorrow - расписание на завтра"
        
        keyboard = [
            [InlineKeyboardButton("📅 Записаться", callback_data="book")],
            [InlineKeyboardButton("📋 Услуги и цены", callback_data="services")],
            [InlineKeyboardButton("👩‍💻 Наши мастера", callback_data="masters")],
            [InlineKeyboardButton("🎯 Акции", callback_data="promotions")],
            [InlineKeyboardButton("📱 Мои записи", callback_data="my_bookings")]
        ]
        
        # Добавляем админ-кнопку если пользователь - администратор
        if user_id in ADMIN_USER_IDS:
            keyboard.append([InlineKeyboardButton("🔧 Расписание салона", callback_data="admin_schedule")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда для просмотра расписания на дату"""
        user_id = update.effective_user.id
        username = update.effective_user.first_name or "Администратор"
        
        # Проверка прав администратора
        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text(
                "❌ У вас нет прав для просмотра расписания.\n"
                "📞 Обратитесь к администратору салона."
            )
            return
        
        user_states[user_id] = UserState.ADMIN_SELECTING_DATE
        
        print(f"📋 Запрос расписания от: {username}")
        
        text = (
            f"📋 **Расписание салона**\n\n"
            f"👋 {username}, выберите дату для просмотра записей:\n\n"
            f"📅 Доступные даты:"
        )
        
        keyboard = await self.generate_date_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def today_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрая команда для просмотра сегодняшнего расписания"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ У вас нет прав для просмотра расписания.")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Создаем fake query объект для совместимости с существующим методом
        class FakeQuery:
            def __init__(self, message):
                self.message = message
            
            async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
                await self.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        
        fake_query = FakeQuery(update.message)
        await self.show_day_schedule(fake_query, today)
    
    async def tomorrow_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Быстрая команда для просмотра завтрашнего расписания"""
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ У вас нет прав для просмотра расписания.")
            return
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        class FakeQuery:
            def __init__(self, message):
                self.message = message
            
            async def edit_message_text(self, text, reply_markup=None, parse_mode=None):
                await self.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        
        fake_query = FakeQuery(update.message)
        await self.show_day_schedule(fake_query, tomorrow)
    
    async def generate_date_keyboard(self):
        """Генерация клавиатуры с датами"""
        keyboard = []
        today = datetime.now()
        
        for i in range(0, 8):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            if i == 0:
                date_display = f"📅 Сегодня ({date.strftime('%d.%m')})"
            elif i == 1:
                date_display = f"📅 Завтра ({date.strftime('%d.%m')})"
            else:
                date_display = date.strftime("%d.%m (%a)")
                days = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}
                for eng, rus in days.items():
                    date_display = date_display.replace(eng, rus)
            
            keyboard.append([InlineKeyboardButton(date_display, callback_data=f"admin_date_{date_str}")])
        
        keyboard.append([InlineKeyboardButton("📅 Показать еще", callback_data="admin_more_dates")])
        return keyboard
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        print(f"🔘 Нажата кнопка: {data}")
        
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
        elif data == "admin_schedule":
            await self.schedule_command_inline(query)
        elif data.startswith("admin_date_"):
            selected_date = data.replace("admin_date_", "")
            await self.show_day_schedule(query, selected_date)
        elif data == "admin_more_dates":
            await self.show_more_admin_dates(query)
        elif data == "admin_select_date":
            await self.schedule_command_inline(query)
        elif data.startswith("admin_stats_"):
            selected_date = data.replace("admin_stats_", "")
            await self.show_date_statistics(query, selected_date)
        elif data.startswith("service_"):
            await self.select_service(query, data)
        elif data.startswith("date_"):
            await self.select_date(query, data)
        elif data.startswith("time_"):
            await self.select_time(query, data)
        elif data == "back_to_menu":
            await self.back_to_main_menu(query)
    
    async def schedule_command_inline(self, query):
        """Команда расписания через inline кнопку"""
        user_id = query.from_user.id
        
        # Проверка прав администратора
        if user_id not in ADMIN_USER_IDS:
            await query.edit_message_text("❌ У вас нет прав для просмотра расписания.")
            return
            
        user_states[user_id] = UserState.ADMIN_SELECTING_DATE
        
        text = "📋 **Расписание салона**\n\n📅 Выберите дату:"
        
        keyboard = await self.generate_date_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_day_schedule(self, query, selected_date):
        """Показ расписания на выбранную дату"""
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            day_name = date_obj.strftime("%A")
            
            # Перевод дня недели
            days_ru = {
                'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда',
                'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'
            }
            day_name_ru = days_ru.get(day_name, day_name)
            
            # Получение записей на дату
            appointments = db.get_appointments_by_date(selected_date)
            
            text = f"📋 **Расписание на {formatted_date}**\n"
            text += f"📅 {day_name_ru}\n\n"
            
            if appointments:
                # Группировка по времени
                schedule_by_time = {}
                for apt in appointments:
                    time_key = apt['appointment_time']
                    if time_key not in schedule_by_time:
                        schedule_by_time[time_key] = []
                    schedule_by_time[time_key].append(apt)
                
                # Сортировка по времени
                sorted_times = sorted(schedule_by_time.keys())
                
                text += f"📊 **Всего записей: {len(appointments)}**\n\n"
                
                for time_slot in sorted_times:
                    text += f"🕐 **{time_slot}**\n"
                    for apt in schedule_by_time[time_slot]:
                        service_name = SERVICES.get(apt['service_type'], {}).get('name', apt['service_type'])
                        
                        # Получение имени клиента
                        client_name = apt.get('user_name', 'Неизвестный')
                        if not client_name or client_name == 'None':
                            client_name = f"ID: {apt['user_id']}"
                        
                        # Эмодзи для статуса
                        status_emoji = "✅" if apt['status'] == 'active' else "❌"
                        
                        text += f"   {status_emoji} {client_name}\n"
                        text += f"   👩‍💻 {apt['master']}\n"
                        text += f"   💅 {service_name}\n"
                        
                        # Показ телефона если есть
                        if apt.get('phone'):
                            text += f"   📞 {apt['phone']}\n"
                        
                        text += "\n"
                
                # Статистика по мастерам
                master_stats = {}
                for apt in appointments:
                    if apt['status'] == 'active':
                        master = apt['master']
                        master_stats[master] = master_stats.get(master, 0) + 1
                
                if master_stats:
                    text += "📈 **Загруженность мастеров:**\n"
                    for master, count in sorted(master_stats.items(), key=lambda x: x[1], reverse=True):
                        text += f"👩‍💻 {master}: {count} записей\n"
            else:
                text += "📭 **На эту дату записей нет**\n\n"
                text += "✨ Свободный день или записи еще не поступили"
            
            # Кнопки навигации
            keyboard = [
                [InlineKeyboardButton("📅 Другая дата", callback_data="admin_select_date")],
                [InlineKeyboardButton("📊 Статистика", callback_data=f"admin_stats_{selected_date}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            error_text = f"❌ Ошибка при получении расписания: {str(e)}"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_text, reply_markup=reply_markup)
    
    async def show_more_admin_dates(self, query):
        """Показ дополнительных дат для админа"""
        text = "📅 **Выберите дату:**"
        
        keyboard = []
        today = datetime.now()
        for i in range(8, 22):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            date_display = date.strftime("%d.%m (%a)")
            
            days = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}
            for eng, rus in days.items():
                date_display = date_display.replace(eng, rus)
            
            keyboard.append([InlineKeyboardButton(date_display, callback_data=f"admin_date_{date_str}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Первые даты", callback_data="admin_select_date")])
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_date_statistics(self, query, selected_date):
        """Показ статистики по дате"""
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            
            appointments = db.get_appointments_by_date(selected_date)
            
            text = f"📊 **Статистика на {formatted_date}**\n\n"
            
            if appointments:
                # Общая статистика
                active_count = len([apt for apt in appointments if apt['status'] == 'active'])
                cancelled_count = len([apt for apt in appointments if apt['status'] == 'cancelled'])
                
                text += f"📈 **Общая статистика:**\n"
                text += f"✅ Активных записей: {active_count}\n"
                text += f"❌ Отмененных записей: {cancelled_count}\n"
                text += f"📊 Всего записей: {len(appointments)}\n\n"
                
                # Статистика по услугам
                services_stats = {}
                for apt in appointments:
                    if apt['status'] == 'active':
                        service_type = apt['service_type']
                        service_name = SERVICES.get(service_type, {}).get('name', service_type)
                        services_stats[service_name] = services_stats.get(service_name, 0) + 1
                
                if services_stats:
                    text += f"💅 **По услугам:**\n"
                    for service, count in sorted(services_stats.items(), key=lambda x: x[1], reverse=True):
                        text += f"• {service}: {count}\n"
                    text += "\n"
                
                # Статистика по мастерам
                masters_stats = {}
                for apt in appointments:
                    if apt['status'] == 'active':
                        master = apt['master']
                        masters_stats[master] = masters_stats.get(master, 0) + 1
                
                if masters_stats:
                    text += f"👩‍💻 **По мастерам:**\n"
                    for master, count in sorted(masters_stats.items(), key=lambda x: x[1], reverse=True):
                        text += f"• {master}: {count} записей\n"
                    text += "\n"
                
                # Загруженность по времени
                time_stats = {}
                for apt in appointments:
                    if apt['status'] == 'active':
                        hour = apt['appointment_time'].split(':')[0]
                        time_stats[hour] = time_stats.get(hour, 0) + 1
                
                if time_stats:
                    text += f"🕐 **По времени:**\n"
                    for hour in sorted(time_stats.keys()):
                        text += f"• {hour}:00 - {time_stats[hour]} записей\n"
            else:
                text += "📭 На эту дату записей нет"
            
            keyboard = [
                [InlineKeyboardButton("📋 Расписание", callback_data=f"admin_date_{selected_date}")],
                [InlineKeyboardButton("📅 Другая дата", callback_data="admin_select_date")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            error_text = f"❌ Ошибка при получении статистики: {str(e)}"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_text, reply_markup=reply_markup)
    
    async def show_services(self, query):
        text = f"📋 **Услуги {SALON_INFO['name']}**\n\n"
        
        for service_info in SERVICES.values():
            text += f"**{service_info['name']}**\n"
            for service in service_info['services']:
                text += f"• {service}\n"
            text += f"⏱ {service_info['duration']} мин\n\n"
        
        text += f"📞 {SALON_INFO['phone']}\n"
        text += f"📍 {SALON_INFO['address']}"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def start_booking(self, query):
        user_id = query.from_user.id
        user_states[user_id] = UserState.SELECTING_SERVICE
        
        text = "📅 **Выберите услугу:**"
        
        keyboard = [
            [InlineKeyboardButton("💅 Ногтевой сервис", callback_data="service_nails")],
            [InlineKeyboardButton("💇‍♀️ Парикмахерские услуги", callback_data="service_hair")],
            [InlineKeyboardButton("💄 Перманентный макияж", callback_data="service_makeup")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def select_service(self, query, callback_data):
        user_id = query.from_user.id
        service_type = callback_data.replace("service_", "")
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['service_type'] = service_type
        
        service_info = SERVICES[service_type]
        text = f"**{service_info['name']}**\n\n"
        for service in service_info['services']:
            text += f"• {service}\n"
        text += f"\n⏱ {service_info['duration']} мин\n\n"
        
        # Генерация дат
        available_dates = []
        for i in range(1, 8):
            date = datetime.now() + timedelta(days=i)
            if date.weekday() < 6:  # Пн-Сб
                available_dates.append(date)
        
        if available_dates:
            text += "📅 **Выберите дату:**"
            keyboard = []
            for date in available_dates:
                date_str = date.strftime("%Y-%m-%d")
                date_display = date.strftime("%d.%m (%a)")
                days = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб'}
                for eng, rus in days.items():
                    date_display = date_display.replace(eng, rus)
                keyboard.append([InlineKeyboardButton(date_display, callback_data=f"date_{date_str}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="book")])
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            text += "❌ **Нет дат**"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def select_date(self, query, callback_data):
        user_id = query.from_user.id
        selected_date = callback_data.replace("date_", "")
        user_data[user_id]['date'] = selected_date
        
        service_type = user_data[user_id]['service_type']
        masters = MASTERS[service_type]
        
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d.%m.%Y")
        
        text = f"📅 **{formatted_date}**\n⏰ **Выберите время:**"
        
        keyboard = []
        for hour in WORK_HOURS:
            time_str = f"{hour:02d}:00"
            available = any(db.is_time_available(master, selected_date, time_str) for master in masters)
            if available:
                keyboard.append([InlineKeyboardButton(time_str, callback_data=f"time_{time_str}")])
        
        if keyboard:
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"service_{service_type}")])
        else:
            text += "\n❌ **Нет времени**"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data=f"service_{service_type}")]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def select_time(self, query, callback_data):
        user_id = query.from_user.id
        selected_time = callback_data.replace("time_", "")
        user_data[user_id]['time'] = selected_time
        
        if not db.is_user_registered(user_id):
            user_states[user_id] = UserState.AWAITING_NAME
            
            text = (
                f"📝 **Для записи нужна регистрация**\n\n"
                f"👤 Введите ваше имя:"
            )
            await query.edit_message_text(text, parse_mode='Markdown')
        else:
            await self.confirm_booking(query)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in user_states:
            await self.start_command(update, context)
            return
        
        state = user_states[user_id]
        
        if state == UserState.AWAITING_NAME:
            user_data[user_id]['name'] = text.strip()
            user_states[user_id] = UserState.AWAITING_PHONE
            
            await update.message.reply_text(f"👍 Приятно познакомиться, {text}!\n📞 Введите номер телефона:")
        
        elif state == UserState.AWAITING_PHONE:
            user_data[user_id]['phone'] = text.strip()
            
            db.register_user(user_id, user_data[user_id]['name'], user_data[user_id]['phone'])
            await self.complete_booking(update)
        
        # Обработка текстовых команд на русском языке
        elif text.lower() in ['расписание', 'график', 'записи']:
            # Создаем fake update для команды schedule
            class FakeUpdate:
                def __init__(self, original_update):
                    self.effective_user = original_update.effective_user
                    self.message = original_update.message
            
            fake_update = FakeUpdate(update)
            await self.schedule_command(fake_update, context)
    
    async def confirm_booking(self, query):
        user_id = query.from_user.id
        await self._finalize_booking(user_id, query)
    
    async def complete_booking(self, update):
        user_id = update.effective_user.id
        await self._finalize_booking(user_id, update)
        user_states[user_id] = UserState.MAIN_MENU
    
    async def _finalize_booking(self, user_id, update_or_query):
        service_type = user_data[user_id]['service_type']
        date = user_data[user_id]['date']
        time = user_data[user_id]['time']
        
        masters = MASTERS[service_type]
        available_master = None
        for master in masters:
            if db.is_time_available(master, date, time):
                available_master = master
                break
        
        if available_master:
            db.create_appointment(user_id, service_type, available_master, date, time)
            
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            
            text = (
                f"🎉 **ЗАПИСЬ ПОДТВЕРЖДЕНА!**\n\n"
                f"📅 Дата: {formatted_date}\n"
                f"⏰ Время: {time}\n"
                f"👩‍💻 Мастер: {available_master}\n"
                f"💅 Услуга: {SERVICES[service_type]['name']}\n\n"
                f"📍 {SALON_INFO['address']}\n"
                f"📞 {SALON_INFO['phone']}\n\n"
                f"✨ Ждем вас!"
            )
        else:
            text = "😔 Время занято. Выберите другое."
        
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update_or_query, 'edit_message_text'):
            await update_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update_or_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_masters(self, query):
        text = f"👩‍💻 **Мастера {SALON_INFO['name']}:**\n\n"
        
        for service_type, masters in MASTERS.items():
            service_name = SERVICES[service_type]['name']
            text += f"**{service_name}:**\n"
            for master in masters:
                text += f"• {master}\n"
            text += "\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_promotions(self, query):
        text = (
            f"🎯 **Акции {SALON_INFO['name']}:**\n\n"
            f"🌟 Скидка 20% на первое посещение\n"
            f"💅 Маникюр + педикюр = скидка 15%\n"
            f"👯‍♀️ Приведи подругу - скидка 10%\n"
            f"🎂 В день рождения - скидка 25%\n\n"
            f"📞 Подробности: {SALON_INFO['phone']}"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_user_bookings(self, query):
        user_id = query.from_user.id
        appointments = db.get_user_appointments(user_id)
        
        if appointments:
            text = "📱 **Ваши записи:**\n\n"
            for apt in appointments:
                service_name = SERVICES[apt['service_type']]['name']
                date_obj = datetime.strptime(apt['date'], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                
                text += f"• {service_name}\n"
                text += f"📅 {formatted_date} в {apt['time']}\n"
                text += f"👩‍💻 {apt['master']}\n\n"
            
            text += f"📞 Для изменения: {SALON_INFO['phone']}"
        else:
            text = "📱 У вас нет записей\n\n📅 Хотите записаться?"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def back_to_main_menu(self, query):
        user_id = query.from_user.id
        user_states[user_id] = UserState.MAIN_MENU
        
        text = f"🏠 **Главное меню {SALON_INFO['name']}**\n\nВыберите действие:"
        
        keyboard = [
            [InlineKeyboardButton("📅 Записаться", callback_data="book")],
            [InlineKeyboardButton("📋 Услуги и цены", callback_data="services")],
            [InlineKeyboardButton("👩‍💻 Наши мастера", callback_data="masters")],
            [InlineKeyboardButton("🎯 Акции", callback_data="promotions")],
            [InlineKeyboardButton("📱 Мои записи", callback_data="my_bookings")]
        ]
        
        # Добавляем админ-кнопку если пользователь - администратор
        if user_id in ADMIN_USER_IDS:
            keyboard.append([InlineKeyboardButton("🔧 Расписание салона", callback_data="admin_schedule")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def run(self):
        print("🤖 БОТ ЗАПУЩЕН!")
        print("📱 Проверьте в Telegram")
        print("🔄 Для остановки: Ctrl+C")
        print("🔧 Админ-команды:")
        print("   /schedule - расписание на дату")
        print("   /today - сегодняшнее расписание") 
        print("   /tomorrow - завтрашнее расписание")
        print("   Или напишите: 'расписание', 'график', 'записи'")
        self.application.run_polling()

def main():
    try:
        print("🎯 Инициализация...")
        bot = SalonBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    print("🚀 ЗАПУСК БОТА...")
    main()