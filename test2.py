from __future__ import unicode_literals
import string
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, MessageAction
import requests
import json
import configparser
import os
from urllib import parse
app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


config = configparser.ConfigParser() #讀取config檔案
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {  #http的HEADER
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return 'ok'
    body = request.json
    events = body["events"]
    if request.method == 'POST' and len(events) == 0:
        return 'ok'
    print(body)
    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload["replyToken"] = replyToken
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "查詢匯率":
                    payload["messages"] = [get_currency_template()]
                elif text == "查詢天氣":
                    payload["messages"] = [getcityname()]
                elif text == "早安":
                    payload["messages"] = [getmorningStickerMessage()]
                elif text == "台北101":
                    payload["messages"] = [getTaipei101ImageMessage(),
                                           getTaipei101LocationMessage(),
                                           getMRTVideoMessage()]
                elif text == "天母棒球場":
                    payload["messages"] = [getTaipeiBaseball()]
                elif text == "quoda":
                    payload["messages"] = [
                            {
                                "type": "text",
                                "text": getTotalSentMessageCount()
                            }
                        ]
                elif text == "今日確診人數":
                    payload["messages"] = [
                            {
                                "type": "text",
                                "text": getTodayCovid19Message()
                            }
                        ]
                elif text == "主選單":
                    payload["messages"] = [
                            {
                                "type": "template",
                                "altText": "This is a buttons template",
                                "template": {
                                  "type": "buttons",
                                  "title": "Menu",
                                  "text": "Please select",
                                  "actions": [
                                      {
                                        "type": "message",
                                        "label": "我的名字",
                                        "text": "我的名字"
                                      },
                                      {
                                        "type": "message",
                                        "label": "今日確診人數",
                                        "text": "今日確診人數"
                                      },
                                      {
                                        "type": "uri",
                                        "label": "聯絡我",
                                        "uri": f"tel:{my_phone}"
                                      }
                                  ]
                              }
                            }
                        ]
                elif text == "天氣":
                    pass   
                else:
                    payload["messages"] = [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                replyMessage(payload)
            elif events[0]["message"]["type"] == "location":
                title = events[0]["message"]["title"]
                latitude = events[0]["message"]["latitude"]
                longitude = events[0]["message"]["longitude"]
                payload["messages"] = [getLocationConfirmMessage(title, latitude, longitude)]
                replyMessage(payload)
        elif events[0]["type"] == "postback":
            if "params" in events[0]["postback"]:
                reservedTime = events[0]["postback"]["params"]["datetime"].replace("T", " ")
                payload["messages"] = [
                        {
                            "type": "text",
                            "text": F"已完成預約於{reservedTime}的叫車服務"
                        }
                    ]
                replyMessage(payload)
            else:
                data = json.loads(events[0]["postback"]["data"])
                action = data["action"]
                if action == "get_near":
                    data["action"] = "get_detail"
                    payload["messages"] = [getCarouselMessage(data)]
                elif action == "get_detail":
                    del data["action"]
                    payload["messages"] = [getTaipei101ImageMessage(),
                                           getTaipei101LocationMessage(),
                                           getMRTVideoMessage(),
                                           getCallCarMessage(data)]
                replyMessage(payload)

    return 'OK'

# 查詢匯率
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
# 
def getcityname():
    message ={
        "type": "text",
        "text": "請輸入您要查詢的縣市名稱",
    }
    
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
            "Authorization": "CWB-496A8CF2-1587-49DD-AD0E-FB54EC524B0C",
            "locationName": f"{message}",
        }
    data = requests.get(url, params=params)   # 取得 JSON 檔案的內容為文字
    data_json = data.json()    # 轉換成 JSON 格式
    location = data_json["records"]["location"]

    city = location[0]['locationName']   # 縣市名稱
    wx8 = location[0]['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
    maxt8 = location[0]['weatherElement'][4]['time'][0]['parameter']['parameterName']  # 最高溫
    mint8 = location[0]['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
    ci8 = location[0]['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
    pop8 = location[0]['weatherElement'][1]['time'][0]['parameter']['parameterName']   # 降雨機率
        
    return f'{city}未來天氣{wx8}，最高溫度 {maxt8} 度，最低溫度 {mint8} 度，降雨機率 {pop8} %'

# 取得天氣資訊
def get_weather_info(name):
    url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
            "Authorization": "CWB-496A8CF2-1587-49DD-AD0E-FB54EC524B0C",
            "locationName": f"{name}",
        }
    data = requests.get(url, params=params)   # 取得 JSON 檔案的內容為文字
    data_json = data.json()    # 轉換成 JSON 格式
    location = data_json["records"]["location"]

    city = location[0]['locationName']   # 縣市名稱
    wx8 = location[0]['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
    maxt8 = location[0]['weatherElement'][4]['time'][0]['parameter']['parameterName']  # 最高溫
    mint8 = location[0]['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
    ci8 = location[0]['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
    pop8 = location[0]['weatherElement'][1]['time'][0]['parameter']['parameterName']   # 降雨機率
    
    return f'{city}未來天氣{wx8}，最高溫度 {maxt8} 度，最低溫度 {mint8} 度，降雨機率 {pop8} %'