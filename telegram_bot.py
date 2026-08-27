#!/usr/bin/env python3
"""
telegram_bot.py - Bot de Telegram COMPLETO para QuizFactory
Versão 2.0 - com botões, canal automático e anti-erro

COMO USAR:
1. No Telegram, fala com @BotFather -> /newbot -> nome: QuizFactoryBot -> guarda o TOKEN
2. No terminal:
   pip install python-telegram-bot edge-tts Pillow moviepy imageio-ffmpeg gTTS
   export TELEGRAM_TOKEN="123456:ABC-DEF..."
   python telegram_bot.py

COMANDOS:
- /start - menu com botões
- /quiz - gera vídeo aleatório (4 rondas)
- /custom - formato: /custom Ter dinheiro | Poder voar | 70% | 30%
- /canal - configura canal para auto-post
"""
import os
import json
import tempfile
import random
import logging
import asyncio
from pathlib import Path
from datetime import time

# Fix Pillow ANTIALIAS
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    print("❌ pip install python-telegram-bot")

from make_quiz import gerar_video_quiz
from generate_quizzes import generate_one_quiz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CANAL_ID = os.getenv("CANAL_ID", "")  # ex: @meucanal ou -100123456789

# --- TECLADO MENU ---
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 Quiz Aleatório (4 rondas)", callback_data="quiz_random")],
        [InlineKeyboardButton("⚡ Quiz Rápido (1 ronda)", callback_data="quiz_1")],
        [InlineKeyboardButton("📝 Como criar custom?", callback_data="help_custom")],
        [InlineKeyboardButton("📢 Configurar Canal", callback_data="setup_canal")],
    ]
    return InlineKeyboardMarkup(keyboard)

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎬 *QuizFactory Bot - Red vs Blue* 🔴🔵\n\n"
        "Eu gero vídeos virais de *Would You Rather* prontos para TikTok!\n\n"
        "👇 *Escolhe uma opção:*\n"
        "• Aleatório = 4 perguntas, 45 seg\n"
        "• Rápido = 1 pergunta, 12 seg (teste)\n"
        "• Custom = tu escreves as opções\n\n"
        "💡 *Dica:* Vídeos com 49% vs 51% geram mais comentários!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *Como criar quiz custom:*\n\n"
        "Envia:\n"
        "`/custom Ter dinheiro infinito | Poder voar | 70% | 30%`\n\n"
        "Formato:\n"
        "`opção A | opção B | %A | %B`\n\n"
        "Exemplos:\n"
        "`/custom Ser invisível | Ser super forte`\n"
        "`/custom Pizza todos os dias | Hambúrguer todos os dias | 55% | 45%`\n\n"
        "Se não puseres %, eu randomizo!",
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "quiz_random":
        await query.message.reply_text("🎬 A gerar quiz de 4 rondas... ⏳ demora 2-3 min")
        await gerar_e_enviar(update, context, num_rounds=4, chat_id=query.message.chat_id)

    elif query.data == "quiz_1":
        await query.message.reply_text("⚡ A gerar quiz rápido de 1 ronda... ⏳ 30 seg")
        await gerar_e_enviar(update, context, num_rounds=1, chat_id=query.message.chat_id)

    elif query.data == "help_custom":
        await help_cmd(update, context)

    elif query.data == "setup_canal":
        await query.message.reply_text(
            "📢 *Para auto-post no canal:*\n\n"
            "1. Cria um canal no Telegram\n"
            "2. Adiciona o bot como Admin no canal\n"
            "3. Pega o ID do canal (ex: @meucanal ou -100...)\n"
            "4. Define: `export CANAL_ID='@meucanal'`\n"
            "5. O bot vai postar automaticamente a cada 8h\n\n"
            "Comando manual: /postar_canal",
            parse_mode="Markdown"
        )

# --- FUNÇÃO CORE QUE GERA VÍDEO ---
async def gerar_e_enviar(update: Update, context: ContextTypes.DEFAULT_TYPE, num_rounds=4, custom_data=None, chat_id=None):
    if not chat_id:
        chat_id = update.effective_chat.id

    try:
        if custom_data:
            quiz_data = custom_data
        else:
            quiz_data = generate_one_quiz(num_rounds=num_rounds)

        tmp_json = tempfile.mktemp(suffix=".json")
        with open(tmp_json, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)

        tmp_mp4 = tempfile.mktemp(suffix=".mp4")

        # Gera vídeo (bloqueante, mas ok para bot pequeno)
        # Para não travar o bot, corre em thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: gerar_video_quiz(tmp_json, tmp_mp4, voice="en-US-AriaNeural", temp_dir="temp_audio"))

        # Legenda viral
        caption = "🔥 WOULD YOU RATHER? 🔴 vs 🔵\n\n"
        for i, q in enumerate(quiz_data, 1):
            caption += f"{i}. {q['option_a']} ({q['percent_a']}) vs {q['option_b']} ({q['percent_b']})\n"
        caption += "\n👇 Comenta a tua escolha! #wouldyourather #quiz #redvsblue"

        # Envia
        with open(tmp_mp4, 'rb') as vf:
            await context.bot.send_video(
                chat_id=chat_id,
                video=vf,
                caption=caption[:1024],  # limite Telegram
                supports_streaming=True
            )

        # Limpa
        if os.path.exists(tmp_json):
            os.remove(tmp_json)
        if os.path.exists(tmp_mp4):
            os.remove(tmp_mp4)

        await context.bot.send_message(chat_id=chat_id, text="✅ Vídeo enviado! Queres outro? /quiz", reply_markup=get_main_keyboard())

    except Exception as e:
        logger.exception(e)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Erro: {e}\nTenta /quiz de novo.")

