
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = "8748472237:AAHTRywNoC9l8M3-9FRcYBS52ETLjhG2fKo"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Test successful")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question="Sample Quiz Question",
        options=[
            "Option A",
            "Option B",
            "Option C",
            "Option D"
        ],
        type="quiz",
        correct_option_id=0
    )


async def error_handler(update, context):
    logging.error("Error:", exc_info=context.error)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("quiz", quiz))

    app.add_error_handler(error_handler)

    print("Bot started successfully")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
