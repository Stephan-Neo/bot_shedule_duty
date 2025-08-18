import asyncio
from telegram import Bot

TOKEN = "8310592279:AAGq7SUA2_v6XmP-JKN5RbbKF0eBnFnyc84"

async def get_chat_info():
    bot = Bot(token=TOKEN)
    
    try:
        # Получаем последние обновления
        updates = await bot.get_updates()
        
        if not updates:
            print("Бот не получил ни одного сообщения. Отправьте боту сообщение в ЛС или чате.")
            return
        
        for update in updates:
            if update.message:
                chat = update.message.chat
                print("\n=== Информация о чате ===")
                print(f"Chat ID: {chat.id}")
                print(f"Type: {chat.type}")
                print(f"Title: {getattr(chat, 'title', 'Private chat')}")
                
            elif update.channel_post:
                channel = update.channel_post.chat
                print("\n=== Информация о канале ===")
                print(f"Channel ID: {channel.id}")
                print(f"Channel Title: {channel.title}")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Запускаем асинхронную функцию
def main():
    asyncio.run(get_chat_info())

if __name__ == "__main__":
    main()