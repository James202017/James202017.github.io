import logging
import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

try:
    import ssl
except ModuleNotFoundError:
    ssl = None
    logging.error("Модуль SSL не найден. Проверьте наличие OpenSSL в вашей системе.")

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command, Text
from aiogram.utils import executor

# Настройка логирования
log_filename = f'bot_{datetime.now().strftime("%Y%m%d")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение значений из переменных окружения
API_TOKEN = os.getenv('API_TOKEN3')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Проверка наличия необходимых переменных окружения
if not API_TOKEN:
    raise ValueError("API_TOKEN3 не найден в .env файле")
if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в .env файле")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    raise ValueError("ADMIN_CHAT_ID должен быть числом")

# Проверка SSL
if ssl is None:
    sys.exit("Ошибка: Модуль SSL недоступен. Установите OpenSSL или используйте среду с поддержкой SSL.")

# Инициализация бота
bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class InvestForm(StatesGroup):
    direction = State()
    amount = State()
    term = State()
    comment = State()
    photo = State()
    contact = State()

# Клавиатуры
def get_invest_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="🏗️ 1. Новостройки (доход до 3 млн руб и выше)")],
            [KeyboardButton(text="🌍 2. Зарубежная недвижимость")],
            [KeyboardButton(text="💎 3. Выкуп лотов ниже рынка")],
            [KeyboardButton(text="💰 4. Вклады под 29% годовых")],
            [KeyboardButton(text="🔙 Назад")]
        ]
    )

# Валидация опций
VALID_OPTIONS = [
    "🏗️ 1. Новостройки (доход до 3 млн руб и выше)",
    "🌍 2. Зарубежная недвижимость",
    "💎 3. Выкуп лотов ниже рынка",
    "💰 4. Вклады под 29% годовых"
]

# Тексты сообщений
WELCOME_MESSAGE = (
    "<b>🎉 Добро пожаловать в мир выгодных инвестиций!</b>\n\n"
    "💼 С помощью этого умного помощника вы можете оставить заявку на самые перспективные инвестиционные предложения!\n\n"
    "🚀 <b>Наши топ-направления:</b>\n"
    "🌍 Зарубежная недвижимость\n"
    "💰 Вклады под 29% годовых\n"
    "📈 Пассивный доход от 100,000₽/месяц\n\n"
    "✨ Пожалуйста, заполняйте все поля внимательно и максимально подробно, "
    "чтобы наши <b>эксперты-консультанты</b> могли связаться с вами и предложить идеальное решение! 🎯"
)

RECOMMENDATIONS = (
    "📋 <b>Важные рекомендации для успешной заявки:</b>\n\n"
    "✅ Указывайте максимум информации о ваших целях\n"
    "📝 Все поля обязательны для заполнения\n"
    "🎯 Мы подберем <b>персональное</b> выгодное решение\n"
    "⚡ Быстрая обработка заявки в течение 2-х часов\n"
    "🔒 Полная конфиденциальность ваших данных\n\n"
    "💡 <i>Чем подробнее информация, тем точнее наше предложение!</i>"
)

