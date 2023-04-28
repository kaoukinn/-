import time
import requests
import twder
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage,
    ButtonsTemplate, MessageAction
)

app = Flask(__name__)

# 填入自己的Channel Access Token
line_bot_api = LineBotApi('YGP5KkxC5I0KGB5dyMvkF+kBJKJetli3hiMWmQBej/ZzTkL68n+EWck4ittijZZ/qwMpTDbpFwbIVYjXRB6UVADgWDVISEDZjTtyj6AcXbhXb9vetlOw5KNkAg4Og8Kbxw7yiyOQL6h1eGB7tsE19AdB04t89/1O/w1cDnyilFU=')
# 填入自己的Channel Secret
handler = WebhookHandler('8b47bca8709250bb165d9039d4d33d7c')

stock_api_url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
stock_code_mapping = {
    "2330": "台積電",
    "2884": "玉山金",
    "2890": "永豐金",
    "1101": "台泥" ,
    "00878": "國泰永續高股息",
    "00713": "元大高息低波高股息"
    # 可以添加更多的股票代码和名称映射
}
# 獲取股票代號
def stock_price_search(event):
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='請輸入您要查詢的股票代號')
        )
    except LineBotApiError as e:
        print(e)

# 取得匯率資訊
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

# 取得天氣資訊
def get_weather_info(text):
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
            "Authorization": "CWB-496A8CF2-1587-49DD-AD0E-FB54EC524B0C",
            "locationName": f"{text}",
        }
    data = requests.get(url, params=params)
    data_json = data.json()
    location = data_json["records"]["location"]

    city = location[0]['locationName']
    wx8 = location[0]['weatherElement'][0]['time'][0]['parameter']['parameterName']
    maxt8 = location[0]['weatherElement'][4]['time'][0]['parameter']['parameterName']
    mint8 = location[0]['weatherElement'][2]['time'][0]['parameter']['parameterName']
    ci8 = location[0]['weatherElement'][3]['time'][0]['parameter']['parameterName']
    pop8 = location[0]['weatherElement'][1]['time'][0]['parameter']['parameterName']
    
    # 使用 TextSendMessage() 函式來建立訊息物件
    message = TextSendMessage(text=f'{city}未來天氣{wx8}，最高溫度 {maxt8} 度，最低溫度 {mint8} 度，降雨機率 {pop8} %')
    
    # 回傳訊息物件
    return message
    

citylist = ['宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹縣', '新竹市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '屏東縣']

@app.route("/", methods=['POST'])
def callback():
    # 获取请求头中的 X-Line-Signature
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == "股價查詢":
        stock_price_search(event)

    elif text == "查詢匯率":
        # 取得Button Template
        button_template = get_currency_template()
        # 建立Template Message
        message = TemplateSendMessage(alt_text='查詢匯率', template=button_template)
        # 使用Line Messaging API的reply_message功能，向使用者回覆Button Template
        line_bot_api.reply_message(event.reply_token, message)
    elif text == "查詢天氣":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您要查詢的縣市名稱")
        )
    elif text in citylist:
        message = get_weather_info(text)
        line_bot_api.reply_message(event.reply_token, message)
    elif text in stock_code_mapping:
        # 股票查詢
        stock_code = text
        stock_name = stock_code_mapping[stock_code]
        stock_params = {"ex_ch": "tse_" + stock_code + ".tw"}
        stock_res = requests.get(stock_api_url, params=stock_params)
        stock_data = stock_res.json()
        try:
            price = stock_data["msgArray"][0]["z"]
            message = f"{stock_name}現在的股價為 {float(price)} 元"
        except:
            message = f"找不到 {stock_name} 的股價資料"
        # 使用Line Messaging API的reply_message功能，向使用者回覆股價
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif text.isalpha():
        # 匯率查詢
        user_input = text[0:]
        currency = user_input.upper()
        try:
            rate = twder.now(currency)[3]
            message = f"現在 {currency} 匯率為 {rate}"
        except:
            message = f"找不到 {currency} 的匯率資料"
        # 使用Line Messaging API的reply_message功能，向使用者回覆匯率
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="抱歉，目前不支持您輸入的查詢。")
        )


if __name__ == "__main__":
    app.debug = True
    app.run()