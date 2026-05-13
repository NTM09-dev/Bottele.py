import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CẤU HÌNH ---
TOKEN = '8413720640:AAEcijmXUBEwKwD9Q28RO39OvUYu3KtWnXc'
ADMIN_ID = 8195111209  # Thay bằng ID Telegram của bạn
CHATS_FILE = 'chats.txt' # File lưu danh sách các box

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Hàm lưu ID vào file (để tránh mất dữ liệu khi restart bot)
def save_chat_id(chat_id):
    chat_id = str(chat_id)
    with open(CHATS_FILE, 'a+') as f:
        f.seek(0)
        ids = f.read().splitlines()
        if chat_id not in ids:
            f.write(chat_id + '\n')

# Khi bot được thêm vào box hoặc có tin nhắn mới, nó sẽ lưu chat_id
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat:
        save_chat_id(update.effective_chat.id)

# Lệnh gửi thông báo (Chỉ Admin)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra quyền Admin
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    # Lấy nội dung thông báo
    message_to_send = " ".join(context.args)
    if not message_to_send:
        await update.message.reply_text("⚠️ Vui lòng nhập nội dung: `/broadcast Nội dung...`", parse_mode='Markdown')
        return

    # Đọc danh sách chat_id
    try:
        with open(CHATS_FILE, 'r') as f:
            chat_ids = f.read().splitlines()
    except FileNotFoundError:
        await update.message.reply_text("Chưa có dữ liệu box nào.")
        return

    success = 0
    fail = 0

    # Gửi tin nhắn
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message_to_send)
            success += 1
        except Exception as e:
            print(f"Lỗi gửi đến {chat_id}: {e}")
            fail += 1

    await update.message.reply_text(f"✅ Đã gửi xong!\n- Thành công: {success}\n- Thất bại: {fail}")

def main():
    app = Application.builder().token(TOKEN).build()

    # Lưu chat_id mỗi khi có tương tác
    app.add_handler(MessageHandler(filters.ALL, track_chats), group=0)
    
    # Lệnh broadcast cho admin
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
