import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

TOKEN = "8714647008:AAFAOchFmETOjYmupuKUusmqWBXTpJjduHk"
ADMIN_ID = 1675494718

PROXY_URL = "http://200.10.31.45:8081"
DB_NAME = "barbershop.db"

session = AiohttpSession(proxy=PROXY_URL)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

def get_db_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            username TEXT,
            telegram_id INTEGER,
            phone TEXT,
            service TEXT,
            master TEXT,
            booking_date TEXT,
            booking_time TEXT,
            UNIQUE(master, booking_date, booking_time)
        )
    """)

    connection.commit()
    connection.close()


def get_busy_times(master, booking_date):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT booking_time
        FROM bookings
        WHERE master = ? AND booking_date = ?
    """, (master, booking_date))

    rows = cursor.fetchall()
    connection.close()

    return [row["booking_time"] for row in rows]


def save_booking(
    client_name,
    username,
    telegram_id,
    phone,
    service,
    master,
    booking_date,
    booking_time
):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO bookings (
                client_name,
                username,
                telegram_id,
                phone,
                service,
                master,
                booking_date,
                booking_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_name,
            username,
            telegram_id,
            phone,
            service,
            master,
            booking_date,
            booking_time
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


# ==================================================
# ДАННЫЕ БАРБЕРШОПА
# ==================================================

MAIN_MENU = [
    "✂️ Записаться",
    "👨‍🎨 Наши мастера",
    "ℹ️ О барбершопе"
]

SERVICES = [
    "✂️ Мужская стрижка",
    "🧔 Стрижка бороды",
    "🔥 Бритьё опасной бритвой",
    "💈 Fade / Фейд",
    "👦 Детская стрижка",
    "⚡ Комплекс: стрижка + борода",
    "🎨 Камуфляж седины",
    "🧴 Уход за бородой"
]

MASTERS = [
    "🧔 Артем",
    "👩 Мария",
    "👨 Дмитрий",
    "👩‍🦰 Елена",
    "👨‍🦱 Сергей",
    "🧔‍♂️ Никита",
    "👨‍🦲 Андрей"
]

VIEW_MASTERS = [
    "ℹ️ Артем",
    "ℹ️ Мария",
    "ℹ️ Дмитрий",
    "ℹ️ Елена",
    "ℹ️ Сергей",
    "ℹ️ Никита",
    "ℹ️ Андрей"
]

SERVICE_MASTERS = {
    "✂️ Мужская стрижка": [
        "🧔 Артем",
        "👨 Дмитрий",
        "👨‍🦱 Сергей",
        "🧔‍♂️ Никита"
    ],

    "🧔 Стрижка бороды": [
        "🧔 Артем",
        "👨 Дмитрий",
        "🧔‍♂️ Никита"
    ],

    "🔥 Бритьё опасной бритвой": [
        "👨 Дмитрий",
        "👨‍🦲 Андрей"
    ],

    "💈 Fade / Фейд": [
        "🧔 Артем",
        "👨‍🦱 Сергей",
        "🧔‍♂️ Никита"
    ],

    "👦 Детская стрижка": [
        "👩 Мария",
        "👩‍🦰 Елена",
        "👨‍🦱 Сергей"
    ],

    "⚡ Комплекс: стрижка + борода": [
        "🧔 Артем",
        "👨 Дмитрий",
        "🧔‍♂️ Никита"
    ],

    "🎨 Камуфляж седины": [
        "👩 Мария",
        "👩‍🦰 Елена"
    ],

    "🧴 Уход за бородой": [
        "🧔 Артем",
        "👨 Дмитрий",
        "👨‍🦲 Андрей"
    ]
}

DATES = [
    "📅 Сегодня",
    "📅 Завтра",
    "📅 Послезавтра"
]

TIMES = [
    "🕙 10:00",
    "🕛 12:00",
    "🕑 14:00",
    "🕓 16:00",
    "🕕 18:00"
]

MASTER_INFO = {
    "🧔 Артем": (
        "🧔 <b>Артем</b>\n\n"
        "✂️ <b>Специализация:</b> fade, мужские стрижки, оформление бороды\n"
        "📅 <b>Стаж:</b> 6 лет\n\n"
        "Артем — мастер современных мужских стилей. "
        "Идеально делает fade и аккуратно оформляет бороду."
    ),

    "👩 Мария": (
        "👩 <b>Мария</b>\n\n"
        "🎨 <b>Специализация:</b> модельные стрижки, укладки\n"
        "📅 <b>Стаж:</b> 8 лет\n\n"
        "Мария помогает создать аккуратный и стильный образ."
    ),

    "👨 Дмитрий": (
        "👨 <b>Дмитрий</b>\n\n"
        "💈 <b>Специализация:</b> классические мужские стрижки, бритьё\n"
        "📅 <b>Стаж:</b> 10 лет\n\n"
        "Дмитрий любит точность, аккуратные линии "
        "и классический мужской стиль."
    ),

    "👩‍🦰 Елена": (
        "👩‍🦰 <b>Елена</b>\n\n"
        "💇‍♀️ <b>Специализация:</b> уход за волосами, укладки\n"
        "📅 <b>Стаж:</b> 5 лет\n\n"
        "Елена помогает подчеркнуть индивидуальность клиента."
    ),

    "👨‍🦱 Сергей": (
        "👨‍🦱 <b>Сергей</b>\n\n"
        "💈 <b>Специализация:</b> fade, молодежные стрижки\n"
        "📅 <b>Стаж:</b> 4 года\n\n"
        "Сергей отлично разбирается в современных трендах."
    ),

    "🧔‍♂️ Никита": (
        "🧔‍♂️ <b>Никита</b>\n\n"
        "✂️ <b>Специализация:</b> борода, мужские стрижки\n"
        "📅 <b>Стаж:</b> 7 лет\n\n"
        "Никита специализируется на оформлении бороды "
        "и создании аккуратных мужских образов."
    ),

    "👨‍🦲 Андрей": (
        "👨‍🦲 <b>Андрей</b>\n\n"
        "🪒 <b>Специализация:</b> классическое бритьё\n"
        "📅 <b>Стаж:</b> 9 лет\n\n"
        "Андрей — мастер классического барберинга "
        "и бритья опасной бритвой."
    )
}


# ==================================================
# FSM СОСТОЯНИЯ
# ==================================================

class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()
    time = State()
    phone = State()


# ==================================================
# КЛАВИАТУРА
# ==================================================

def make_keyboard(items):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=item)] for item in items],
        resize_keyboard=True,
        input_field_placeholder="Выберите вариант..."
    )


