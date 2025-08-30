import logging
import asyncio
import os
import sys
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN4')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not API_TOKEN or not ADMIN_CHAT_ID:
    sys.exit("❌ Переменные окружения API_TOKEN4 или ADMIN_CHAT_ID не заданы")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния
class InsuranceForm(StatesGroup):
    direction = State()
    object_info = State()
    period = State()
    comment = State()
    contact = State()

# Клавиатура
insurance_kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="1. ОСАГО"), KeyboardButton(text="2. Ипотека")],
    [KeyboardButton(text="3. Имущество"), KeyboardButton(text="4. Грузы")],
    [KeyboardButton(text="5. Антиклещ"), KeyboardButton(text="6. Несчастные случаи")],
    [KeyboardButton(text="7. Потеря работы")],
    [KeyboardButton(text="🔙 Назад")]
])

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    # Получаем параметр start из команды
    start_param = message.text.split()[1] if len(message.text.split()) > 1 else ''
    
    # Персонализированное приветствие в зависимости от источника
    if start_param == 'strahovanie':
        welcome_msg = "🛡️ <b>Отлично! Вы перешли из раздела страхования на сайте!</b>\n\n<b>Добро пожаловать!</b>\n\nС помощью этого помощника вы можете оставить заявку на страхование. Защита для вас и вашего имущества: ОСАГО, ипотечное страхование, защита от несчастных случаев и потери работы."
    else:
        welcome_msg = "<b>Добро пожаловать!</b>\n\nС помощью этого помощника вы можете оставить заявку на страхование. Защита для вас и вашего имущества: ОСАГО, ипотечное страхование, защита от несчастных случаев и потери работы."
    
    await message.answer(welcome_msg)
    await state.set_state(InsuranceForm.direction)
    await message.answer("Выберите направление страхования:", reply_markup=insurance_kb)

@dp.message_handler(lambda message: message.text == "🔙 Назад", state='*')
async def go_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    state_list = list(InsuranceForm.__all_states__)
    if current_state == state_list[0]:
        await message.answer("🔄 Вы уже на первом шаге. Выберите направление:")
    else:
        prev_index = state_list.index(current_state) - 1
        await state.set_state(state_list[prev_index])
        await message.answer("⬅️ Вернулись на предыдущий шаг. Введите данные заново:")

@dp.message_handler(state=InsuranceForm.direction)
async def process_direction(message: types.Message, state: FSMContext):
    options = [
        "1. ОСАГО", "2. Ипотека", "3. Имущество",
        "4. Грузы", "5. Антиклещ", "6. Несчастные случаи", "7. Потеря работы"
    ]
    if message.text not in options:
        await message.answer("❗Пожалуйста, выберите вариант из списка.")
        return
    await state.update_data(direction=message.text)
    await state.set_state(InsuranceForm.object_info)
    await message.answer("📄 Уточните объект страхования")

@dp.message_handler(state=InsuranceForm.object_info)
async def process_object(message: types.Message, state: FSMContext):
    await state.update_data(object_info=message.text)
    await state.set_state(InsuranceForm.period)
    await message.answer("📅 Укажите желаемый срок страхования (например: 1 год, 6 месяцев):")

@dp.message_handler(state=InsuranceForm.period)
async def process_period(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)
    await state.set_state(InsuranceForm.comment)
    await message.answer("📝 Есть ли дополнительные пожелания или комментарии?")

@dp.message_handler(state=InsuranceForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(InsuranceForm.contact)
    await message.answer("📞 Укажите ваше имя и номер телефона для связи:")

@dp.message_handler(state=InsuranceForm.contact)
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
    await message.answer("✅ Спасибо! Ваша заявка принята. Наш специалист скоро свяжется с вами.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
