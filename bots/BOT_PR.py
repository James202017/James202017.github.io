import logging
import asyncio
import sys
import os
from dotenv import load_dotenv

try:
    import ssl
except ModuleNotFoundError:
    ssl = None
    logging.error("Модуль SSL не найден. Проверьте наличие OpenSSL в вашей системе.")

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение значений из переменных окружения
API_TOKEN = os.getenv('BOT_TOKEN_PR')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

# Проверка наличия необходимых переменных окружения
if not API_TOKEN:
    raise ValueError("BOT_TOKEN_PR не найден в .env файле")

logging.basicConfig(level=logging.INFO)

# Проверка SSL перед запуском бота
if ssl is None:
    sys.exit("Ошибка: Модуль SSL недоступен. Установите OpenSSL или используйте среду с поддержкой SSL.")

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния опросника
class SaleForm(StatesGroup):
    property_type = State()
    location = State()
    details = State()
    price = State()
    photos = State()
    contact = State()

# Динамические клавиатуры для каждого этапа
def get_property_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🏠 Квартира"), KeyboardButton(text="🏡 Дом")],
        [KeyboardButton(text="🏖️ Дача"), KeyboardButton(text="🌳 Участок")],
        [KeyboardButton(text="🏢 Коммерческая недвижимость")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_location_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔙 Назад к выбору типа")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_details_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔙 Назад к локации")],
        [KeyboardButton(text="🔙 Назад к выбору типа")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_price_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="💰 До 3 млн"), KeyboardButton(text="💰 3-5 млн")],
        [KeyboardButton(text="💰 5-10 млн"), KeyboardButton(text="💰 Свыше 10 млн")],
        [KeyboardButton(text="🔙 Назад к деталям")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_photos_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="📷 Пропустить фото")],
        [KeyboardButton(text="🔙 Назад к бюджету")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_contact_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
        [KeyboardButton(text="🔙 Назад к фото")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

@dp.message(Command('start'))
async def start_handler(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'prodazha':
        welcome_msg = (
            f"🏠 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            "💼 <b>Профессиональная продажа недвижимости</b>\n\n"
            "🎯 <b>Наши преимущества:</b>\n"
            "• 📈 Максимальная цена за вашу недвижимость\n"
            "• ⚡ Быстрая продажа (в среднем 30 дней)\n"
            "• 🔍 Профессиональная оценка и маркетинг\n"
            "• 📋 Полное юридическое сопровождение\n"
            "• 💯 Гарантия безопасности сделки\n\n"
            "🏢 <b>Выберите тип недвижимости для продажи:</b>"
        )
    else:
        welcome_msg = (
            f"🏠 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            "💼 <b>Продажа недвижимости с экспертами</b>\n\n"
            "🎯 <b>Почему выбирают нас:</b>\n"
            "• 📈 Продаем по рыночной цене\n"
            "• ⚡ Быстрый поиск покупателей\n"
            "• 🔍 Профессиональная презентация объекта\n"
            "• 📋 Юридическая чистота сделки\n"
            "• 💯 Полная поддержка на всех этапах\n\n"
            "🏢 <b>Выберите тип недвижимости:</b>"
        )
    
    await message.answer(welcome_msg, reply_markup=get_property_keyboard())
    await state.set_state(SaleForm.property_type)

@dp.message(F.text.in_(["🔙 Назад к выбору типа", "🔙 Назад к локации", "🔙 Назад к деталям", "🔙 Назад к бюджету", "🔙 Назад к фото", "🔄 Начать заново", "📷 Пропустить фото"]))
async def navigation_handler(message: types.Message, state: FSMContext):
    if message.text == "🔄 Начать заново":
        await state.set_state(SaleForm.property_type)
        await message.answer(
            "🔄 <b>Начинаем заново!</b>\n\n🏠 <b>Выберите тип недвижимости для продажи:</b>",
            reply_markup=get_property_keyboard()
        )
    elif message.text == "🔙 Назад к выбору типа":
        await state.set_state(SaleForm.property_type)
        await message.answer(
            "🏠 <b>Выберите тип недвижимости для продажи:</b>",
            reply_markup=get_property_keyboard()
        )
    elif message.text == "🔙 Назад к локации":
        await state.set_state(SaleForm.location)
        await message.answer(
            "📍 <b>Укажите населенный пункт, район, адрес в развернутом формате:</b>",
            reply_markup=get_location_keyboard()
        )
    elif message.text == "🔙 Назад к деталям":
        await state.set_state(SaleForm.details)
        await message.answer(
            "📐 <b>Укажите детали недвижимости:</b>\n\n📏 Метраж\n🏠 Количество комнат\n🛠️ Состояние (ремонт)\n✨ Особенности и преимущества",
            reply_markup=get_details_keyboard()
        )
    elif message.text == "🔙 Назад к бюджету":
        await state.set_state(SaleForm.price)
        await message.answer(
            "💰 <b>Укажите желаемую цену:</b>\n\n💵 Цена или диапазон\n📊 Мы поможем определить оптимальную стоимость",
            reply_markup=get_price_keyboard()
        )
    elif message.text == "🔙 Назад к фото":
        await state.set_state(SaleForm.photos)
        await message.answer(
            "📸 <b>Пришлите фото недвижимости:</b>\n\n📷 Можно отправить несколько фотографий\n🏠 Покажите лучшие ракурсы объекта\n✨ Качественные фото = быстрая продажа!",
            reply_markup=get_photos_keyboard()
        )
    elif message.text == "📷 Пропустить фото":
        await state.update_data(photos="Фото не предоставлены")
        await state.set_state(SaleForm.contact)
        await message.answer(
            "📞 <b>Укажите контактные данные:</b>\n\n📱 Номер телефона\n👤 Ваше имя\n⏰ Удобное время для звонка",
            reply_markup=get_contact_keyboard()
        )

@dp.message(SaleForm.property_type)
async def process_type(message: types.Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await state.set_state(SaleForm.location)
    await message.answer(
        "📍 <b>Укажите населенный пункт, район, адрес в развернутом формате:</b>",
        reply_markup=get_location_keyboard()
    )

@dp.message(SaleForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(SaleForm.details)
    await message.answer(
        "📐 <b>Укажите детали недвижимости:</b>\n\n📏 Метраж\n🏠 Количество комнат\n🛠️ Состояние (ремонт)\n✨ Особенности и преимущества",
        reply_markup=get_details_keyboard()
    )

@dp.message(SaleForm.details)
async def process_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    await state.set_state(SaleForm.price)
    await message.answer(
        "💰 <b>Укажите желаемую цену:</b>\n\n💵 Цена или диапазон\n📊 Мы поможем определить оптимальную стоимость",
        reply_markup=get_price_keyboard()
    )

@dp.message(SaleForm.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(SaleForm.photos)
    await message.answer(
        "📸 <b>Пришлите фото недвижимости:</b>\n\n📷 Можно отправить несколько фотографий\n🏠 Покажите лучшие ракурсы объекта\n✨ Качественные фото = быстрая продажа!",
        reply_markup=get_photos_keyboard()
    )

@dp.message(SaleForm.photos)
async def process_photos(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id if message.photo else "Нет фото"
    await state.update_data(photos=photo_id)
    await state.set_state(SaleForm.contact)
    await message.answer(
        "📞 <b>Укажите контактные данные:</b>\n\n📱 Номер телефона\n👤 Ваше имя\n⏰ Удобное время для звонка",
        reply_markup=get_contact_keyboard()
    )

@dp.message(SaleForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    contact_info = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=contact_info)
    data = await state.get_data()

    # Отправляем данные в админский чат
    admin_message = f"""🏠 <b>Новая заявка на продажу недвижимости</b>

📋 <b>Тип недвижимости:</b> {data['property_type']}
📍 <b>Адрес:</b> {data['location']}
📐 <b>Детали:</b> {data['details']}
💰 <b>Цена:</b> {data['price']}
📸 <b>Фото:</b> {data['photos']}
📞 <b>Контакты:</b> {data['contact']}

👤 <b>От пользователя:</b> @{message.from_user.username or 'Без username'} (ID: {message.from_user.id})"""
    
    await bot.send_message(ADMIN_CHAT_ID, admin_message)
    await message.answer(
        "✅ <b>Превосходно! Ваша заявка успешно отправлена!</b>\n\n"
        "🎯 Наш эксперт по продажам свяжется с вами в течение часа\n"
        "📊 Проведем бесплатную оценку вашей недвижимости\n"
        "📋 Подготовим индивидуальный план продажи\n\n"
        "💼 <i>Спасибо за доверие! Продадим быстро и выгодно!</i>",
        reply_markup=get_property_keyboard()
    )
    await state.clear()

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
