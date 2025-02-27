import os
import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

app = Flask(__name__)

# 用正確的 CHANNEL_ACCESS_TOKEN 和 CHANNEL_SECRET 替換下面的字串
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))  # 假設環境變數有設置正確的 ACCESS TOKEN
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))  # 假設環境變數有設置正確的 SECRET

# 查詢股票健康狀況的函數
def get_stock_health(stock_code):
    stock = yf.Ticker(stock_code)
    if stock.info:
        valuation = stock.info.get('forwardPE', 'N/A')
        growth = stock.info.get('earningsGrowth', 'N/A')
        financials = stock.info.get('financialCurrency', 'N/A')
        technicals = stock.info.get('fiftyDayAverage', 'N/A')
        risk = stock.info.get('beta', 'N/A')
        competition = 'N/A'  # Yahoo Finance doesn't provide competition info directly
        news = 'N/A'  # For simplicity, not fetching news in this example
        return (f"股票代碼 {stock_code} 的健康狀況：\n"
                f"估值（前瞻市盈率）：{valuation}\n"
                f"成長（收益成長）：{growth}\n"
                f"財務狀況（財務貨幣）：{financials}\n"
                f"技術分析（50 日均價）：{technicals}\n"
                f"風險評估（Beta）：{risk}\n"
                f"競爭分析：{competition}\n"
                f"近期新聞和事件：{news}")
    else:
        return "無法獲取股票健康資料，請檢查股票代碼。"

# 定義按鈕範本消息
buttons_template_message = TemplateSendMessage(
    alt_text='功能按鈕',
    template=ButtonsTemplate(
        thumbnail_image_url='https://example.com/image.jpg',  # 確保圖片 URL 是有效的
        title='選擇功能',
        text='請選擇以下其中一項功能',
        actions=[
            MessageTemplateAction(
                label='股票健檢',
                text='股票健檢'
            ),
            # 您可以根據需求增加更多功能按鈕
        ]
    )
)

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
    user_input = event.message.text.strip()

    if user_input == '股票健檢':
        line_bot_api.reply_message(event.reply_token, buttons_template_message)
    elif user_input.isalnum() and 4 <= len(user_input) <= 6:
        result = get_stock_health(user_input)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入有效的股票代碼（4 至 6 位數的字母或數字）。"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
