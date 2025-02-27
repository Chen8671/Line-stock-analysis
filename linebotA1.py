import os
import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

app = Flask(__name__)

# 從環境變數中獲取 LINE bot 的 Access Token 和 Channel Secret
line_access_token = os.environ.get('D9zBfnRl2A6H/Vvj+DH0CpyBLIjdLYHmgsVI+ndsHssd+dwUwy5gtyw3rvx4Cg4X0skcPSeGrb7YIYWkLmrxAzUWBG6uQ2HJtb1gayfIHkFcDjLxdDb+pxLbLc//i9xc/IsKnDXUAp1MMurIq3gmqQdB04t89/1O/w1cDnyilFU=')
line_channel_secret = os.environ.get('5b750f8f51ea241fe0a6579fdcf61ed5')

# 如果未找到環境變數，則顯示錯誤
if not line_access_token or not line_channel_secret:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未正確設置")

# 初始化 LineBotApi 和 WebhookHandler
line_bot_api = LineBotApi(line_access_token)
handler = WebhookHandler(line_channel_secret)

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
