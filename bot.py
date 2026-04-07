import os
import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running successfully!")

def main():
    print("=== BOT STARTING ===")

    try:
        # Show environment keys
        print("ENV KEYS:", list(os.environ.keys()))

        token = os.environ.get("8748472237:AAHTRywNoC9l8M3-9FRcYBS52ETLjhG2fKo")

        print("BOT_TOKEN exists:", bool(token))

        if not token:
            print("ERROR: BOT_TOKEN missing")
            sys.exit(1)

        print("Creating application...")

        app = ApplicationBuilder().token(token.strip()).build()

        app.add_handler(CommandHandler("start", start))

        print("Starting polling...")

        app.run_polling()

    except Exception as e:
        print("CRASH ERROR:", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()