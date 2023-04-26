import os
import twder
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, MessageAction, TemplateSendMessage
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
import configparser
from linebot.exceptions import InvalidSignatureError

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

# 處理接收到的訊息
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
    else:
        # 若使用者輸入的是匯率代碼，則回傳該國匯率
        currency = user_input.upper()
        try:
            rate = twder.now(currency)[3]
            message = f"現在 {currency} 匯率為 {rate}"
        except:
            message = f"找不到 {currency} 的匯率資料"
        # 使用Line Messaging API的reply_message功能，向使用者回覆匯率
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

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


