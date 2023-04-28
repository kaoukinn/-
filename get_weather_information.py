import openai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent
from linebot.exceptions import LineBotApiError
from flask import Flask, request, abort
import configparser
from linebot.exceptions import InvalidSignatureError
import requests
import time

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

# 股票实时价格查询 API 的 URL
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

def stock_price_search(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入您要查詢的股票代號')
        )
    except LineBotApiError as e:
        print(e)

@app.route("/", methods=['POST'])
def callback():
    # 获取请求头中的 X-Line-Signature
    signature = request.headers['X-Line-Signature']

    # 获取请求体的内容
    body = request.get_data(as_text=True)

    # 处理 Line Bot 的事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 获取用户输入的股票代码
    text = event.message.text
    if text == "股價查詢":
        stock_price_search(event)
    # 检查股票代码是否在映射表中
    elif text not in stock_code_mapping:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，目前不支持您輸入的股票查詢。")
        )
        return

    # 组装查询参数
    query_params = {
        "ex_ch": "tse_{}.tw".format(text),
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
    stock_name = stock_code_mapping[text]
    stock_price = float(result['msgArray'][0]['z'])

    # 格式化响应消息
    response_text = "{} ({}) 的即時股價是 {}元。".format(stock_name, text, stock_price)

    # 发送响应消息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )



if __name__ == "__main__":
    app.debug = True
    app.run()
