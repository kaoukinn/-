import openai
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent
from linebot.exceptions import LineBotApiError
from flask import Flask, request, abort
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

# 設置 OpenAI API Key
openai.api_key = os.environ.get('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')

# 定義翻譯功能
def translate_text(text, dest):
    prompt = f"翻譯 '{text}' 成為 '{dest}'"
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message.strip()

# 處理 Linebot 收到的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    # 如果使用者輸入「翻譯」，則進入翻譯模式
    if text == '翻譯':
        reply_text = '請輸入要翻譯的內容：'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    # 如果使用者在翻譯模式中，則進行翻譯
    elif hasattr(event, 'translation_mode'):
        # 如果是中文，則翻譯成英文
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            prompt = f"翻譯 '{text}' 成為 'en'"
        # 如果是英文，則翻譯成中文
        else:
            prompt = f"翻譯 '{text}' 成為 'zh'"
        completions = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        translated_text = completions.choices[0].text.strip()
        reply_text = f"翻譯結果：{translated_text}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    # 如果不是翻譯模式，也不是翻譯指令，則回覆預設訊息
    else:
        reply_text = '您好，歡迎使用翻譯機器人。請輸入「翻譯」進入翻譯模式。'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# 處理 Linebot 收到的 Postback Event
@handler.add(PostbackEvent)
def handle_postback(event):
    # 如果 Postback Data 是翻譯指令，則進入翻譯模式
    if event.postback.data == 'translation_mode':
        event.translation_mode = True
        reply_text = '請輸入要翻譯的內容：'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.debug = True
    app.run()
