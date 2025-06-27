import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai

BOT_TOKEN = "8039690445:AAG38YkaKel09yV7em1Q97fENwzQWyV7N_8"
GEMINI_API_KEY = "AIzaSyDbhLv968qzBUj2PlVneAe_oIymRl74IRM"


try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Error: {e}")
    exit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Saya Ravchell famili dari koala. Kirimkan saya pertanyaan apa saja.")

def get_gemini_reply(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {str(e)}")
        return f"Maaf, terjadi kesalahan saat berkomunikasi dengan AI: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")


    reply = await asyncio.to_thread(get_gemini_reply, question)
    
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
