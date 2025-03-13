import os
import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = "T/EUr80xzlGCYpOUBsuORZdWpWwl/EYMxZRgnyorALxmo0xp5ti+2ELOII85fYQZ1bf/tNbOy3Y2T3GFPKBrOGsJd1dkQ8t2Rhkh5Fc9SSq1Jn/+dTZljEyGzEdUfoL1n0LsPdKagWWHk5ZEyd8aygdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "a2180e40b0a6c2ef14fde47b59650d60"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.history(period="1d")
        if stock_info.empty:
            return "查無此股票代號，請確認是否輸入正確！"

        last_price = stock_info["Close"].iloc[-1]
        prev_price = stock_info["Open"].iloc[-1]
        change_percent = ((last_price - prev_price) / prev_price) * 100

        return (f"股票代號：{symbol.upper()}\n"
                f"最新價格：${last_price:.2f}\n"
                f"漲跌幅：{change_percent:.2f}%")
    except Exception as e:
        return f"無法查詢股票資訊，錯誤：{str(e)}"


@app.route("/", methods=["GET"])
def home():
    return "股票查詢機器人已運行！"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip().upper()  # 轉大寫
    reply_text = get_stock_price(user_input)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
