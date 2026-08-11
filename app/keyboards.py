from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from config import BOSS_IDS, ADMIN_IDS

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

def get_main_keyboard(user_id: int):
    buttons = [
        [KeyboardButton(text="✂️ Услуги"), KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="📋 Мои записи"), KeyboardButton(text="ℹ️ О нас")]
    ]
    if user_id in BOSS_IDS or user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="⚙️ Панель управления")])
        
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_boss_keyboard():
    buttons = [
        [KeyboardButton(text="➕ Добавить услугу"), KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

def get_services_inline_kb(services):
    keyboard = []
    for s in services:
        keyboard.append([InlineKeyboardButton(text=f"{s.title} — {s.price} ₸", callback_data=f"select_service:{s.id}")])
    keyboard.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_dates_inline_kb():
    keyboard = []
    today = datetime.now()
    for i in range(7):
        current_day = today + timedelta(days=i)
        date_str = current_day.strftime("%d.%m")
        weekday_str = WEEKDAYS[current_day.weekday()]
        keyboard.append([InlineKeyboardButton(text=f"📅 {date_str} ({weekday_str})", callback_data=f"select_date:{date_str}")])
        
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_services"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_times_inline_kb(selected_date, booked_times):
    working_hours = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    keyboard = []
    
    clean_booked = [str(b).strip() for b in booked_times]
    now = datetime.now()
    today_str = now.strftime("%d.%m")

    for time in working_hours:
        short_time = time.split(":")[0]
        check_full = f"{selected_date} в {time}"
        check_short = f"{selected_date} в {short_time}"
        
        # 1. Проверяем, не прошло ли уже это время на СОГОДНЯ
        is_past = False
        if selected_date == today_str:
            slot_hour = int(short_time)
            # Если текущий час уже больше или равен часу слота, скрываем его
            if now.hour >= slot_hour:
                is_past = True

        # 2. Формируем статус кнопки
        if check_full in clean_booked or check_short in clean_booked:
            text = f"🔒 {time} (Занято)"
            cd = "ignore"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=cd)])
        elif is_past:
            # Прошедшее время просто пропускаем (не добавляем в список кнопок)
            continue
        else:
            text = f"🕒 {time}"
            cd = f"select_time:{time}"
            keyboard.append([InlineKeyboardButton(text=text, callback_data=cd)])
        
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_dates"),
        InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_my_booking_cancel_kb(booking_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить запись", callback_data=f"ask_cancel:{booking_id}")]
    ])

def get_confirm_cancel_kb(booking_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, отменить", callback_data=f"confirm_cancel:{booking_id}"),
            InlineKeyboardButton(text="🚫 Отмена", callback_data="back_to_my_bookings")
        ]
    ])