# ==================================================
# /start
# ==================================================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "💈 <b>Добро пожаловать в BarberBeard!</b>\n\n"
        "Выберите нужный раздел:",
        reply_markup=make_keyboard(MAIN_MENU),
        parse_mode="HTML"
    )


# ==================================================
# ГЛАВНОЕ МЕНЮ
# ==================================================

@dp.message(F.text == "✂️ Записаться")
async def booking_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Booking.service)

    await message.answer(
        "✂️ <b>Онлайн-запись</b>\n\n"
        "Выберите услугу:",
        reply_markup=make_keyboard(SERVICES),
        parse_mode="HTML"
    )


@dp.message(F.text == "👨‍🎨 Наши мастера")
async def masters_menu(message: Message):
    await message.answer(
        "👨‍🎨 <b>Наши мастера</b>\n\n"
        "Выберите мастера:",
        reply_markup=make_keyboard(VIEW_MASTERS),
        parse_mode="HTML"
    )


@dp.message(F.text == "ℹ️ О барбершопе")
async def about_barbershop(message: Message):
    await message.answer(
        "💈 <b>BarberBeard</b>\n\n"
        "Современный барбершоп с опытными мастерами.\n"
        "Стрижки, борода, бритьё и стиль.\n\n"
        "🕙 Работаем ежедневно: 10:00 — 22:00",
        reply_markup=make_keyboard(MAIN_MENU),
        parse_mode="HTML"
    )


# ==================================================
# ПРОСМОТР ОПИСАНИЯ МАСТЕРОВ
# ==================================================

@dp.message(F.text.in_(VIEW_MASTERS))
async def show_master_info(message: Message):
    master_name = message.text.replace("ℹ️ ", "")

    full_master_name = None

    for master in MASTERS:
        if master_name in master:
            full_master_name = master
            break

    if full_master_name is None:
        await message.answer(
            "Не удалось найти информацию о мастере.",
            reply_markup=make_keyboard(MAIN_MENU)
        )
        return

    await message.answer(
        MASTER_INFO[full_master_name],
        parse_mode="HTML"
    )

    await message.answer(
        "Вы можете посмотреть другого мастера или перейти к записи.",
        reply_markup=make_keyboard(MAIN_MENU)
    )


# ==================================================
# ШАГ 1 — ВЫБОР УСЛУГИ
# ==================================================

@dp.message(Booking.service)
async def choose_service(message: Message, state: FSMContext):
    if message.text not in SERVICES:
        await message.answer(
            "⚠️ Выберите услугу кнопкой ниже.",
            reply_markup=make_keyboard(SERVICES)
        )
        return

    await state.update_data(service=message.text)

    available_masters = SERVICE_MASTERS[message.text]

    await state.update_data(available_masters=available_masters)
    await state.set_state(Booking.master)

    await message.answer(
        f"✨ Вы выбрали:\n<b>{message.text}</b>\n\n"
        "👨‍🎨 Доступные мастера:",
        reply_markup=make_keyboard(available_masters),
        parse_mode="HTML"
    )


