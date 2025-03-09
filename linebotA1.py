import yfinance as yf
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 初始化 Flask 應用
app = Flask(__name__)

# 使用硬編碼方式設置 LINE Bot 的 Access Token 和 Channel Secret
line_bot_api = LineBotApi('EriLCkSHz8vqv7gH6Y8PKMZTH9kd8zJLL1aQEy1jEoK/eNOo50Ly0gNAarUUfsod0skcPSeGrb7YIYWkLmrxAzUWBG6uQ2HJtb111yfIHk11KLmrx1KFylU​​UmU​​Umi11454FFFFyft 04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5b750f8f51ea241fe0a6579fdcf61ed5')

# 定義查詢股票健康狀況的函式
def get_stock_health(stock_code):
    try:
        stock = yf.Ticker(stock_code)  # 使用 yfinance 取得股票資訊
        # 確保股票資訊非空
        if stock.info and 'symbol' in stock.info:
            valuation = stock.info.get('forwardPE', 'N/A')  # 取得估值（前瞻市盈率）
            growth = stock.info.get('earningsGrowth', 'N/A')  # 取得成長率（收益成長）
            financials = stock.info.get('financialCurrency', 'N/A')  # 財務貨幣
            technicals = stock.info.get('fiftyDayAverage', 'N/A')  # 50 日均價
            risk = stock.info.get('beta', 'N/A')  # 風險評估（Beta 值）
            competition = 'N/A'  # Yahoo 財經未提供競爭分析
            news = 'N/A'  # 為簡化例子，未抓取新聞
            return (f"股票代號 {stock_code} 的健康狀況：\n"
                    f"估值（前瞻市盈率）：{valuation}\n"
                    f"成長（收益成長）：{growth}\n"
                    f"財務狀況（財務貨幣）：{financials}\n"
                    f"技術分析（50 日均價）：{technicals}\n"
                    f"風險評估（Beta）：{risk}\n"
                    f"競爭分析：{competition}\n"
                    f"近期新聞和事件：{news}")
        else:
            return "無法獲取股票健康資料，請檢查股票代號是否正確。"
    except Exception as e:
        return f"查詢股票時發生錯誤：{str(e)}"

# 定義 Line Bot 的 Webhook 回調處理
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')  # 從請求頭中取得簽名
    body = request.get_data(as_text=True)  # 取得請求內容
    try:
        handler.handle(body, signature)  # 使用 WebhookHandler 驗證和處理
    except InvalidSignatureError:  # 如果簽名無效，返回錯誤
        print("無效的簽名錯誤")
        abort(400)
    except Exception as e:
        print(f"處理回調時發生錯誤：{str(e)}")
        abort(500)
    return 'OK'

# 處理使用者發送的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()  # 取得使用者輸入的訊息

    # 處理股票代號邏輯
    if "." not in user_input:  # 如果用戶未指定市場後綴
        user_input += ".TW"  # 默認添加台灣市場代碼

    result = get_stock_health(user_input)  # 查詢股票健康資料
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))  # 回應股票資訊

# 啟動應用程式
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # 設置執行的主機及埠號
