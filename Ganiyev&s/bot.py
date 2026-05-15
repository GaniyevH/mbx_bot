import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8773496702:AAEFnrlXd5xL2YMifJLuFTZk6jE7LnPth9w"

print("TOKEN:", repr(API_TOKEN))
print("TOKEN LENGTH:", len(API_TOKEN))

ADMIN_ID = 123456789

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

texts = {
    "choose_language": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Choose a language:"
    },
    "welcome": {
        "uz": "Assalomu alaykum! Tilni tanlab boshlang.",
        "ru": "Здравствуйте! Выберите язык.",
        "en": "Hello! Please choose a language."
    },
    "main_menu": {
        "uz": "Asosiy menyu:",
        "ru": "Главное меню:",
        "en": "Main menu:"
    },
    "register": {
        "uz": "Ro'yxatdan o'tish",
        "ru": "Регистрация",
        "en": "Register"
    },
    "admin": {
        "uz": "Boshqaruv",
        "ru": "Админка",
        "en": "Admin"
    },
    "language": {
        "uz": "Til",
        "ru": "Язык",
        "en": "Language"
    },
    "choose_name": {
        "uz": "Ism va familiyangizni kiriting:",
        "ru": "Введите ваше имя и фамилию:",
        "en": "Please enter your full name:"
    },
    "choose_phone": {
        "uz": "Telefon raqamingizni yuboring:",
        "ru": "Отправьте ваш номер телефона:",
        "en": "Send your phone number:"
    },
    "choose_location": {
        "uz": "Manzilni joylashuv sifatida yuboring:",
        "ru": "Отправьте местоположение:",
        "en": "Send your location:"
    },
    "registered": {
        "uz": "Ro'yxatdan o'tdingiz!",
        "ru": "Вы зарегистрированы!",
        "en": "You are registered!"
    },
    "invalid_contact": {
        "uz": "Iltimos, kontakt tugmasi orqali telefon raqam yuboring.",
        "ru": "Пожалуйста, отправьте номер через кнопку контакта.",
        "en": "Please send your phone via contact button."
    },
    "invalid_location": {
        "uz": "Iltimos, joylashuv yuboring.",
        "ru": "Пожалуйста, отправьте местоположение.",
        "en": "Please send your location."
    },
    "users_list": {
        "uz": "Ro'yxatdan o'tgan foydalanuvchilar:",
        "ru": "Зарегистрированные пользователи:",
        "en": "Registered users:"
    },
    "no_users": {
        "uz": "Hozircha foydalanuvchi yo'q.",
        "ru": "Пока нет пользователей.",
        "en": "No users yet."
    },
    "not_admin": {
        "uz": "Siz boshqaruvchi emassiz.",
        "ru": "Вы не администратор.",
        "en": "You are not an admin."
    },
    "language_selected": {
        "uz": "Til muvaffaqiyatli tanlandi.",
        "ru": "Язык выбран.",
        "en": "Language selected."
    },
}


def get_user_language(user_id: int) -> str:
    return user_data.get(user_id, {}).get("lang", "uz")


def get_text(user_id: int, key: str) -> str:
    lang = get_user_language(user_id)
    return texts[key][lang]


def main_menu_keyboard(user_id: int) -> types.ReplyKeyboardMarkup:
    lang = get_user_language(user_id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(texts["register"][lang])
    keyboard.add(texts["language"][lang])

    if user_id == ADMIN_ID:
        keyboard.add(texts["admin"][lang])

    return keyboard


def language_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Uz", "Ru", "En")
    return keyboard


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_data[message.from_user.id] = {"lang": "uz", "stage": None}
    await message.answer(texts["welcome"]["uz"], reply_markup=language_keyboard())
    await message.answer(texts["choose_language"]["uz"])


@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        await message.reply(get_text(user_id, "not_admin"))
        return

    await show_users(message)


async def show_users(message: types.Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    users = []
    for uid, entry in user_data.items():
        if entry.get("name"):
            users.append(
                f"ID: {uid}\n"
                f"Ism: {entry.get('name', '-')}\n"
                f"Telefon: {entry.get('phone', '-')}\n"
                f"Joylashuv: {entry.get('location', '-')}"
            )

    if not users:
        await message.answer(texts["no_users"][lang], reply_markup=main_menu_keyboard(user_id))
    else:
        await message.answer(
            texts["users_list"][lang] + "\n\n" + "\n\n".join(users),
            reply_markup=main_menu_keyboard(user_id)
        )


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    data = user_data.setdefault(user_id, {"lang": "uz", "stage": None})
    lang = data["lang"]

    if data.get("stage") != "await_phone":
        await message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))
        return

    data["phone"] = message.contact.phone_number
    data["stage"] = "await_location"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(text=texts["choose_location"][lang], request_location=True))

    await message.answer(texts["choose_location"][lang], reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    user_id = message.from_user.id
    data = user_data.setdefault(user_id, {"lang": "uz", "stage": None})
    lang = data["lang"]

    if data.get("stage") != "await_location":
        await message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))
        return

    data["location"] = f"{message.location.latitude}, {message.location.longitude}"
    data["stage"] = None

    await message.answer(texts["registered"][lang], reply_markup=main_menu_keyboard(user_id))


@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    data = user_data.setdefault(user_id, {"lang": "uz", "stage": None})
    lang = data["lang"]

    if text in ("Uz", "Ru", "En"):
        selected = {"Uz": "uz", "Ru": "ru", "En": "en"}[text]
        data["lang"] = selected
        data["stage"] = None
        await message.answer(
            texts["language_selected"][selected],
            reply_markup=main_menu_keyboard(user_id)
        )
        return

    if text == texts["language"][lang]:
        await message.answer(texts["choose_language"][lang], reply_markup=language_keyboard())
        return

    if text == texts["register"][lang]:
        data["stage"] = "await_name"
        await message.answer(texts["choose_name"][lang], reply_markup=types.ReplyKeyboardRemove())
        return

    if text == texts["admin"][lang]:
        if user_id != ADMIN_ID:
            await message.answer(texts["not_admin"][lang])
            return
        await show_users(message)
        return

    if data["stage"] == "await_name":
        data["name"] = text
        data["stage"] = "await_phone"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(types.KeyboardButton(text=texts["choose_phone"][lang], request_contact=True))

        await message.answer(texts["choose_phone"][lang], reply_markup=keyboard)
        return

    if data["stage"] == "await_phone":
        await message.answer(texts["invalid_contact"][lang])
        return

    if data["stage"] == "await_location":
        await message.answer(texts["invalid_location"][lang])
        return

    await message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)