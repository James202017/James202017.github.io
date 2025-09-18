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
API_TOKEN = os.getenv('BOT_TOKEN_P')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '123456789')  # Значение по умолчанию

# Проверка наличия необходимых переменных окружения
if not API_TOKEN:
    raise ValueError("BOT_TOKEN_P не найден в .env файле")

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
    contact = State()

# Функции для создания динамических клавиатур
def get_property_keyboard():
    """Клавиатура выбора типа недвижимости"""
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🏠 Квартира"), KeyboardButton(text="🏡 Дом")],
        [KeyboardButton(text="🏖️ Дача"), KeyboardButton(text="🌳 Участок")],
        [KeyboardButton(text="🏢 Коммерческая недвижимость")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_location_keyboard():
    """Клавиатура для этапа указания локации"""
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔙 Назад к выбору типа")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_details_keyboard():
    """Клавиатура для этапа указания деталей"""
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔙 Назад к локации")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_price_keyboard():
    """Клавиатура для этапа указания бюджета"""
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="💰 До 3 млн"), KeyboardButton(text="💰 3-5 млн")],
        [KeyboardButton(text="💰 5-10 млн"), KeyboardButton(text="💰 Свыше 10 млн")],
        [KeyboardButton(text="🔙 Назад к деталям")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_contact_keyboard():
    """Клавиатура для этапа указания контактов"""
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
        [KeyboardButton(text="🔙 Назад к бюджету")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'pokupka':
        welcome_msg = (
            "🏠 <b>Отлично! Вы перешли из раздела покупки на сайте!</b>\n\n"
            "🎉 <b>Добро пожаловать в мир недвижимости!</b>\n\n"
            "💼 <b>Мы поможем найти недвижимость вашей мечты!</b>\n\n"
            "✨ <b>Наши преимущества:</b>\n"
            "🔍 Персональный подбор объектов\n"
            "💰 Лучшие цены на рынке\n"
            "📋 Полное юридическое сопровождение\n"
            "⚡ Быстрое оформление сделки\n"
            "🏆 Гарантия чистоты документов\n\n"
            "📝 Пожалуйста, заполняйте все поля внимательно и максимально подробно, "
            "чтобы наши <b>эксперты-консультанты</b> могли связаться с вами и предложить идеальные варианты! 🎯"
        )
    else:
        welcome_msg = (
            "🎉 <b>Добро пожаловать в мир недвижимости!</b>\n\n"
            "💼 <b>Мы поможем найти недвижимость вашей мечты!</b>\n\n"
            "✨ <b>Наши преимущества:</b>\n"
            "🔍 Персональный подбор объектов\n"
            "💰 Лучшие цены на рынке\n"
            "📋 Полное юридическое сопровождение\n"
            "⚡ Быстрое оформление сделки\n"
            "🏆 Гарантия чистоты документов\n\n"
            "📝 Пожалуйста, заполняйте все поля внимательно и максимально подробно, "
            "чтобы наши <b>эксперты-консультанты</b> могли связаться с вами и предложить идеальные варианты! 🎯"
        )
    
    await message.answer(welcome_msg)
    await message.answer(
        "🏠 <b>Выберите тип недвижимости, которую хотите приобрести:</b>", 
        reply_markup=get_property_keyboard()
    )
    await state.set_state(SaleForm.property_type)

@dp.message(F.text.in_(["🔙 Назад к выбору типа", "🔙 Назад к локации", "🔙 Назад к деталям", "🔙 Назад к бюджету", "🔄 Начать заново"]))
async def navigation_handler(message: types.Message, state: FSMContext):
    if message.text == "🔄 Начать заново":
        await state.set_state(SaleForm.property_type)
        await message.answer(
            "🔄 <b>Начинаем заново!</b>\n\n🏠 <b>Выберите тип недвижимости:</b>",
            reply_markup=get_property_keyboard()
        )
    elif message.text == "🔙 Назад к выбору типа":
        await state.set_state(SaleForm.property_type)
        await message.answer(
            "🏠 <b>Выберите тип недвижимости:</b>",
            reply_markup=get_property_keyboard()
        )
    elif message.text == "🔙 Назад к локации":
        await state.set_state(SaleForm.location)
        await message.answer(
            "📍 <b>Укажите населенный пункт, район, какие есть пожелания:</b>",
            reply_markup=get_location_keyboard()
        )
    elif message.text == "🔙 Назад к деталям":
        await state.set_state(SaleForm.details)
        await message.answer(
            "📐 <b>Укажите детали недвижимости:</b>\n\n📏 Метраж\n🏠 Количество комнат\n✨ Дополнительные пожелания",
            reply_markup=get_details_keyboard()
        )
    elif message.text == "🔙 Назад к бюджету":
        await state.set_state(SaleForm.price)
        await message.answer(
            "💰 <b>Укажите ваш бюджет:</b>\n\n💵 Выберите диапазон или укажите свою сумму:",
            reply_markup=get_price_keyboard()
        )

@dp.message(SaleForm.property_type)
async def process_type(message: types.Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await state.set_state(SaleForm.location)
    await message.answer(
        "📍 <b>Укажите населенный пункт, район, какие есть пожелания:</b>",
        reply_markup=get_location_keyboard()
    )

@dp.message(SaleForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(SaleForm.details)
    await message.answer(
        "📐 <b>Укажите детали недвижимости:</b>\n\n📏 Метраж\n🏠 Количество комнат\n✨ Дополнительные пожелания",
        reply_markup=get_details_keyboard()
    )

@dp.message(SaleForm.details)
async def process_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    await state.set_state(SaleForm.price)
    await message.answer(
        "💰 <b>Укажите ваш бюджет:</b>\n\n💵 Выберите диапазон или укажите свою сумму:",
        reply_markup=get_price_keyboard()
    )

@dp.message(SaleForm.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(SaleForm.contact)
    await message.answer(
        "📞 <b>Укажите ваши контактные данные:</b>\n\n📱 Телефон\n👤 Имя\n📧 Email (по желанию)",
        reply_markup=get_contact_keyboard()
    )

@dp.message(SaleForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    
    data = await state.get_data()
    
    # Отправляем данные в админский чат
    admin_message = f"""🏠 <b>Новая заявка на покупку недвижимости</b>

📋 <b>Тип недвижимости:</b> {data['property_type']}
📍 <b>Локация:</b> {data['location']}
📐 <b>Детали:</b> {data['details']}
💰 <b>Бюджет:</b> {data['price']}
📞 <b>Контакты:</b> {data['contact']}

👤 <b>От пользователя:</b> @{message.from_user.username or 'Без username'} (ID: {message.from_user.id})"""
    
    await bot.send_message(ADMIN_CHAT_ID, admin_message)
    
    await message.answer(
        "✅ <b>Спасибо! Ваша заявка принята.</b>\n\n📞 Наш менеджер свяжется с вами в ближайшее время.",
        reply_markup=get_property_keyboard()
    )
    await state.clear()

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
