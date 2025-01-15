# -*- coding: utf-8 -*-

import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('mXE1BzBQ67nBGrZGbBO0TEWrT3xy9h3rpk4sz+PGeC00bwwc3yvWz9BEANYMNpm0MqpSk7xfmEh6l2KEy/KFEAduvGPm3m7A++Sxl3eJTiSzeQlzZJhxXfDoiyEdfGnsDern1toKbzLJdDe/IvtFpwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7c7b7ddfcfa323b252f5f4d81a4bff1d')

# 查詢股票健康狀況的函數
def get_stock_health(stock_code):
    url = f'https://api.example.com/stock_health/{stock_code}'  # 假設這是一個可以查詢股票健康狀況的 API
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            valuation = data['valuation']
            growth = data['growth']
            financials = data['financials']
            technicals = data['technicals']
            risk = data['risk']
            competition = data['competition']
            news = data['news']
            return (f"股票代碼 {stock_code} 的健康狀況：\n"
                    f"估值：{valuation}\n"
                    f"成長：{growth}\n"
                    f"財務狀況：{financials}\n"
                    f"技術分析：{technicals}\n"
                    f"風險評估：{risk}\n"
                    f"競爭分析：{competition}\n"
                    f"近期新聞和事件：{news}")
        else:
            return "Error fetching the stock health data."
    except requests.exceptions.Timeout:
        return "Connection timed out."
    except requests.exceptions.ConnectionError:
        return "Connection error occurred."

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

    # 假設股票代碼為 4 到 6 位數的字母或數字
    if user_input.isalnum() and 4 <= len(user_input) <= 6:
        result = get_stock_health(user_input)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入有效的股票代碼（4 至 6 位數的字母或數字）。"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
