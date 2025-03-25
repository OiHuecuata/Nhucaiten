import requests
import json

TELEGRAM_BOT_TOKEN = "token_api"
TELEGRAM_CHAT_ID = "id"

def send_telegram_file(file_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption
            }
            requests.post(url, data=data, files=files)
    except Exception as e:
        print(f"Lỗi gửi file Telegram: {str(e)}")

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn Telegram: {str(e)}")

def load_existing_data():
    try:
        with open("flights.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_json(flights_data, instance=None):
    with open("flights.json", "w", encoding="utf-8") as f:
        json.dump(flights_data, f, ensure_ascii=False, indent=4)
        
    if instance and hasattr(instance, 'db_manager'):
        if instance.db_manager and instance.db_manager.db_type != "off":
            success, message = instance.db_manager.save_to_database(flights_data)
            if not success:
                instance.log(f"Lỗi lưu database: {message}")
            else:
                instance.log(f"✅ {message}")

def save_error_log(departure, destination, date):
    try:
        with open("error.txt", "a", encoding="utf-8") as f:
            f.write(f"{departure}-{destination} {date} 1\n")
    except Exception as e:
        print(f"Lỗi khi lưu file error.txt: {str(e)}")
        
def main():
    print("Hoàn Đẹp Trai.")

if __name__=="__main__":
    main()
