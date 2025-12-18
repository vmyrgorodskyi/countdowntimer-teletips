#Copyright ©️ 2021 TeLe TiPs. All Rights Reserved
#Mixed Configuration: Env Vars for Secrets, Top-Level Config for Preferences

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import asyncio
from plugins.teletips_t import *
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.raw.functions.messages import UpdatePinnedMessage

# ==============================================================================
# ========================= USER CONFIGURATION =================================
# ==============================================================================
# Modify these values directly in the code:

# 1. THE MESSAGE TO SHOW WHEN COUNTDOWN FINISHES
# (This replaces "Beep! Beep!! TIME'S UP!!!")
CUSTOM_END_MESSAGE = "🚨 The prices have increased! / Цены увеличились 🚨"

# 2. REFRESH RATE (In Seconds)
# How often to update the message for long timers (longer than 1 minute).
# Setting this to 60 (1 minute) is HIGHLY recommended to prevent Telegram bans/freezing.
REFRESH_RATE_LONG = 60

# ==============================================================================
# ======================= END OF USER CONFIGURATION ============================
# ==============================================================================

# Initialize Bot using Render Environment Variables (Secrets)
bot = Client(
    "Countdown-TeLeTiPs",
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"],
    bot_token = os.environ["BOT_TOKEN"]
)

# Load Footer Message from Render Environment Variables
# Priority: CUSTOM_FOOTER -> FOOTER_MESSAGE -> Default Text
footer_message = os.environ.get("CUSTOM_FOOTER", os.environ.get("FOOTER_MESSAGE", "Countdown by TeLe TiPs"))

stoptimer = False

TELETIPS_MAIN_MENU_BUTTONS = [
            [
                InlineKeyboardButton('❓ HELP', callback_data="HELP_CALLBACK")
            ],
            [
                InlineKeyboardButton('👥 SUPPORT', callback_data="GROUP_CALLBACK"),
                InlineKeyboardButton('📣 CHANNEL', url='https://t.me/teletipsofficialchannel'),
                InlineKeyboardButton('👨‍💻 CREATOR', url='https://t.me/teIetips')
            ],
            [
                InlineKeyboardButton('➕ CREATE YOUR BOT ➕', callback_data="TUTORIAL_CALLBACK")
            ]
        ]

@bot.on_message(filters.command(['start','help']) & filters.private)
async def start(client, message):
    text = START_TEXT
    reply_markup = InlineKeyboardMarkup(TELETIPS_MAIN_MENU_BUTTONS)
    await message.reply(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

@bot.on_callback_query()
async def callback_query(client: Client, query: CallbackQuery):
    if query.data=="HELP_CALLBACK":
        TELETIPS_HELP_BUTTONS = [[InlineKeyboardButton("⬅️ BACK", callback_data="START_CALLBACK")]]
        reply_markup = InlineKeyboardMarkup(TELETIPS_HELP_BUTTONS)
        try:
            await query.edit_message_text(HELP_TEXT, reply_markup=reply_markup)
        except MessageNotModified:
            pass
    elif query.data=="GROUP_CALLBACK":
        TELETIPS_GROUP_BUTTONS = [
            [InlineKeyboardButton("TeLe TiPs Chat [EN]", url="https://t.me/teletipsofficialontopicchat")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="START_CALLBACK")]
        ]
        reply_markup = InlineKeyboardMarkup(TELETIPS_GROUP_BUTTONS)
        try:
            await query.edit_message_text(GROUP_TEXT, reply_markup=reply_markup)
        except MessageNotModified:
            pass    
    elif query.data=="TUTORIAL_CALLBACK":
        TELETIPS_TUTORIAL_BUTTONS = [
            [InlineKeyboardButton("🎥 Video", url="https://youtu.be/nYSrgdIYdTw")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="START_CALLBACK")]
        ]
        reply_markup = InlineKeyboardMarkup(TELETIPS_TUTORIAL_BUTTONS)
        try:
            await query.edit_message_text(TUTORIAL_TEXT, reply_markup=reply_markup)
        except MessageNotModified:
            pass      
    elif query.data=="START_CALLBACK":
        reply_markup = InlineKeyboardMarkup(TELETIPS_MAIN_MENU_BUTTONS)
        try:
            await query.edit_message_text(START_TEXT, reply_markup=reply_markup)
        except MessageNotModified:
            pass    

