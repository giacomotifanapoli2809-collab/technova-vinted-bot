import os
import json
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = Path(__file__).parent
FILE_FILTRI = BASE_DIR / "filtri.json"

MARCHE = [
    "Gucci",
    "Prada",
    "Louis Vuitton",
    "Fendi",
    "Burberry"
]

logging.basicConfig(level=logging.INFO)


def carica():
    if not FILE_FILTRI.exists():
        return {}
    try:
        return json.loads(FILE_FILTRI.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def salva(dati):
    FILE_FILTRI.write_text(
        json.dumps(dati, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )


def chat_id(update):
    return str(update.effective_chat.id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 TECHNOVA VINTED BOT\n\n"
        "📋 COMANDI DISPONIBILI\n\n"
        "/ricerche - Visualizza le 5 marche\n"
        "/imposta - Imposta marche e prezzi\n"
        "/filtri - Visualizza i filtri\n"
        "/testnotifica - Prova Telegram\n"
        "/reset - Cancella i filtri\n\n"
        "Prezzo predefinito: 10-50 €"
    )


async def ricerche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 LE TUE RICERCHE\n\n" +
        "\n".join("🏷 " + marca for marca in MARCHE)
    )


async def imposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parti = update.message.text.split()

    if len(parti) < 4:
        await update.message.reply_text(
            "Formato:\n"
            "/imposta Gucci, Prada, Louis Vuitton, Fendi, Burberry 10 50"
        )
        return

    try:
        minimo = float(parti[-2].replace(",", "."))
        massimo = float(parti[-1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ Prezzi non validi.")
        return

    marche = [
        m.strip()
        for m in " ".join(parti[1:-2]).split(",")
        if m.strip()
    ]

    if not marche or minimo < 0 or massimo < minimo:
        await update.message.reply_text("❌ Controlla marche e prezzi.")
        return

    dati = carica()
    dati[chat_id(update)] = {
        "marche": marche,
        "minimo": minimo,
        "massimo": massimo
    }
    salva(dati)

    await update.message.reply_text(
        "✅ FILTRI SALVATI\n\n"
        f"Marche: {', '.join(marche)}\n"
        f"Prezzo minimo: {minimo:.2f} €\n"
        f"Prezzo massimo: {massimo:.2f} €"
    )


async def filtri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtro = carica().get(chat_id(update))

    if not filtro:
        await update.message.reply_text("⚠️ Nessun filtro. Usa /imposta.")
        return

    await update.message.reply_text(
        "🔎 I TUOI FILTRI\n\n"
        f"Marche: {', '.join(filtro['marche'])}\n"
        f"Minimo: {filtro['minimo']:.2f} €\n"
        f"Massimo: {filtro['massimo']:.2f} €"
    )


async def testnotifica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔔 TECHNOVA VINTED BOT\n\n"
        "✅ Telegram collegato correttamente!\n"
        "📡 Pronto per il collegamento a una fonte autorizzata di annunci."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dati = carica()
    dati.pop(chat_id(update), None)
    salva(dati)
    await update.message.reply_text("🗑 Filtri cancellati.")


async def errore(update, context):
    logging.error("Errore Telegram", exc_info=context.error)


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN non configurato.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ricerche", ricerche))
    app.add_handler(CommandHandler("imposta", imposta))
    app.add_handler(CommandHandler("filtri", filtri))
    app.add_handler(CommandHandler("testnotifica", testnotifica))
    app.add_handler(CommandHandler("reset", reset))
    app.add_error_handler(errore)

    print("TECHNOVA VINTED BOT AVVIATO", flush=True)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
