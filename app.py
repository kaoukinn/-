import openai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, MessageAction, TemplateSendMessage
from linebot.exceptions import LineBotApiError
from flask import Flask, request, abort
import configparser
from linebot.exceptions import InvalidSignatureError
import requests
import time
import twder


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

config = configparser.ConfigParser() #讀取config檔案
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
HEADER = {  #http的HEADER
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}

# 股票查詢的網址
stock_api_url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"

# 股票代码与名称的映射表
stock_code_mapping = {
    "2330": "台積電",
    "2884": "玉山金",
    "2890": "永豐金",
    "1101": "台泥" ,
    "00878": "國泰永續高股息",
    "00713": "元大高息低波高股息"
    # 可以添加更多的股票代码和名称映射
}



# 查詢匯率的Button Template
def get_currency_template():
    return ButtonsTemplate(
        title='查詢匯率',
        text='請選擇您要查詢的貨幣',
        actions=[
            MessageAction(
                label='查詢美金匯率',
                text='USD'
            ),
            MessageAction(
                label='查詢日幣匯率',
                text='JPY'
            ),
            MessageAction(
                label='查詢英鎊匯率',
                text='GBP'
            ),
            MessageAction(
                label='查詢澳幣匯率',
                text='AUD'
            )
        ]
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    if user_input == "查詢匯率":
        # 取得Button Template
        button_template = get_currency_template()
        # 建立Template Message
        message = TemplateSendMessage(alt_text='查詢匯率', template=button_template)
        # 使用Line Messaging API的reply_message功能，向使用者回覆Button Template
        line_bot_api.reply_message(event.reply_token, message)
    elif user_input.isalpha():
        rate = twder.now(user_input)[3]
        message = f"現在 {user_input} 匯率為 {rate}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
    elif user_input == "股價查詢":
        # 回覆「請輸入股票代號」的訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入股票代號")
        )
    else:
        # 检查股票代码是否在映射表中
        if user_input not in stock_code_mapping:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="抱歉，目前不支持您輸入的股票查詢。")
            )
            return

        # 组装查询参数
        query_params = {
            "ex_ch": "tse_{}.tw".format(user_input),
            "json": "1",
            "_": int(time.time() * 1000),
        }

        # 发送 HTTP 请求
        response = requests.get(stock_api_url, params=query_params)

        # 解析响应内容
        result = response.json()
        if result['rtmessage'] != "OK":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="查詢失敗，請稍後在試。")
            )
            return

        # 获取股票名称和实时价格
        stock_name = stock_code_mapping[user_input]
        stock_price = float(result['msgArray'][0]['z'])

        # 格式化响应消息
        response_text = "{} ({}) 的即時股價是 {}元。".format(stock_name, user_input, stock_price)

        # 发送响应消息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )

# Line Bot 訊息處理
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'






if __name__ == "__main__":
    app.debug = True
    app.run()