# ==================================================
# ШАГ 2 — ВЫБОР МАСТЕРА
# ==================================================

@dp.message(Booking.master)
async def choose_master(message: Message, state: FSMContext):
    data = await state.get_data()
    available_masters = data["available_masters"]

    if message.text not in available_masters:
        await message.answer(
            "⚠️ Выберите мастера кнопкой ниже.",
            reply_markup=make_keyboard(available_masters)
        )
        return

    await state.update_data(master=message.text)
    await state.set_state(Booking.date)

    await message.answer(
        f"👨‍🎨 Мастер:\n<b>{message.text}</b>\n\n"
        "📅 Выберите дату:",
        reply_markup=make_keyboard(DATES),
        parse_mode="HTML"
    )


# ==================================================
# ШАГ 3 — ВЫБОР ДАТЫ
# ==================================================

@dp.message(Booking.date)
async def choose_date(message: Message, state: FSMContext):
    if message.text not in DATES:
        await message.answer(
            "⚠️ Выберите дату кнопкой ниже.",
            reply_markup=make_keyboard(DATES)
        )
        return

    await state.update_data(date=message.text)

    data = await state.get_data()
    selected_master = data["master"]
    selected_date = message.text

    busy_times = get_busy_times(selected_master, selected_date)

    free_times = []

    for time in TIMES:
        if time not in busy_times:
            free_times.append(time)

    if not free_times:
        await message.answer(
            "❌ На выбранную дату у этого мастера нет свободного времени.\n\n"
            "Выберите другую дату.",
            reply_markup=make_keyboard(DATES)
        )
        return

    await state.update_data(free_times=free_times)
    await state.set_state(Booking.time)

    await message.answer(
        "🕒 Выберите свободное время:",
        reply_markup=make_keyboard(free_times)
    )


# ==================================================
# ШАГ 4 — ВЫБОР ВРЕМЕНИ
# ==================================================

@dp.message(Booking.time)
async def choose_time(message: Message, state: FSMContext):
    data = await state.get_data()
    free_times = data["free_times"]

    if message.text not in free_times:
        await message.answer(
            "⚠️ Выберите свободное время кнопкой ниже.",
            reply_markup=make_keyboard(free_times)
        )
        return

    await state.update_data(time=message.text)
    await state.set_state(Booking.phone)

    await message.answer(
        "📞 Введите ваш номер телефона:",
        reply_markup=ReplyKeyboardRemove()
    )


# ==================================================
# ШАГ 5 — СОХРАНЕНИЕ ЗАПИСИ
# ==================================================

@dp.message(Booking.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)

    data = await state.get_data()

    booking_saved = save_booking(
        client_name=message.from_user.full_name,
        username=message.from_user.username,
        telegram_id=message.from_user.id,
        phone=message.text,
        service=data["service"],
        master=data["master"],
        booking_date=data["date"],
        booking_time=data["time"]
    )

    if not booking_saved:
        await message.answer(
            "❌ Это время только что заняли.\n\n"
            "Пожалуйста, начните запись заново.",
            reply_markup=make_keyboard(MAIN_MENU)
        )
        await state.clear()
        return

    username_text = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "не указан"
    )

    user_text = (
        "✅ <b>Запись успешно оформлена!</b>\n\n"
        "━━━━━━━━━━━━━━━\n"
        f"💎 <b>Услуга:</b> {data['service']}\n"
        f"👨‍🎨 <b>Мастер:</b> {data['master']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"🕒 <b>Время:</b> {data['time']}\n"
        f"📞 <b>Телефон:</b> {message.text}\n"
        "━━━━━━━━━━━━━━━\n\n"
        "Спасибо за запись! 💈"
    )

    admin_text = (
        "📩 <b>Новая запись!</b>\n\n"
        "━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клиент:</b> {message.from_user.full_name}\n"
        f"🔗 <b>Username:</b> {username_text}\n"
        f"🆔 <b>Telegram ID:</b> {message.from_user.id}\n\n"
        f"💎 <b>Услуга:</b> {data['service']}\n"
        f"👨‍🎨 <b>Мастер:</b> {data['master']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"🕒 <b>Время:</b> {data['time']}\n"
        f"📞 <b>Телефон:</b> {message.text}\n"
        "━━━━━━━━━━━━━━━"
    )

    await message.answer(
        user_text,
        reply_markup=make_keyboard(MAIN_MENU),
        parse_mode="HTML"
    )

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode="HTML"
    )

    await state.clear()


# ==================================================
# НЕИЗВЕСТНОЕ СООБЩЕНИЕ
# ==================================================

@dp.message()
async def unknown_message(message: Message):
    await message.answer(
        "Я не понял команду.\n\n"
        "Выберите действие из меню:",
        reply_markup=make_keyboard(MAIN_MENU)
    )


# ==================================================
# ЗАПУСК
# ==================================================

async def main():
    create_tables()
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())