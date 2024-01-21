import requests
from config import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

START_ACTION = "start"
STOP_ACTION = "stop"
# Stages
START_ROUTES, MAP_ROUTES, SETTING_ROUTES, INFO_ROUTES = range(4)
# Callback data
ERROR = 404
MAPS, SETTINGS, INFO, BACK, ON_SERVER, OFF_SERVER = range(6)
maps = ["2000$", "aim_headshot", "awp_india",
        "fy_buzzkill", "fy_iceworld", "ka_deatharena",
        "fy_new_iceworld", "fy_dinoiceworld", "fy_pool_day"]
maps_dict = {}
count = 6
for value in maps:
    maps_dict[value] = count
    count += 1


def change_map(map_name: str) -> bool:
    # Формируем ссылку на API сервер CS 1.6
    api_url = f"http://cp.gamehost.com.ua/api.html?action=map&id={ID_SERVER}&key={API_KEY}&map={map_name}"

    # Отправляем GET-запрос на API сервер и получаем ответ в формате JSON
    response = requests.get(api_url).json()
    # Проверяем, есть ли ключ "message" в ответе
    if not "message" in response:
        return True
    return False


def server_action(action: str) -> bool:
    api_url = f"http://cp.gamehost.com.ua/api.html?action={action}&id={ID_SERVER}&key={API_KEY}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return True
    else:
        return False


def get_info() -> str:
    api_url = f"http://cp.gamehost.com.ua/api.html?action=status&id={ID_SERVER}&key={API_KEY}"
    try:
        response = requests.get(api_url).json()
        players: str = ''
        if response['players']:
            for player in response['players']:
                players += 'Player: ' + str(player['name']) + ', Kills: ' + str(player['frags']) + ', Time: ' + str(
                    player['time']) + '\n'
        else:
            players = '-'
        server_info = f"Server: {response['info']['hostname']}" \
                      f"\nStatus: {'Online' if response['online'] else 'Offline'}" \
                      f"\nMap: {response['info']['map']}" \
                      f"\nNumber of players: {response['info']['activeplayers']}" \
                      f"\nPlayers: {players}"
        return server_info
    except requests.exceptions.RequestException as e:
        return f"Error sending request: {e}"
    except Exception as e:
        return f"Error has occurred: {e}"


def get_key(d: dict, value_of_dict: any) -> any:
    for k, v in d.items():
        if v == value_of_dict:
            return k


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.from_user.id not in ALLOWED_USERS:
        await update.message.reply_text("You haven't access to bot!")
        return ERROR
    keyboard = [
        [InlineKeyboardButton("🌎Maps", callback_data=str(MAPS))],
        [InlineKeyboardButton("⚙️Control", callback_data=str(SETTINGS))],
        [InlineKeyboardButton("ℹ️Info", callback_data=str(INFO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select menu item:", reply_markup=reply_markup)
    return START_ROUTES


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🟢Turn on", callback_data=str(ON_SERVER))],
        [InlineKeyboardButton("🔴Turn off", callback_data=str(OFF_SERVER))],
        [InlineKeyboardButton("️❎Menu", callback_data=str(BACK))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="⚙️Control", reply_markup=reply_markup
    )
    return SETTING_ROUTES


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = get_info()
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("️❎Menu", callback_data=str(BACK))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=answer, reply_markup=reply_markup
    )
    return INFO_ROUTES


async def choose_map(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choosing_map: str = ""
    map_number = update.callback_query.data
    if int(map_number) in list(maps_dict.values()):
        choosing_map = get_key(maps_dict, int(map_number))
    if choosing_map != "":
        if change_map(choosing_map):
            answer = f"🌎Map {choosing_map} successfully changed!"
        else:
            answer = f"❌Failed to change map to {choosing_map}!"
    else:
        answer = "🌎Select map"
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(key, callback_data=str(maps_dict[key]))] for key in maps] + \
               [[InlineKeyboardButton("❎Menu", callback_data=str(BACK))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=answer, reply_markup=reply_markup
    )
    return MAP_ROUTES


async def server_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if server_action(START_ACTION):
        answer = "🟢Server is on"
    else:
        answer = "❌Failed to turn on the server"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🟢Turn on", callback_data=str(ON_SERVER))],
        [InlineKeyboardButton("🔴Turn off", callback_data=str(OFF_SERVER))],
        [InlineKeyboardButton("❎Menu", callback_data=str(BACK))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=answer, reply_markup=reply_markup
    )
    return SETTING_ROUTES


async def server_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if server_action(STOP_ACTION):
        answer = "🔴Server is off"
    else:
        answer = "❌Failed to turn off the server"
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🟢Turn on", callback_data=str(ON_SERVER))],
        [InlineKeyboardButton("🔴Turn off", callback_data=str(OFF_SERVER))],
        [InlineKeyboardButton("❎Menu", callback_data=str(BACK))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=answer, reply_markup=reply_markup
    )
    return SETTING_ROUTES


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🌎Maps", callback_data=str(MAPS))],
        [InlineKeyboardButton("⚙️Control", callback_data=str(SETTINGS))],
        [InlineKeyboardButton("ℹ️Info", callback_data=str(INFO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.answer()
    await query.edit_message_text(
        text="Select menu item:", reply_markup=reply_markup
    )
    return START_ROUTES


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(choose_map, pattern="^" + str(MAPS) + "$"),
                CallbackQueryHandler(settings, pattern="^" + str(SETTINGS) + "$"),
                CallbackQueryHandler(info, pattern="^" + str(INFO) + "$"),
            ],
            # START_ROUTES, MAP_ROUTES, SETTING_ROUTES, INFO_ROUTES
            MAP_ROUTES: [CallbackQueryHandler(back, pattern="^" + str(BACK) + "$")] +
                        [CallbackQueryHandler(choose_map, pattern="^" + str(maps_dict[key]) + "$") for key in
                         maps],

            SETTING_ROUTES: [
                CallbackQueryHandler(back, pattern="^" + str(BACK) + "$"),
                CallbackQueryHandler(server_on, pattern="^" + str(ON_SERVER) + "$"),
                CallbackQueryHandler(server_off, pattern="^" + str(OFF_SERVER) + "$"),
            ],
            INFO_ROUTES: [
                CallbackQueryHandler(back, pattern="^" + str(BACK) + "$"),
            ],

        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
