import logging
import asyncio
import os
import sys
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN_STR')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not API_TOKEN or not ADMIN_CHAT_ID:
    sys.exit("❌ Переменные окружения BOT_TOKEN_STR или ADMIN_CHAT_ID не заданы")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния
class InsuranceForm(StatesGroup):
    direction = State()
    object_info = State()
    period = State()
    comment = State()
    contact = State()

# Клавиатуры
def get_insurance_keyboard():
    """Создает клавиатуру для выбора направления страхования"""
    keyboard = [
        [KeyboardButton(text="🏠 Ипотека и недвижимость")],
        [KeyboardButton(text="🚗 ОСАГО и КАСКО")],
        [KeyboardButton(text="🏡 Имущество физлиц")],
        [KeyboardButton(text="📦 Грузы и логистика")],
        [KeyboardButton(text="💼 Коммерческое страхование")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_object_keyboard():
    """Создает клавиатуру для этапа описания объекта"""
    keyboard = [
        [KeyboardButton(text="🔙 Назад к выбору направления")],
        [KeyboardButton(text="🔄 Начать заново")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_period_keyboard():
    """Создает клавиатуру для этапа выбора срока"""
    keyboard = [
        [KeyboardButton(text="🔙 Назад к описанию объекта")],
        [KeyboardButton(text="🔄 Начать заново")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_comment_keyboard():
    """Создает клавиатуру для этапа комментария"""
    keyboard = [
        [KeyboardButton(text="🔙 Назад к сроку страхования")],
        [KeyboardButton(text="🔄 Начать заново")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_contact_keyboard():
    """Создает клавиатуру для этапа контактов"""
    keyboard = [
        [KeyboardButton(text="🔙 Назад к комментарию")],
        [KeyboardButton(text="🔄 Начать заново")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'strahovanie':
        welcome_msg = (
            f"🛡️ <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            "🏠 <b>Надежное страхование недвижимости</b>\n\n"
            "🎯 <b>Наши преимущества:</b>\n"
            "• 💯 Полная защита вашего имущества\n"
            "• ⚡ Быстрое оформление за 15 минут\n"
            "• 💰 Выгодные тарифы и скидки до 30%\n"
            "• 🚨 Круглосуточная поддержка при страховых случаях\n"
            "• 📋 Простое урегулирование убытков\n"
            "• 🏆 Работаем с ведущими страховыми компаниями\n\n"
            "🔒 <b>Выберите направление страхования:</b>"
        )
    else:
        welcome_msg = (
            f"🛡️ <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            "🏠 <b>Профессиональное страхование недвижимости</b>\n\n"
            "🎯 <b>Почему выбирают нас:</b>\n"
            "• 💯 Максимальная защита имущества\n"
            "• ⚡ Онлайн оформление без визитов в офис\n"
            "• 💰 Лучшие условия на рынке\n"
            "• 🚨 Экстренная помощь 24/7\n"
            "• 📋 Прозрачные условия без скрытых платежей\n"
            "• 🏆 Высокий рейтинг надежности\n\n"
            "🔒 <b>Выберите тип страхования:</b>"
        )
    
    await message.answer(welcome_msg, reply_markup=get_insurance_keyboard())
    await state.set_state(InsuranceForm.direction)

@dp.message(F.text.in_(["🔙 Назад к выбору направления", "🔙 Назад к описанию объекта", "🔙 Назад к сроку страхования", "🔙 Назад к комментарию", "🔄 Начать заново"]))
async def navigation_handler(message: types.Message, state: FSMContext):
    try:
        if message.text == "🔄 Начать заново":
            await state.set_state(InsuranceForm.direction)
            await message.answer(
                "🔄 <b>Начинаем заново!</b>\n\n🛡️ Выберите направление страхования:",
                reply_markup=get_insurance_keyboard()
            )
        elif message.text == "🔙 Назад к выбору направления":
            await state.set_state(InsuranceForm.direction)
            await message.answer(
                "🛡️ <b>Выберите направление страхования:</b>",
                reply_markup=get_insurance_keyboard()
            )
        elif message.text == "🔙 Назад к описанию объекта":
            await state.set_state(InsuranceForm.object_info)
            await message.answer(
                "📄 <b>Уточните объект страхования:</b>\n\n💡 Опишите подробно что именно вы хотите застраховать",
                reply_markup=get_object_keyboard()
            )
        elif message.text == "🔙 Назад к сроку страхования":
            await state.set_state(InsuranceForm.period)
            await message.answer(
                "📅 <b>Укажите желаемый срок страхования:</b>\n\n⏰ Например: 1 год, 6 месяцев, 3 месяца",
                reply_markup=get_period_keyboard()
            )
        elif message.text == "🔙 Назад к комментарию":
            await state.set_state(InsuranceForm.comment)
            await message.answer(
                "📝 <b>Дополнительные пожелания или комментарии:</b>\n\n💬 Укажите особые условия или напишите 'нет'",
                reply_markup=get_comment_keyboard()
            )
    except Exception as e:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(InsuranceForm.direction)
async def process_direction(message: types.Message, state: FSMContext):
    options = [
        "🏠 Ипотека и недвижимость", "🚗 ОСАГО и КАСКО", "🏡 Имущество физлиц",
        "📦 Грузы и логистика", "💼 Коммерческое страхование"
    ]
    if message.text not in options:
        await message.answer("❗Пожалуйста, выберите вариант из списка.", reply_markup=get_insurance_keyboard())
        return
    await state.update_data(direction=message.text)
    await state.set_state(InsuranceForm.object_info)
    
    # Персонализированные сообщения для разных типов страхования
    if "Ипотека" in message.text:
        await message.answer(
            "🏠 <b>Уточните объект ипотечного страхования</b>\n\n"
            "💡 Опишите подробно недвижимость:\n"
            "• Тип недвижимости (квартира, дом, таунхаус)\n"
            "• Площадь (общая и жилая)\n"
            "• Адрес или район\n"
            "• Этаж (для квартиры)\n"
            "• Год постройки\n"
            "• Стоимость недвижимости",
            reply_markup=get_object_keyboard()
        )
    elif "ОСАГО" in message.text:
        await message.answer(
            "🚗 <b>Уточните данные автомобиля для ОСАГО</b>\n\n"
            "💡 Укажите информацию об автомобиле:\n"
            "• Марка и модель\n"
            "• Год выпуска\n"
            "• Мощность двигателя (л.с.)\n"
            "• Регион регистрации\n"
            "• Количество водителей\n"
            "• Возраст и стаж водителей",
            reply_markup=get_object_keyboard()
        )
    elif "Имущество" in message.text:
        await message.answer(
            "🏡 <b>Уточните объект страхования имущества</b>\n\n"
            "💡 Опишите подробно что страхуем:\n"
            "• Тип недвижимости (квартира, дом, дача)\n"
            "• Площадь и адрес\n"
            "• Движимое имущество (мебель, техника)\n"
            "• Примерная стоимость имущества\n"
            "• Особенности объекта",
            reply_markup=get_object_keyboard()
        )
    elif "Грузы" in message.text:
        await message.answer(
            "📦 <b>Уточните данные груза</b>\n\n"
            "💡 Укажите информацию о грузе:\n"
            "• Тип и описание груза\n"
            "• Стоимость груза\n"
            "• Маршрут перевозки\n"
            "• Вид транспорта\n"
            "• Упаковка и особенности",
            reply_markup=get_object_keyboard()
        )
    else:
        await message.answer(
            "📄 <b>Уточните объект страхования</b>\n\n"
            "💡 Опишите подробно что именно вы хотите застраховать:\n"
            "• Детали объекта страхования\n"
            "• Стоимость или оценочная стоимость\n"
            "• Особенности и риски\n"
            "• Другие важные детали",
            reply_markup=get_object_keyboard()
        )

@dp.message(InsuranceForm.object_info)
async def process_object(message: types.Message, state: FSMContext):
    await state.update_data(object_info=message.text)
    await state.set_state(InsuranceForm.period)
    await message.answer(
        "📅 <b>Укажите желаемый срок страхования</b>\n\n"
        "⏰ Примеры:\n"
        "• 1 год\n"
        "• 6 месяцев\n"
        "• 3 месяца\n"
        "• Другой срок",
        reply_markup=get_period_keyboard()
    )

@dp.message(InsuranceForm.period)
async def process_period(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)
    await state.set_state(InsuranceForm.comment)
    await message.answer(
        "📝 <b>Дополнительные пожелания или комментарии</b>\n\n"
        "💬 Укажите если есть:\n"
        "• Особые условия страхования\n"
        "• Предпочтения по франшизе\n"
        "• Дополнительные риски\n"
        "• Другие пожелания\n\n"
        "Или напишите 'нет', если дополнений нет.",
        reply_markup=get_comment_keyboard()
    )

@dp.message(InsuranceForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(InsuranceForm.contact)
    await message.answer(
        "📞 <b>Контактная информация</b>\n\n"
        "👤 Укажите для связи:\n"
        "• Ваше имя\n"
        "• Номер телефона\n"
        "• Удобное время для звонка (по желанию)\n\n"
        "📝 Пример: Иван Петров, +7 (999) 123-45-67, с 9:00 до 18:00",
        reply_markup=get_contact_keyboard()
    )

@dp.message(InsuranceForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    summary = (
        f"<b>📥 Новая заявка на страхование:</b>\n"
        f"🔹 Направление: {data.get('direction')}\n"
        f"🔹 Объект: {data.get('object_info')}\n"
        f"🔹 Срок: {data.get('period')}\n"
        f"🔹 Комментарий: {data.get('comment')}\n"
        f"🔹 Контакт: {data.get('contact')}"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
    await message.answer(
        "✅ <b>Заявка успешно отправлена!</b>\n\n"
        "🎉 Спасибо за обращение! Ваша заявка на страхование принята и передана нашим специалистам.\n\n"
        "📞 <b>Что дальше:</b>\n"
        "• Наш эксперт свяжется с вами в течение 30 минут\n"
        "• Проведет бесплатную консультацию\n"
        "• Подберет оптимальные условия страхования\n"
        "• Поможет оформить полис с максимальной выгодой\n\n"
        "🛡️ <b>Ваши преимущества:</b>\n"
        "• Индивидуальный подход к каждому клиенту\n"
        "• Лучшие тарифы от ведущих страховых компаний\n"
        "• Быстрое оформление и получение полиса\n\n"
        "💼 Мы работаем для вашей безопасности и спокойствия!",
        reply_markup=get_insurance_keyboard()
    )
    await state.clear()

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
