import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Read token from environment
TOKEN = os.getenv("8748472237:AAHTRywNoC9l8M3-9FRcYBS52ETLjhG2fKo")

# Safety check for token
if not TOKEN:
    raise ValueError("BOT_TOKEN is missing. Check Render Environment Variables.")

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running successfully on Render!")

# Main function
def main():
    print("Starting bot...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot started successfully")

    app.run_polling()

if __name__ == "__main__":
    main()