@bot.on_message(filters.command('set'))
async def set_timer(client, message):
    global stoptimer
    try:
        if message.chat.id>0:
            return await message.reply('⛔️ Try this command in a **group chat**.')
        elif not (await client.get_chat_member(message.chat.id,message.from_user.id)).privileges:
            return await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')    
        elif len(message.command)<3:
            return await message.reply('❌ **Incorrect format.**\n\n✅ Format should be like,\n<code> /set seconds "event"</code>\n\n**Example**:\n <code>/set 600 "Sales Event"</code>')    
        else:
            user_input_time = int(message.command[1])
            user_input_event = str(message.command[2])
            get_user_input_time = await bot.send_message(message.chat.id, user_input_time)
            await get_user_input_time.pin()
            if stoptimer: stoptimer = False
            
            # --- LOGIC START ---
            
            # Case 1: Very Short Timer (Under 1 minute) - Updates every 1 second (Standard behavior)
            if user_input_time < 60:
                 while user_input_time and not stoptimer:
                    s=user_input_time%60
                    Countdown_TeLe_TiPs='{}\n\n⏳ {:02d}**s**\n\n<i>{}</i>'.format(user_input_event, s, footer_message)
                    try:
                        finish_countdown = await get_user_input_time.edit(Countdown_TeLe_TiPs)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception:
                        pass
                    await asyncio.sleep(1)
                    user_input_time -=1
                 await finish_countdown.edit(CUSTOM_END_MESSAGE)

            # Case 2: Long Timer (1 minute or more) - Updates every REFRESH_RATE_LONG (60s default)
            else:
                while user_input_time > 0 and not stoptimer:
                    d=user_input_time//(3600*24)
                    h=user_input_time%(3600*24)//3600
                    m=user_input_time%3600//60
                    
                    # Clean Display Logic:
                    # If days exist, show Days:Hours:Minutes
                    # If no days, show Hours:Minutes
                    # SECONDS ARE HIDDEN to match the 1-minute update cycle
                    
                    if d > 0:
                        Countdown_TeLe_TiPs='{}\n\n⏳ {:02d}**d** : {:02d}**h** : {:02d}**m**\n\n<i>{}</i>'.format(user_input_event, d, h, m, footer_message)
                    else:
                        Countdown_TeLe_TiPs='{}\n\n⏳ {:02d}**h** : {:02d}**m**\n\n<i>{}</i>'.format(user_input_event, h, m, footer_message)

                    try:
                        finish_countdown = await get_user_input_time.edit(Countdown_TeLe_TiPs)
                    except FloodWait as e:
                        print(f"FloodWait: Sleeping {e.value}s")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        pass
                    
                    # Wait for the configured refresh rate (e.g., 60 seconds)
                    await asyncio.sleep(REFRESH_RATE_LONG)
                    user_input_time -= REFRESH_RATE_LONG
                
                await finish_countdown.edit(CUSTOM_END_MESSAGE)
            
    except FloodWait as e:
        await asyncio.sleep(e.value)

@bot.on_message(filters.command('stopc'))
async def stop_timer(Client, message):
    global stoptimer
    try:
        if (await bot.get_chat_member(message.chat.id,message.from_user.id)).privileges:
            stoptimer = True
            await message.reply('🛑 Countdown stopped.')
        else:
            await message.reply('👮🏻‍♂️ Sorry, **only admins** can execute this command.')
    except FloodWait as e:
        await asyncio.sleep(e.value)

print("Countdown Timer is alive!")
bot.run()