# --- COMANDOS NORMAIS ---
async def quiz_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎲 A gerar quiz aleatório de 4 rondas... ⏳")
    await gerar_e_enviar(update, context, num_rounds=4)

async def quiz_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ A gerar quiz de 1 ronda (teste rápido)...")
    await gerar_e_enviar(update, context, num_rounds=1)

async def quiz_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/custom", "").strip()
    if "|" not in text:
        await update.message.reply_text("❌ Formato: /custom Opção A | Opção B | 70% | 30%\nEx: /custom Ter dinheiro | Poder voar | 72% | 28%")
        return

    try:
        parts = [p.strip() for p in text.split("|")]
        opt_a = parts[0]
        opt_b = parts[1]
        perc_a = parts[2] if len(parts) > 2 else f"{random.randint(30,70)}%"
        perc_b = parts[3] if len(parts) > 3 else f"{100 - int(perc_a.strip('%'))}%"

        quiz_data = [{"option_a": opt_a, "option_b": opt_b, "percent_a": perc_a, "percent_b": perc_b}]
        await update.message.reply_text(f"🎬 A gerar custom: {opt_a} VS {opt_b}...")
        await gerar_e_enviar(update, context, custom_data=quiz_data)

    except Exception as e:
        await update.message.reply_text(f"❌ Erro no formato: {e}")

async def postar_canal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not CANAL_ID:
        await update.message.reply_text("❌ Define primeiro: export CANAL_ID='@teucanal' e adiciona o bot como admin no canal")
        return
    await update.message.reply_text(f"📢 A postar no canal {CANAL_ID}...")
    await gerar_e_enviar(update, context, num_rounds=4, chat_id=CANAL_ID)
    await update.message.reply_text(f"✅ Postado no canal {CANAL_ID}!")

# --- AUTO POST JOB (a cada 8h) ---
async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    if not CANAL_ID:
        return
    logger.info(f"Auto post no canal {CANAL_ID}")
    try:
        quiz_data = generate_one_quiz(num_rounds=4)
        tmp_json = tempfile.mktemp(suffix=".json")
        with open(tmp_json, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2)
        tmp_mp4 = tempfile.mktemp(suffix=".mp4")
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: gerar_video_quiz(tmp_json, tmp_mp4, voice="en-US-AriaNeural", temp_dir="temp_audio"))

        with open(tmp_mp4, 'rb') as vf:
            await context.bot.send_video(chat_id=CANAL_ID, video=vf, caption="🔥 Novo Would You Rather! Comenta! #quiz")

        os.remove(tmp_json)
        os.remove(tmp_mp4)
    except Exception as e:
        logger.exception(f"Erro auto post: {e}")

def main():
    if not HAS_TELEGRAM:
        print("❌ pip install python-telegram-bot")
        return

    if not TOKEN:
        print("="*60)
        print("❌ TOKEN NÃO DEFINIDO!")
        print("="*60)
        print("1. Vai no Telegram -> @BotFather -> /newbot")
        print("2. Cria bot e copia o token tipo 123456:ABC-DEF...")
        print("3. No terminal:")
        print("   export TELEGRAM_TOKEN='teu_token_aqui'")
        print("   python telegram_bot.py")
        print("")
        print("No Windows:")
        print("   set TELEGRAM_TOKEN=teu_token_aqui")
        print("="*60)
        return

    print(f"🤖 Bot a iniciar com token {TOKEN[:10]}...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("quiz", quiz_random))
    app.add_handler(CommandHandler("quiz1", quiz_1))
    app.add_handler(CommandHandler("custom", quiz_custom))
    app.add_handler(CommandHandler("postar_canal", postar_canal))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Auto post a cada 8 horas se CANAL_ID definido
    if CANAL_ID:
        print(f"📢 Auto-post ativo para canal {CANAL_ID} a cada 8h")
        app.job_queue.run_repeating(auto_post_job, interval=8*3600, first=10)
    else:
        print("ℹ️ Sem CANAL_ID - auto-post desativado. Define export CANAL_ID='@teucanal' para ativar")

    print("✅ Bot online! Vai no Telegram e manda /start")
    print("   Pressiona Ctrl+C para parar")
    app.run_polling()

if __name__ == "__main__":
    main()
