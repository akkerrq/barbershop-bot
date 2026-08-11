from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOSS_IDS, ADMIN_IDS
from app.database.requests import (
    get_services, 
    get_service_by_id,
    add_booking, 
    get_all_bookings, 
    get_booked_times,
    add_service,
    get_user_bookings,
    delete_booking_by_id
)
from app.keyboards import (
    get_main_keyboard, 
    get_boss_keyboard, 
    get_admin_keyboard, 
    get_cancel_keyboard,
    get_phone_keyboard,
    get_services_inline_kb,
    get_dates_inline_kb,
    get_times_inline_kb,
    get_my_booking_cancel_kb,
    get_confirm_cancel_kb
)

router = Router()

class BookingState(StatesGroup):
    service = State()
    date = State()
    time = State()
    name = State()
    phone = State()

class AddServiceState(StatesGroup):
    title = State()
    description = State()
    price = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = get_main_keyboard(message.from_user.id)
    await message.answer("Добро пожаловать в барбершоп! Выберите действие ниже:", reply_markup=kb)

@router.message(F.text == "ℹ️ О нас")
async def about_us(message: Message):
    text = (
        "💈 <b>Барбершоп TOP CUTS</b>\n\n"
        "📍 <b>Адрес:</b> г. Алматы, пр. Абая, 150\n"
        "⏰ <b>Режим работы:</b> Ежедневно с 12:00 до 21:00\n"
        "📞 <b>Телефон:</b> +7 (777) 244-12-40\n"
        "🌐 <b>Instagram:</b> @topcuts_almaty\n\n"
        "Мы создаём правильный стиль и делаем лучший уход за вашей бородой!"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "✂️ Услуги")
