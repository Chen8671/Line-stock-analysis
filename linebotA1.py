# -*- coding: utf-8 -*-

import os
import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('mXE1BzBQ67nBGrZGbBO0TEWrT3xy9h3rpk4sz+PGeC00bwwc3yvWz9BEANYMNpm0MqpSk7xfmEh6l2KEy/KFEAduvGPm3m7A++Sxl3eJTiSzeQlzZJhxXfDoiyEdfGnsDern1toKbzLJdDe/IvtFpwdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.environ.get('7c7b7ddfcfa323b252f5f4d81a4bff1d'))

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
        return "Error fetching the stock health data."

# 定義按鈕範本消息
buttons_template_message = TemplateSendMessage(
    alt_text='功能按鈕',
    template=ButtonsTemplate(
        thumbnail_image_url='https://example.com/image.jpg',  # 圖片網址，可選
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
