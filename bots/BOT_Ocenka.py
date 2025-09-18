import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN_OCENKA')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class AppraisalForm(StatesGroup):
    object_type = State()
    purpose = State()
    region = State()
    area = State()
    comment = State()
    contact = State()

def get_object_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="1. Квартира"), KeyboardButton(text="2. Дом")],
        [KeyboardButton(text="3. Земельный участок"), KeyboardButton(text="4. Коммерция")],
        [KeyboardButton(text="🔄 Начать заново")]
    ])

def get_purpose_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Для ипотеки или кредита")],
        [KeyboardButton(text="Для судебного разбирательства")],
        [KeyboardButton(text="Для сделки купли-продажи")],
        [KeyboardButton(text="Для наследства или дарения")],
        [KeyboardButton(text="Назад к выбору объекта"), KeyboardButton(text="🔄 Начать заново")]
    ])

def get_region_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Назад к цели оценки"), KeyboardButton(text="🔄 Начать заново")]
    ])

def get_area_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Назад к местоположению"), KeyboardButton(text="🔄 Начать заново")]
    ])

def get_comment_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Назад к площади"), KeyboardButton(text="🔄 Начать заново")]
    ])

def get_contact_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Назад к комментарию"), KeyboardButton(text="🔄 Начать заново")]
    ])

@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'ocenka':
        welcome_msg = (
            "📊 **Отлично! Вы перешли из раздела оценки на сайте!**\n\n"
            "🎉 **Добро пожаловать в службу профессиональной оценки!**\n\n"
            "🏢 **Наши услуги оценки недвижимости:**\n"
            "• Квартиры и дома\n"
            "• Земельные участки\n"
            "• Коммерческая недвижимость\n"
            "• Производственные объекты\n\n"
            "⚡ **Ваши преимущества:**\n"
            "• Отчет готов за 1 рабочий день\n"
            "• Аккредитованные оценщики\n"
            "• Принимается всеми банками и судами\n"
            "• Гарантия качества и точности\n"
            "• Выезд оценщика в удобное время\n\n"
            "📋 **Для чего нужна оценка:**\n"
            "• Ипотека и кредиты\n"
            "• Судебные разбирательства\n"
            "• Сделки купли-продажи\n"
            "• Наследство и дарение\n\n"
            "📝 Заполните форму ниже, и наш эксперт свяжется с вами!"
        )
    else:
        welcome_msg = (
            "🎉 **Добро пожаловать в службу профессиональной оценки!**\n\n"
            "🏢 **Наши услуги оценки недвижимости:**\n"
            "• Квартиры и дома\n"
            "• Земельные участки\n"
            "• Коммерческая недвижимость\n"
            "• Производственные объекты\n\n"
            "⚡ **Ваши преимущества:**\n"
            "• Отчет готов за 1 рабочий день\n"
            "• Аккредитованные оценщики\n"
            "• Принимается всеми банками и судами\n"
            "• Гарантия качества и точности\n"
            "• Выезд оценщика в удобное время\n\n"
            "📋 **Для чего нужна оценка:**\n"
            "• Ипотека и кредиты\n"
            "• Судебные разбирательства\n"
            "• Сделки купли-продажи\n"
            "• Наследство и дарение\n\n"
            "📝 Заполните форму ниже, и наш эксперт свяжется с вами!"
        )
    
    await message.answer(welcome_msg)
    await message.answer(
        "🎯 **Выберите тип объекта для оценки:**\n\n"
        "Нажмите на подходящий вариант ниже ⬇️",
        reply_markup=get_object_keyboard()
    )
    await state.set_state(AppraisalForm.object_type)

@dp.message(F.text.in_([
    "🔄 Начать заново", "Назад к выбору объекта", "Назад к цели оценки", 
    "Назад к местоположению", "Назад к площади", "Назад к комментарию"
]))
async def navigation_handler(message: types.Message, state: FSMContext):
    if message.text == "🔄 Начать заново":
        await state.set_state(AppraisalForm.object_type)
        await message.answer(
            "🔄 **Начинаем заново!**\n\n"
            "🎯 **Выберите тип объекта для оценки:**",
            reply_markup=get_object_keyboard()
        )
    elif message.text == "Назад к выбору объекта":
        await state.set_state(AppraisalForm.object_type)
        await message.answer(
            "🎯 **Выберите тип объекта для оценки:**",
            reply_markup=get_object_keyboard()
        )
    elif message.text == "Назад к цели оценки":
        await state.set_state(AppraisalForm.purpose)
        await message.answer(
            "🎯 **Укажите цель оценки:**",
            reply_markup=get_purpose_keyboard()
        )
    elif message.text == "Назад к местоположению":
        await state.set_state(AppraisalForm.region)
        await message.answer(
            "🌍 **Укажите местоположение объекта:**",
            reply_markup=get_region_keyboard()
        )
    elif message.text == "Назад к площади":
        await state.set_state(AppraisalForm.area)
        await message.answer(
            "📐 **Укажите площадь объекта:**",
            reply_markup=get_area_keyboard()
        )
    elif message.text == "Назад к комментарию":
        await state.set_state(AppraisalForm.comment)
        await message.answer(
            "📝 **Дополнительная информация:**",
            reply_markup=get_comment_keyboard()
        )

