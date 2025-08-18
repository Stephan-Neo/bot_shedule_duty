import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    CallbackContext
)
import datetime
import os
from tabulate import tabulate

# Конфигурация
TOKEN = "8310592279:AAGq7SUA2_v6XmP-JKN5RbbKF0eBnFnyc84"
EXCEL_FILE = "exc.xlsx"
CHANNEL_ID = "-1002257875520"

def load_schedule():
    if not os.path.exists(EXCEL_FILE):
        return pd.DataFrame(columns=['Дата', 'Дежурный'])
    df = pd.read_excel(EXCEL_FILE)
    df['Дата'] = pd.to_datetime(df['Дата']).dt.date
    return df.sort_values('Дата')

def get_duty(date):
    df = load_schedule()
    duty = df[df['Дата'] == date]
    return duty.iloc[0]['Дежурный'] if not duty.empty else None

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 Сегодня", callback_data='duty_today'),
         InlineKeyboardButton("⏩ Завтра", callback_data='duty_tomorrow')],
        [InlineKeyboardButton("📋 Полное расписание", callback_data='full_schedule')],
    ]
    return InlineKeyboardMarkup(keyboard)

def format_single_duty(date, duty):
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    weekday = weekdays[date.weekday()]
    return (
        f"📅 *Дата:* {date.strftime('%d.%m.%Y')} ({weekday})\n"
        f"👤 *Дежурный:* _{duty}_"
    )

def format_all_duties(df):
    headers = ["📅 Дата", "👤 Дежурный"]
    table_data = [[row['Дата'].strftime('%d.%m.%Y'), row['Дежурный']] for _, row in df.iterrows()]
    return (
        "📋 *Расписание дежурных:*\n"
        "```\n"
        f"{tabulate(table_data, headers=headers, tablefmt='grid')}\n"
        "```"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    today = datetime.date.today()
    df = load_schedule()
    
    try:
        if query.data == 'duty_today':
            duty = get_duty(today)
            new_text = format_single_duty(today, duty) if duty else "📭 На сегодня дежурный не назначен"
        elif query.data == 'duty_tomorrow':
            tomorrow = today + datetime.timedelta(days=1)
            duty = get_duty(tomorrow)
            new_text = format_single_duty(tomorrow, duty) if duty else "📭 На завтра дежурный не назначен"
        elif query.data == 'full_schedule':
            new_text = format_all_duties(df) if not df.empty else "📭 Расписание пустое"
        
        # Проверяем изменения
        if new_text != query.message.text:
            await query.edit_message_text(
                text=new_text,
                parse_mode='Markdown',
                reply_markup=get_main_keyboard()
            )
        else:
            await query.answer("✅ Информация актуальна")
            
    except Exception as e:
        print(f"Error: {e}")
        await query.answer("⚠️ Ошибка, попробуйте позже")

async def send_channel_message(context: CallbackContext):
    today = datetime.date.today()
    duty = get_duty(today)
    
    text = (
        "📢 *Дежурство на сегодня*\n\n"
        f"{format_single_duty(today, duty) if duty else '📭 На сегодня дежурный не назначен'}"
    )
    
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        print(f"Channel message error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 Управление дежурствами:",
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Start error: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.answer("⚠️ Ошибка обработки запроса")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Ежедневное уведомление
    job_queue = application.job_queue
    job_queue.run_daily(
        send_channel_message,
        time=datetime.time(hour=15, minute=0),
        days=tuple(range(7))
    )
    application.run_polling()

if __name__ == '__main__':
    main()