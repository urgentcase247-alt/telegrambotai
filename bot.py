import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# ENV VARIABLES
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# VALIDATION (important for debugging)
if not TOKEN:
    raise ValueError("BOT_TOKEN is missing")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing")

# Groq client
client = Groq(api_key=GROQ_API_KEY)

# HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I'm alive 🚀 (webhook mode)")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_text}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    port = int(os.environ.get("PORT", 10000))

    # 🔥 IMPORTANT: webhook mode for Render
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()