@dp.message(AppraisalForm.object_type)
async def handle_object(message: types.Message, state: FSMContext):
    object_options = [
        "🏠 Квартира", "🏡 Дом/коттедж", "🌾 Земельный участок",
        "🏢 Коммерческая недвижимость", "🏭 Производственный объект"
    ]
    if message.text not in object_options:
        await message.answer("❗Пожалуйста, выберите вариант из списка.", reply_markup=get_object_keyboard())
        return
    await state.update_data(object_type=message.text)
    await state.set_state(AppraisalForm.purpose)
    await message.answer(
        "🎯 <b>Укажите цель оценки</b>\n\n"
        "📋 Выберите или укажите цель:\n"
        "• Для ипотеки или кредита\n"
        "• Для судебного разбирательства\n"
        "• Для сделки купли-продажи\n"
        "• Для наследства или дарения\n"
        "• Для страхования\n"
        "• Другая цель (укажите какая)",
        reply_markup=get_purpose_keyboard()
    )

@dp.message(AppraisalForm.purpose)
async def handle_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await state.set_state(AppraisalForm.region)
    await message.answer(
        "🌍 <b>Укажите местоположение объекта</b>\n\n"
        "📍 Укажите как можно подробнее:\n"
        "• Регион/область\n"
        "• Город/населенный пункт\n"
        "• Улица и номер дома\n"
        "• Дополнительные ориентиры\n\n"
        "📝 Пример: Московская область, г. Подольск, ул. Ленина, д. 15",
        reply_markup=get_region_keyboard()
    )

@dp.message(AppraisalForm.region)
async def handle_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    await state.set_state(AppraisalForm.area)
    await message.answer(
        "📐 <b>Укажите площадь объекта</b>\n\n"
        "📏 Укажите площадь в квадратных метрах:\n"
        "• Общая площадь\n"
        "• Жилая площадь (для квартир/домов)\n"
        "• Площадь участка (для земли)\n\n"
        "📝 Пример: 65 м² общая, 45 м² жилая",
        reply_markup=get_area_keyboard()
    )

@dp.message(AppraisalForm.area)
async def handle_area(message: types.Message, state: FSMContext):
    await state.update_data(area=message.text)
    await state.set_state(AppraisalForm.comment)
    await message.answer(
        "📝 <b>Дополнительная информация</b>\n\n"
        "💬 Укажите если есть:\n"
        "• Год постройки\n"
        "• Состояние объекта\n"
        "• Особенности планировки\n"
        "• Наличие ремонта\n"
        "• Другие важные детали\n\n"
        "Или напишите 'нет', если дополнений нет.",
        reply_markup=get_comment_keyboard()
    )

@dp.message(AppraisalForm.comment)
async def handle_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(AppraisalForm.contact)
    await message.answer(
        "📞 <b>Контактная информация</b>\n\n"
        "👤 Укажите для связи:\n"
        "• Ваше имя\n"
        "• Номер телефона\n"
        "• Удобное время для звонка (по желанию)\n\n"
        "📝 Пример: Иван Петров, +7 (999) 123-45-67, с 9:00 до 18:00",
        reply_markup=get_contact_keyboard()
    )

@dp.message(AppraisalForm.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    result = (
        f"<b>📩 Новая заявка на оценку:</b>\n"
        f"🏠 Объект: {data.get('object_type')}\n"
        f"🎯 Цель: {data.get('purpose')}\n"
        f"🌍 Регион: {data.get('region')}\n"
        f"📐 Площадь: {data.get('area')}\n"
        f"📝 Комментарий: {data.get('comment')}\n"
        f"📞 Контакт: {data.get('contact')}"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=result)
    await message.answer(
        "✅ **Заявка успешно отправлена!**\n\n"
        "🎉 Спасибо за обращение! Ваша заявка на оценку принята и передана нашим экспертам.\n\n"
        "📞 **Что дальше:**\n"
        "• Наш оценщик свяжется с вами в течение 30 минут\n"
        "• Проведет бесплатную консультацию\n"
        "• Согласует удобное время выезда\n"
        "• Подготовит официальный отчет за 1 день\n\n"
        "📊 **Ваши преимущества:**\n"
        "• Аккредитованные оценщики с лицензией\n"
        "• Отчет принимается всеми банками\n"
        "• Гарантия качества и точности оценки\n"
        "• Выгодные цены и быстрые сроки\n\n"
        "🏢 Мы работаем для точной и честной оценки!",
        reply_markup=get_object_keyboard()
    )
    await state.clear()

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
