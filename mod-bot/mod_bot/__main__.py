import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus
import dotenv


# Token extracted from environment
dotenv.load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Whitelist of usernames (replace with actual usernames)
WHITELIST = ['user1', 'user2']

# Dictionary to store mute status for each chat
MUTE_STATUS = {}

# Dictionary to store muted users for each chat
MUTED_USERS = {}

async def toggle_mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat.type.endswith('group'):
        await update.message.reply_text("This command can only be used in groups.")
        return

    # Check if the user invoking the command is an admin
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("Only administrators can use this command.")
        return

    chat_id = update.effective_chat.id
    
    if chat_id in MUTE_STATUS and MUTE_STATUS[chat_id]:
        MUTE_STATUS[chat_id] = False
        await update.message.reply_text("Mute all has been deactivated. Unmuting all previously muted users.")
        await unmute_all(context, chat_id)
    else:
        MUTE_STATUS[chat_id] = True
        MUTED_USERS[chat_id] = set()
        await update.message.reply_text("Mute all has been activated. All members except those in the whitelist will be muted.")

async def unmute_all(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    if chat_id in MUTED_USERS:
        for user_id in MUTED_USERS[chat_id]:
            try:
                await context.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions={"can_send_messages": True, "can_send_media_messages": True, "can_send_other_messages": True}
                )
            except Exception as e:
                print(f"Failed to unmute user {user_id}: {str(e)}")
        MUTED_USERS[chat_id].clear()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id in MUTE_STATUS and MUTE_STATUS[chat_id]:
        if user.username and user.username.lower() not in [username.lower() for username in WHITELIST]:
            try:
                await context.bot.restrict_chat_member(
                    chat_id,
                    user.id,
                    permissions={"can_send_messages": False}
                )
                MUTED_USERS.setdefault(chat_id, set()).add(user.id)
                await update.message.reply_text(f"@{user.username} has been muted.")
            except Exception as e:
                print(f"Failed to mute user: {str(e)}")

async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a username to unmute.")
        return

    chat_id = update.effective_chat.id
    username = context.args[0].replace('@', '')

    try:
        user = next(member for member in await update.effective_chat.get_members() if member.user.username and member.user.username.lower() == username.lower())
        await context.bot.restrict_chat_member(
            chat_id,
            user.user.id,
            permissions={"can_send_messages": True, "can_send_media_messages": True, "can_send_other_messages": True}
        )
        if chat_id in MUTED_USERS and user.user.id in MUTED_USERS[chat_id]:
            MUTED_USERS[chat_id].remove(user.user.id)
        await update.message.reply_text(f"@{username} has been unmuted.")
    except StopIteration:
        await update.message.reply_text(f"Couldn't find user @{username} in this chat.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred while trying to unmute @{username}: {str(e)}")

async def add_to_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a username to add to the whitelist.")
        return

    username = context.args[0].replace('@', '')
    if username.lower() not in [u.lower() for u in WHITELIST]:
        WHITELIST.append(username)
        await update.message.reply_text(f"@{username} has been added to the whitelist.")
    else:
        await update.message.reply_text(f"@{username} is already in the whitelist.")

async def remove_from_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a username to remove from the whitelist.")
        return

    username = context.args[0].replace('@', '')
    lower_whitelist = [u.lower() for u in WHITELIST]
    if username.lower() in lower_whitelist:
        index = lower_whitelist.index(username.lower())
        del WHITELIST[index]
        await update.message.reply_text(f"@{username} has been removed from the whitelist.")
    else:
        await update.message.reply_text(f"@{username} is not in the whitelist.")

async def show_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    whitelist_text = "\n".join([f"@{username}" for username in WHITELIST])
    await update.message.reply_text(f"Current whitelist:\n{whitelist_text}")

async def show_muted_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat.type.endswith('group'):
        await update.message.reply_text("This command can only be used in groups.")
        return

    # Check if the user invoking the command is an admin
    user = await update.effective_chat.get_member(update.effective_user.id)
    if user.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("Only administrators can use this command.")
        return

    chat_id = update.effective_chat.id

    if chat_id not in MUTED_USERS or not MUTED_USERS[chat_id]:
        await update.message.reply_text("There are no muted members in this group.")
        return

    muted_members_text = "Muted members in this group:\n"
    for user_id in MUTED_USERS[chat_id]:
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            username = member.user.username or "No username"
            first_name = member.user.first_name or "No first name"
            muted_members_text += f"- @{username} (ID: {user_id}, Name: {first_name})\n"
        except Exception as e:
            print(f"Error getting info for user {user_id}: {str(e)}")
            muted_members_text += f"- User ID: {user_id} (Unable to fetch details)\n"

    await update.message.reply_text(muted_members_text)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("togglemute", toggle_mute))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("addwhitelist", add_to_whitelist))
    application.add_handler(CommandHandler("removewhitelist", remove_from_whitelist))
    application.add_handler(CommandHandler("showwhitelist", show_whitelist))
    application.add_handler(CommandHandler("showmuted", show_muted_members))  # New command handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()