import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import sqlite3

app = Flask(__name__)

line_bot_api = LineBotApi('T/EUr80xzlGCYpOUBsuORZdWpWwl/EYMxZRgnyorALxmo0xp5ti+2ELOII85fYQZ1bf/tNbOy3Y2T3GFPKBrOGsJd1dkQ8t2Rhkh5Fc9SSq1Jn/+dTZljEyGzEdUfoL1n0LsPdKagWWHk5ZEyd8aygdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a2180e40b0a6c2ef14fde47b59650d60')

# SQLite 資料庫文件路徑
DB_FILE_PATH = 'stock_data.db'

# 初始化 SQLite 資料庫
if not os.path.exists(DB_FILE_PATH):
    conn = sqlite3.connect(DB_FILE_PATH)
    c = conn.cursor()
    # 建立股票資料表
    c.execute('''CREATE TABLE IF NOT EXISTS stocks
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     stock_symbol TEXT UNIQUE,
                     stock_name TEXT,
                     last_price REAL,
                     change_percent REAL)''')
    conn.commit()
    conn.close()

# 查詢股票價格的函數
def fetch_stock_data(stock_symbol):
    api_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey=YOUR_API_KEY'
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            global_quote = data.get("Global Quote", {})
            if global_quote:
                last_price = float(global_quote.get("05. price", 0))
                change_percent = global_quote.get("10. change percent", "0%")
                return last_price, change_percent
            else:
                return None, None
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None

# Line Bot 的 Webhook 處理
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理使用者發送的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip().upper()
    
    # 檢查是否為股票代號
    if user_input.isalnum():
        # 查詢股票數據
        last_price, change_percent = fetch_stock_data(user_input)
        if last_price is not None:
            reply_message = (f"股票代號：{user_input}\n"
                             f"最新價格：${last_price:.2f}\n"
                             f"漲跌幅：{change_percent}")
        else:
            reply_message = f"無法找到股票代號 {user_input} 的相關數據，請檢查後重新輸入。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入有效的股票代號。"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
