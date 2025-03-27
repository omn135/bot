import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Настройки
TOKEN = "YOUR_BOT_TOKEN"  # Заменить на токен бота
CHANNEL_ID = "@your_channel"  # Заменить на ID канала/группы
ADMIN_ID = 123456789  # Заменить на твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

pending_reviews = {}  # Список сообщений на модерации

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Отправь мне отзыв, и после проверки он появится в канале.")

@dp.message_handler()
async def handle_review(message: types.Message):
    review_id = message.message_id
    pending_reviews[review_id] = message
    
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{review_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{review_id}")
    )
    
    await bot.send_message(ADMIN_ID, f"Новый отзыв от @{message.from_user.username}:")
    await bot.send_message(ADMIN_ID, f"{message.text}", reply_markup=keyboard)
    await message.reply("Ваш отзыв отправлен на проверку.")

@dp.callback_query_handler(Text(startswith="approve_"))
async def approve_review(callback_query: types.CallbackQuery):
    review_id = int(callback_query.data.split('_')[1])
    if review_id in pending_reviews:
        review = pending_reviews.pop(review_id)
        await bot.send_message(CHANNEL_ID, f"📝 Отзыв: Ваш текст тут")
        await callback_query.answer("Отзыв опубликован!")
    else:
        await callback_query.answer("Ошибка: отзыв не найден.")

@dp.callback_query_handler(Text(startswith="reject_"))
async def reject_review(callback_query: types.CallbackQuery):
    review_id = int(callback_query.data.split('_')[1])
    if review_id in pending_reviews:
        pending_reviews.pop(review_id)
        await callback_query.answer("Отзыв отклонен.")
    else:
        await callback_query.answer("Ошибка: отзыв не найден.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
