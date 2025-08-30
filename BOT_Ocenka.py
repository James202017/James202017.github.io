import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN5')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class AppraisalForm(StatesGroup):
    object_type = State()
    purpose = State()
    region = State()
    area = State()
    comment = State()
    contact = State()

object_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="1. Квартира"), KeyboardButton(text="2. Дом")],
    [KeyboardButton(text="3. Земельный участок"), KeyboardButton(text="4. Коммерция")],
    [KeyboardButton(text="🔙 Назад")]
])

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'ocenka':
        welcome_msg = "📊 <b>Отлично! Вы перешли из раздела оценки на сайте!</b>\n\n<b>Добро пожаловать!</b>\n\nНужна официальная оценка недвижимости? 🏢 Мы подготовим отчет за 1 день!* ✅ Для банков, судов, сделок ✅ Гарантия принятия документа\nПожалуйста, заполняйте все поля внимательно и максимально подробно, чтобы наши специалисты могли связаться с вами и помочь быстро и качественно."
    else:
        welcome_msg = "<b>Добро пожаловать!</b>\n\nНужна официальная оценка недвижимости? 🏢 Мы подготовим отчет за 1 день!* ✅ Для банков, судов, сделок ✅ Гарантия принятия документа\nПожалуйста, заполняйте все поля внимательно и максимально подробно, чтобы наши специалисты могли связаться с вами и помочь быстро и качественно."
    
    await message.answer(welcome_msg)
    await message.answer("Для продолжения нажмите нужный вам вариант. Что хотели бы оценить?", reply_markup=object_kb)
    await state.set_state(AppraisalForm.object_type)

@dp.message_handler(lambda message: message.text == "🔙 Назад", state='*')
async def go_back(message: types.Message, state: FSMContext):
    current = await state.get_state()
    steps = list(AppraisalForm.__all_states__)
    if current == steps[0]:
        await message.answer("Вы на начальном шаге. Укажите тип объекта:")
    else:
        idx = steps.index(current) - 1
        await state.set_state(steps[idx])
        await message.answer("⬅️ Вернулись на предыдущий шаг. Введите данные снова:")

@dp.message_handler(state=AppraisalForm.object_type)
async def handle_object(message: types.Message, state: FSMContext):
    await state.update_data(object_type=message.text)
    await state.set_state(AppraisalForm.purpose)
    await message.answer("🎯 Укажите цель оценки (например: для продажи, для суда, для ипотеки):")

@dp.message_handler(state=AppraisalForm.purpose)
async def handle_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await state.set_state(AppraisalForm.region)
    await message.answer("🌍 Укажите регион или адрес объекта:")

@dp.message_handler(state=AppraisalForm.region)
async def handle_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    await state.set_state(AppraisalForm.area)
    await message.answer("📐 Укажите площадь объекта в м²:")

@dp.message_handler(state=AppraisalForm.area)
async def handle_area(message: types.Message, state: FSMContext):
    await state.update_data(area=message.text)
    await state.set_state(AppraisalForm.comment)
    await message.answer("📝 Есть ли дополнительные данные или комментарии?")

@dp.message_handler(state=AppraisalForm.comment)
async def handle_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(AppraisalForm.contact)
    await message.answer("📞 Укажите ваше имя и телефон для связи:")

@dp.message_handler(state=AppraisalForm.contact)
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
    await message.answer("✅ Спасибо! Ваша заявка отправлена. Мы скоро свяжемся с вами.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