def format_amount(amount: str) -> str:
    """Форматирует сумму для отображения"""
    try:
        num = float(amount.replace(' ', '').replace(',', '.'))
        return f"{num:,.2f}".replace(',', ' ').replace('.', ',')
    except ValueError:
        return amount

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    try:
        # Получаем параметр start из команды
        start_param = message.get_args() if hasattr(message, 'get_args') else ''
        logger.info(f"Пользователь {message.from_user.id} запустил бота с параметром: {start_param}")
        
        # Персонализированное приветствие в зависимости от источника
        if start_param == 'investicii':
            welcome_msg = "🎯 <b>Отлично! Вы перешли из раздела инвестиций на сайте!</b>\n\n" + WELCOME_MESSAGE
        else:
            welcome_msg = WELCOME_MESSAGE
            
        await message.answer(welcome_msg)
        await message.answer(RECOMMENDATIONS)
        await state.set_state(InvestForm.direction)
        await message.answer("Выберите направление инвестиций:", reply_markup=get_invest_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(Text(equals="🔙 Назад"), state='*')
async def go_back(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        state_list = list(InvestForm.__all_states__)
        
        if current_state == state_list[0]:
            await message.answer(
                "Вы на начальном этапе. Выберите направление инвестиций:",
                reply_markup=get_invest_keyboard()
            )
        else:
            prev_index = state_list.index(current_state) - 1
            await state.set_state(state_list[prev_index])
            await message.answer("⬅️ Вернулись на предыдущий шаг. Введите данные снова:")
    except Exception as e:
        logger.error(f"Ошибка в команде назад: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(state=InvestForm.direction)
async def process_direction(message: types.Message, state: FSMContext):
    try:
        if message.text not in VALID_OPTIONS:
            await message.answer(
                "❗Пожалуйста, выберите вариант из списка.",
                reply_markup=get_invest_keyboard()
            )
            return
        
        logger.info(f"Пользователь {message.from_user.id} выбрал направление: {message.text}")
        await state.update_data(direction=message.text)
        await state.set_state(InvestForm.amount)
        await message.answer(
            "💰 <b>Отлично!</b> Теперь укажите желаемую сумму инвестиций:\n\n"
            "💡 <i>Например: 500000, 1000000, 5000000</i>",
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке направления: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(state=InvestForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Это поле обязательно. Укажите сумму.")
            return
        
        # Проверка на числовое значение
        try:
            amount = float(message.text.replace(' ', '').replace(',', '.'))
            if amount <= 0:
                raise ValueError
            formatted_amount = format_amount(message.text)
        except ValueError:
            await message.answer("❗Пожалуйста, введите корректную сумму числом.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} указал сумму: {formatted_amount}")
        await state.update_data(amount=formatted_amount)
        await state.set_state(InvestForm.term)
        await message.answer(
            "📅 <b>Превосходно!</b> На какой срок планируете инвестировать?\n\n"
            "⏰ <i>Например: 6 месяцев, 1 год, 2-3 года, долгосрочно</i>\n\n"
            "💡 <b>Подсказка:</b> Чем дольше срок, тем выше потенциальная доходность! 📈"
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке суммы: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(state=InvestForm.term)
async def process_term(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Пожалуйста, укажите срок.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} указал срок: {message.text}")
        await state.update_data(term=message.text)
        await state.set_state(InvestForm.comment)
        await message.answer(
            "📝 <b>Замечательно!</b> Есть ли у вас дополнительные пожелания или комментарии?\n\n"
            "💭 <i>Например: предпочтения по регионам, уровень риска, особые требования</i>\n\n"
            "✨ Любая дополнительная информация поможет нам подобрать идеальный вариант!"
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке срока: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(state=InvestForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Пользователь {message.from_user.id} добавил комментарий")
        await state.update_data(comment=message.text)
        await state.set_state(InvestForm.photo)
        
        # Создаем inline клавиатуру для выбора
        photo_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📷 Добавить фото", callback_data="add_photo")],
            [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_photo")]
        ])
        
        await message.answer(
            "📸 <b>Хотите добавить фотографии?</b>\n\n"
            "🖼️ Вы можете приложить изображения, которые помогут лучше понять ваши потребности:\n"
            "• Примеры желаемой недвижимости\n"
            "• Документы или справки\n"
            "• Любые визуальные материалы\n\n"
            "💡 <i>Фото помогут нашим экспертам дать более точные рекомендации!</i>",
            reply_markup=photo_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке комментария: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик callback кнопок для фото
@dp.callback_query_handler(lambda c: c.data in ["add_photo", "skip_photo"], state=InvestForm.photo)
async def handle_photo_choice(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        
        if callback.data == "add_photo":
            await callback.message.edit_text(
                "📷 <b>Отлично!</b> Отправьте фотографии (можно несколько)\n\n"
                "📎 После загрузки всех фото нажмите кнопку \"Готово\" или отправьте текст \"готово\"",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Готово", callback_data="photos_done")]
                ])
            )
            await state.update_data(photos=[])
        else:
            await callback.message.edit_text("⏭️ Фотографии пропущены")
            await state.set_state(InvestForm.contact)
            await callback.message.answer(
                "📞 <b>Почти готово!</b> Укажите ваше имя и номер телефона для связи:\n\n"
                "👤 <i>Например: Иван Петров, +7 (999) 123-45-67</i>\n\n"
                "🔒 Ваши данные надежно защищены и используются только для связи с вами!"
            )
    except Exception as e:
        logger.error(f"Ошибка в обработке выбора фото: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик фотографий
@dp.message_handler(content_types=['photo'], state=InvestForm.photo)
async def process_photo(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        photos = data.get('photos', [])
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
        
        await message.answer(
            f"📸 Фото #{len(photos)} добавлено!\n\n"
            "📎 Можете отправить еще фото или нажать \"Готово\"",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Готово", callback_data="photos_done")]
            ])
        )
        logger.info(f"Пользователь {message.from_user.id} добавил фото #{len(photos)}")
    except Exception as e:
        logger.error(f"Ошибка в обработке фото: {e}")
        await message.answer("Произошла ошибка при загрузке фото. Попробуйте еще раз.")

# Обработчик завершения загрузки фото
@dp.callback_query_handler(lambda c: c.data == "photos_done", state=InvestForm.photo)
async def photos_done(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        data = await state.get_data()
        photos_count = len(data.get('photos', []))
        
        await callback.message.edit_text(
            f"✅ <b>Отлично!</b> Загружено фотографий: {photos_count}\n\n"
            "📞 Теперь укажите контактные данные"
        )
        
        await state.set_state(InvestForm.contact)
        await callback.message.answer(
            "📞 <b>Почти готово!</b> Укажите ваше имя и номер телефона для связи:\n\n"
            "👤 <i>Например: Иван Петров, +7 (999) 123-45-67</i>\n\n"
            "🔒 Ваши данные надежно защищены и используются только для связи с вами!"
        )
    except Exception as e:
        logger.error(f"Ошибка в завершении загрузки фото: {e}")
        await callback.message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик текста "готово" для фото
@dp.message_handler(Text(equals="готово", ignore_case=True), state=InvestForm.photo)
async def photos_done_text(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        photos_count = len(data.get('photos', []))
        
        await message.answer(
            f"✅ <b>Отлично!</b> Загружено фотографий: {photos_count}\n\n"
            "📞 Теперь укажите контактные данные"
        )
        
        await state.set_state(InvestForm.contact)
        await message.answer(
            "📞 <b>Почти готово!</b> Укажите ваше имя и номер телефона для связи:\n\n"
            "👤 <i>Например: Иван Петров, +7 (999) 123-45-67</i>\n\n"
            "🔒 Ваши данные надежно защищены и используются только для связи с вами!"
        )
    except Exception as e:
        logger.error(f"Ошибка в завершении загрузки фото текстом: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message_handler(state=InvestForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Контактные данные обязательны.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} отправил контактные данные")
        await state.update_data(contact=message.text)
        data = await state.get_data()

        photos = data.get('photos', [])
        photos_info = f"📸 Фотографий: {len(photos)}" if photos else "📸 Фотографий: нет"
        
        summary = (
            f"<b>📥 Новая заявка на инвестиции:</b>\n\n"
            f"🔸 Направление: {data.get('direction')}\n"
            f"🔸 Сумма: {data.get('amount')}\n"
            f"🔸 Срок: {data.get('term')}\n"
            f"🔸 Комментарий: {data.get('comment')}\n"
            f"🔸 {photos_info}\n"
            f"🔸 Контакт: {data.get('contact')}\n\n"
            f"👤 От: {message.from_user.full_name} (ID: {message.from_user.id})\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
        
        # Отправляем фотографии, если они есть
        if photos:
            for i, photo_id in enumerate(photos, 1):
                try:
                    await bot.send_photo(
                        chat_id=ADMIN_CHAT_ID, 
                        photo=photo_id,
                        caption=f"📸 Фото #{i} от {message.from_user.full_name}"
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки фото #{i}: {e}")
        await message.answer(
            "🎉 <b>Поздравляем! Ваша заявка успешно отправлена!</b>\n\n"
            "✅ Заявка принята и передана нашим экспертам\n"
            "📞 Наш консультант свяжется с вами в течение 2-х часов\n"
            "💼 Мы подготовим персональное предложение\n\n"
            "🚀 <b>Спасибо за доверие! Вместе к финансовому успеху!</b> 💎"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка в обработке контакта: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

def main():
    try:
        logger.info("Бот запущен")
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
