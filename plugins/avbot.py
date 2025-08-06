from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from Script import script
from utils import check_verification, get_token
from info import AUTH_PICS, BATCH_VERIFY, VERIFY, HOW_TO_VERIFY, AUTH_CHANNEL, ENABLE_LIMIT, RATE_LIMIT_TIMEOUT, MAX_FILES, BOT_USERNAME
import asyncio, time

rate_limit = {}

async def is_user_joined(bot, message: Message) -> bool:
    user_id = message.from_user.id
    bot_user = await bot.get_me()    
    not_joined_channels = []
    for channel_id in AUTH_CHANNEL:
        try:
            await bot.get_chat_member(channel_id, user_id)
        except UserNotParticipant:
            try:
                chat = await bot.get_chat(channel_id)
                try:
                    invite_link = await bot.export_chat_invite_link(channel_id)
                except ChatAdminRequired:
                    await message.reply_text(
                        text = (
                            "<i>🔒 Bᴏᴛ ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.\n"
                            "Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ:</i> "
                            "<b><a href='https://t.me/darkworld008'>[ ᴄʟɪᴄᴋ ʜᴇʀᴇ ]</a></b>"
                        ),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    return False
                not_joined_channels.append((chat.title, invite_link))
            except Exception as e:
                print(f"[ERROR] Chat fetch failed: {e}")
                continue
        except Exception as e:
            print(f"[ERROR] get_chat_member failed: {e}")
            continue

    if not_joined_channels:
        buttons = [
            [InlineKeyboardButton(f"[{i+1}] {title}", url=link)]
            for i, (title, link) in enumerate(not_joined_channels)
        ]
        buttons.append([
            InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{bot_user.username}?start=start")
        ])
        await message.reply_photo(
            photo=AUTH_PICS,
            caption=script.AUTH_TXT.format(message.from_user.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
        return False

    return True
    
async def av_verification(client, message):
    user_id = message.from_user.id
    if VERIFY and not await check_verification(client, user_id):
        btn = [[
            InlineKeyboardButton("✅️ ᴠᴇʀɪғʏ ✅️", url=await get_token(client, user_id, f"https://t.me/{BOT_USERNAME}?start=")),
            InlineKeyboardButton("⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ⁉️", url=HOW_TO_VERIFY)
        ],[
            InlineKeyboardButton("😁 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ - ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ 😁", callback_data='seeplans')
        ]]
        d = await message.reply_text(
            text=script.VERIFICATION_TEXT.format(message.from_user.mention),
            protect_content=False,
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(600)
        await d.delete()
        await message.delete()
        return False
    return True

async def av_x_verification(client, message):
    user_id = message.from_user.id
    if BATCH_VERIFY and not await check_verification(client, user_id):
        btn = [[
            InlineKeyboardButton("✅️ ᴠᴇʀɪғʏ ✅️", url=await get_token(client, user_id, f"https://t.me/{BOT_USERNAME}?start=")),
            InlineKeyboardButton("⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ⁉️", url=HOW_TO_VERIFY)
        ],[
            InlineKeyboardButton("😁 ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ - ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ 😁", callback_data='seeplans')
        ]]
        d = await message.reply_text(
            text=script.VERIFICATION_TEXT.format(message.from_user.mention),
            protect_content=False,
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(600)
        await d.delete()
        await message.delete()
        return False
    return True
    
async def is_user_allowed(user_id):
    """📌 यह फंक्शन चेक करेगा कि यूजर की फाइल लिमिट खत्म हुई है या नहीं"""
    current_time = time.time()

    if ENABLE_LIMIT:
        if user_id in rate_limit:
            file_count, last_time = rate_limit[user_id]
            if file_count >= MAX_FILES and (current_time - last_time) < RATE_LIMIT_TIMEOUT:
                remaining_time = int(RATE_LIMIT_TIMEOUT - (current_time - last_time))
                return False, remaining_time  # ❌ Limit Exceeded
            elif file_count >= MAX_FILES:
                rate_limit[user_id] = [1, current_time]  # ✅ Reset Limit
            else:
                rate_limit[user_id][0] += 1
        else:
            rate_limit[user_id] = [1, current_time]

    return True, 0  # ✅ Allowed
