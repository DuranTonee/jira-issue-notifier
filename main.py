
'''how to deploy
1. $ ngrok http 8000
refer to https://dashboard.ngrok.com/get-started/setup
for token: https://dashboard.ngrok.com/get-started/your-authtoken
2. change the url at https://YOURDOMAIN.atlassian.net/plugins/servlet/webhooks#
3. change the host at settings.py in ALLOWED_HOSTS (or just add "*")
4. $ cd jira_notifications
5. $ gunicorn jira_notifications.wsgi
or (for development only) $ python manage.py runserver
6. run main.py
'''
from dotenv import load_dotenv
import os
from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from jira_notifications.jira_notifications_app.db import check_if_in_db, delete_from_db

dotenv_path = "jira_notifications/jira_notifications_app/.env"
load_dotenv(dotenv_path)
BOT_TOKEN = os.getenv("BOT_TOKEN")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class FSMRegister(StatesGroup):
    username_state = State()


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("Bot started! Use /register to start")
    print(f"{message.from_user.id} used /start!")
    

@dp.message_handler(commands="register")
async def reg_start(message: types.Message):
    await FSMRegister.username_state.set()
    await message.answer("Enter your jira username. /cancel for cancellation")


@dp.message_handler(commands="cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        # no state - ignoring
        return
        
    await state.finish()
    await message.answer("Cancelled.")


@dp.message_handler(state=FSMRegister.username_state)
async def reg_username(message: types.Message, state: FSMContext):
    await state.finish()

    jira_username = message.text
    tg_id = message.from_user.id
    in_db = check_if_in_db(jira_username, tg_id)
    if in_db == True:
        inline_button = InlineKeyboardButton(text="Unregister", callback_data=f"unreg")
        inline_keyboard = InlineKeyboardMarkup().add(inline_button)
        await message.answer("You are already registered! Would you like to unregister?", reply_markup=inline_keyboard)
    else:
        await message.answer("Registration successful!")


@dp.callback_query_handler(text = "unreg")
async def callback(call: types.CallbackQuery):
    if call.data == "unreg":
        tg_id = call.from_user.id
        delete_from_db(tg_id)
        await bot.send_message(tg_id, "Unregister successful!")
    await call.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
