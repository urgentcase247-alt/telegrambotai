import os
import sqlite3
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from groq import Groq

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
# Stores conversation history for each user
conversation_history = {}
# SQLite database
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")

conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is now live with Groq AI!")
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Create memory for new users
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {
                "role": "system",
                "content": "You are a helpful, intelligent AI assistant like ChatGPT."
            }
        ]

    # Add user's message
    conversation_history[user_id].append(
        {"role": "user", "content": user_text}
    )

    # Keep only the last 20 messages (+ system prompt)
    if len(conversation_history[user_id]) > 21:
        conversation_history[user_id] = (
            [conversation_history[user_id][0]]
            + conversation_history[user_id][-20:]
        )

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation_history[user_id]
        )

        reply = response.choices[0].message.content

        # Save the assistant's reply
        conversation_history[user_id].append(
            {"role": "assistant", "content": reply}
        )

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Bot is running with Groq...")
app.run_polling()