async def show_services(message: Message):
    services = await get_services()
    if not services:
        await message.answer("Список услуг пока пуст.")
        return
        
    text = "✂️ <b>ПРАЙС-ЛИСТ НАШИХ УСЛУГ:</b>\n\n"
    for s in services:
        text += f"🔹 <b>{s.title}</b> — {s.price} ₸\n<i>{s.description}</i>\n\n"
    text += "Нажмите 📅 <b>Записаться</b> в меню ниже, чтобы выбрать время!"
    await message.answer(text, parse_mode="HTML")

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    user_id = message.from_user.id
    if user_id in BOSS_IDS:
        await message.answer("🔑 Вы авторизовались как Босс!", reply_markup=get_boss_keyboard())
    elif user_id in ADMIN_IDS:
        await message.answer("🔑 Вы авторизовались как Администратор!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("❌ У вас нет доступа к командам администратора.")

@router.message(F.text == "⚙️ Панель управления")
async def open_panel(message: Message):
    user_id = message.from_user.id
    if user_id in BOSS_IDS:
        await message.answer("⚙️ Меню управления:", reply_markup=get_boss_keyboard())
    elif user_id in ADMIN_IDS:
        await message.answer("⚙️ Панель администратора:", reply_markup=get_admin_keyboard())

@router.message(F.text == "🏠 Главное меню")
@router.message(F.text == "❌ Отмена")
async def go_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    kb = get_main_keyboard(message.from_user.id)
    await message.answer("Вы вернулись в главное меню.", reply_markup=kb)

# --- Расписание для администратора с разбивкой по дням ---

@router.message(F.text == "📅 Расписание")
async def view_bookings(message: Message):
    user_id = message.from_user.id
    if user_id not in BOSS_IDS and user_id not in ADMIN_IDS:
        await message.answer("❌ Эта функция доступна только администратору.")
        return
        
    bookings = await get_all_bookings()
    if not bookings:
        await message.answer("📋 Список всех записей пуст.")
        return
    
    grouped = {}
    for b in bookings:
        date_part = b.booking_date.split(" в ")[0] if " в " in b.booking_date else b.booking_date
        if date_part not in grouped:
            grouped[date_part] = []
        grouped[date_part].append(b)

    text = "📋 <b>РАСПИСАНИЕ ЗАПИСЕЙ:</b>\n\n"
    for date, items in grouped.items():
        text += f"📅 <b>═════ [ {date} ] ═════</b>\n\n"
        for b in items:
            text += (
                f"🔹 <b>Запись #{b.id}</b>\n"
                f"👤 <b>Клиент:</b> {b.name}\n"
                f"📞 <b>Тел:</b> {b.phone}\n"
                f"✂️ <b>Услуга:</b> {b.service_name}\n"
                f"⏰ <b>Время:</b> {b.booking_date}\n"
                "-----------------------------------\n"
            )
        text += "\n"

    await message.answer(text, parse_mode="HTML")

# --- Мои записи для клиента ---

@router.message(F.text == "📋 Мои записи")
async def show_my_bookings(message: Message):
    bookings = await get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет активных записей.")
        return

    now = datetime.now()
    has_active = False

    for b in bookings:
        try:
            date_str, time_str = b.booking_date.split(" в ")
            day, month = map(int, date_str.split("."))
            hour, minute = map(int, time_str.split(":"))
            booking_dt = datetime(now.year, month, day, hour, minute)

            if booking_dt < now:
                await delete_booking_by_id(b.id)
                continue
        except Exception:
            pass

        has_active = True
        text = (
            f"📌 <b>Запись #{b.id}</b>\n"
            f"✂️ <b>Услуга:</b> {b.service_name}\n"
            f"📅 <b>Дата и время:</b> {b.booking_date}\n"
        )
        await message.answer(text, reply_markup=get_my_booking_cancel_kb(b.id), parse_mode="HTML")

    if not has_active:
        await message.answer("У вас нет активных записей.")

@router.callback_query(F.data.startswith("ask_cancel:"))
async def ask_cancel_booking(call: CallbackQuery):
    booking_id = int(call.data.split(":")[1])
    await call.answer(
        text="⚠️ Подтвердите отмену записи снизу под сообщением!", 
        show_alert=True
    )
    await call.message.edit_reply_markup(reply_markup=get_confirm_cancel_kb(booking_id))

@router.callback_query(F.data.startswith("confirm_cancel:"))
async def confirm_cancel_booking(call: CallbackQuery):
    booking_id = int(call.data.split(":")[1])
    await delete_booking_by_id(booking_id)
    await call.answer("✅ Запись отменена!", show_alert=True)
    await call.message.edit_text("❌ <i>Эта запись была отменена.</i>", parse_mode="HTML")

@router.callback_query(F.data == "back_to_my_bookings")
async def back_to_my_bookings_callback(call: CallbackQuery):
    await call.answer()
    booking_id = int(call.message.text.split("#")[1].split("\n")[0])
    await call.message.edit_reply_markup(reply_markup=get_my_booking_cancel_kb(booking_id))

# --- Пошаговая инлайн-запись ---

@router.message(F.text == "📅 Записаться")
async def start_booking(message: Message, state: FSMContext):
    services = await get_services()
    if not services:
        await message.answer("Список услуг пока пуст.")
        return
    
    await state.set_state(BookingState.service)
    await message.answer("Выберите услугу:", reply_markup=get_services_inline_kb(services))

@router.callback_query(F.data.startswith("select_service:"))
async def process_service_choice(call: CallbackQuery, state: FSMContext):
    service_id = int(call.data.split(":")[1])
    service = await get_service_by_id(service_id)
    
    await state.update_data(service_name=f"{service.title} ({service.price} ₸)")
    await state.set_state(BookingState.date)
    
    await call.message.edit_text("Выберите желаемую дату:", reply_markup=get_dates_inline_kb())
    await call.answer()

@router.callback_query(F.data.startswith("select_date:"))
async def process_date_choice(call: CallbackQuery, state: FSMContext):
    selected_date = call.data.split(":")[1]
    await state.update_data(selected_date=selected_date)
    await state.set_state(BookingState.time)
    
    booked_times = await get_booked_times()
    await call.message.edit_text(
        f"Выберите время на <b>{selected_date}</b>:", 
        reply_markup=get_times_inline_kb(selected_date, booked_times),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "ignore")
async def process_ignore(call: CallbackQuery):
    await call.answer("🔒 Это время уже занято, выберите другое!", show_alert=True)

@router.callback_query(F.data.startswith("select_time:"))
async def process_time_choice(call: CallbackQuery, state: FSMContext):
    selected_time = call.data.split(":")[1]
    data = await state.get_data()
    
    formatted_time = selected_time if ":" in selected_time else f"{selected_time}:00"
    full_date = f"{data['selected_date']} в {formatted_time}"
    
    await state.update_data(booking_date=full_date)
    await state.set_state(BookingState.name)
    
    await call.message.delete()
    await call.message.answer(
        f"Вы выбрали: <b>{data['service_name']}</b> на <b>{full_date}</b>\n\nВведите ваше Имя:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()

# --- Кнопки Назад / Главное меню в инлайне ---

@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    kb = get_main_keyboard(call.from_user.id)
    await call.message.answer("Вы вернулись в главное меню.", reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "back_to_services")
async def back_to_services_callback(call: CallbackQuery, state: FSMContext):
    services = await get_services()
    await state.set_state(BookingState.service)
    await call.message.edit_text("Выберите услугу:", reply_markup=get_services_inline_kb(services))
    await call.answer()

@router.callback_query(F.data == "back_to_dates")
async def back_to_dates_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(BookingState.date)
    await call.message.edit_text("Выберите желаемую дату:", reply_markup=get_dates_inline_kb())
    await call.answer()

# --- Завершение записи ---

@router.message(BookingState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookingState.phone)
    await message.answer(
        "Нажмите кнопку ниже, чтобы поделиться контактом, или введите номер вручную:",
        reply_markup=get_phone_keyboard()
    )

@router.message(BookingState.phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    data = await state.get_data()
    
    await add_booking(
        user_id=message.from_user.id,
        name=data['name'],
        phone=phone,
        service_name=data['service_name'],
        booking_date=data['booking_date']
    )
    
    text_client = (
        "🎉 <b>Запись успешно оформлена!</b>\n\n"
        f"📌 <b>Услуга:</b> {data['service_name']}\n"
        f"📅 <b>Время:</b> {data['booking_date']}\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"📞 <b>Телефон:</b> {phone}\n\n"
        "Ждём вас в назначенное время!"
    )
    kb = get_main_keyboard(message.from_user.id)
    await message.answer(text_client, reply_markup=kb, parse_mode="HTML")
    
    text_admin = (
        "🔔 <b>НОВАЯ ЗАПИСЬ!</b>\n\n"
        f"👤 <b>Клиент:</b> {data['name']}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"✂️ <b>Услуга:</b> {data['service_name']}\n"
        f"📅 <b>Дата и время:</b> {data['booking_date']}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text_admin, parse_mode="HTML")
        except Exception:
            pass

    await state.clear()

# --- Добавление услуги ---

@router.message(F.text == "➕ Добавить услугу")
async def start_add_service(message: Message, state: FSMContext):
    if message.from_user.id not in BOSS_IDS:
        await message.answer("❌ Эта функция доступна только боссу.")
        return
    await state.set_state(AddServiceState.title)
    await message.answer("Введите название новой услуги:", reply_markup=get_cancel_keyboard())

@router.message(AddServiceState.title)
async def add_service_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddServiceState.description)
    await message.answer("Введите описание услуги:", reply_markup=get_cancel_keyboard())

@router.message(AddServiceState.description)
async def add_service_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddServiceState.price)
    await message.answer("Введите стоимость услуги (числом):", reply_markup=get_cancel_keyboard())

@router.message(AddServiceState.price)
async def add_service_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите стоимость только цифрами.")
        return
    data = await state.get_data()
    await add_service(data['title'], data['description'], int(message.text))
    await state.clear()
    await message.answer("✅ Услуга успешно добавлена!", reply_markup=get_boss_keyboard())