import os
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("8748472237:AAHTRywNoC9l8M3-9FRcYBS52ETLjhG2fKo")

async def start(update, context):
    await update.message.reply_text("Bot is running!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot started...")

    app.run_polling()

if __name__ == "__main__":
    main()