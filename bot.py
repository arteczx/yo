import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

BOT_TOKEN = "8039690445:AAG38YkaKel09yV7em1Q97fENwzQWyV7N_8" 
GEMINI_API_KEY = "AIzaSyDbhLv968qzBUj2PlVneAe_oIymRl74IRM"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error: {e}")
    exit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Saya Ravchell Famili dari Koala. Kirimkan saya pertanyaan apa saja.")

def get_gemini_reply(prompt: str) -> str:
    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # Memeriksa apakah respons diblokir meskipun sudah ada pengaturan keamanan
        if not response.parts:
             return "Maaf, permintaan Anda tidak dapat diproses karena diblokir oleh filter keamanan."
        
        return response.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {str(e)}")
        return f"Maaf, terjadi kesalahan saat berkomunikasi dengan AI: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    reply = await asyncio.to_thread(get_gemini_reply, question)
    
    if not reply:
        await update.message.reply_text("Maaf, saya tidak bisa memberikan jawaban kosong.")
        return
        
    cleaned_reply = reply.replace('**', '').replace('*', '')
    
    MAX_MESSAGE_LENGTH = 4096

    if len(cleaned_reply) > MAX_MESSAGE_LENGTH:
        for i in range(0, len(cleaned_reply), MAX_MESSAGE_LENGTH):
            part = cleaned_reply[i:i + MAX_MESSAGE_LENGTH]
            try:
                await update.message.reply_text(part)
            except Exception as e:
                print(f"Gagal mengirim bagian pesan: {e}")
                await update.message.reply_text(f"Terjadi error saat mengirim balasan: {e}")
    else:
        try:
            await update.message.reply_text(cleaned_reply)
        except Exception as e:
            print(f"Gagal mengirim pesan: {e}")
            await update.message.reply_text(f"Terjadi error saat mengirim balasan: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
    
