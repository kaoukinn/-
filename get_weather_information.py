import openai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent
from linebot.exceptions import LineBotApiError
from flask import Flask, request, abort
import configparser
from linebot.exceptions import InvalidSignatureError
import twstock

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

# 處理收到的文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        # 取得使用者輸入的股票代號
        stock_code = event.message.text + '.TW'
        # 取得該股票的即時資訊
        stock_info = twstock.realtime.get(stock_code)
        # 如果取得成功，回傳即時價格
        if stock_info['success']:
            reply_text = f"{stock_info['info']['name']} 目前的價格為 {stock_info['realtime']['latest_trade_price']} 元"
        # 如果取得失敗，回傳錯誤訊息
        else:
            reply_text = "查詢失敗，請檢查股票代號是否正確"
    except:
        reply_text = "發生錯誤，請稍後再試"
    # 回覆訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    app.debug = True
    app.run()
