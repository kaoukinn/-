import twder
import twstock
import requests

def get_dollar_name():
    message = {
            'type': 'flex',
            'altText': 'this is a flex message',
            'contents': {
                'type': 'carousel',
                'contents': [{
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "匯率查詢",
                        "weight": "bold",
                        "size": "xl",
                        "align": "center"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": []
                    }
                    ]
                    },
                    "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "美金匯率",
                        "text": "USD"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "日幣匯率",
                        "text": "JPY"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "港幣匯率",
                        "text": "HKD"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "澳幣匯率",
                        "text": "AUD"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "message",
                        "label": "人民幣匯率",
                        "text": "CNY"
                        }
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm"
                    }
                    ],
                    "flex": 0
                }
                }
                ]
            }
        }
    return message
# 取得匯率資訊(輸入的參數為貨幣代號)
def get_dollar(target_currency):
    rates = twder.now(target_currency)
    message = {
        "type": "text",
        "text": f"即期匯率 : 1 TWD = {rates[3]} {target_currency}"
    }
    return message

# 取得及時股價資訊(輸入的參數為股票代號)
def get_stock(stock_code):
    stock = twstock.realtime.get(stock_code)
    print(stock['success'])
    
    if stock is None:
        return f"無法獲取股票代號 {stock_code} 的即時股價資訊"
    
    price = stock['realtime']['latest_trade_price']
    print(price)
    message = {
        "type": "text",
        "text": f"股票代號: {stock_code}，現在股價為: {price}"
    }
    return message

# 取得及時天氣資訊(輸入參數為城市名稱)
def get_weather(city_name):
    url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
            "Authorization": "CWB-496A8CF2-1587-49DD-AD0E-FB54EC524B0C",
            "locationName": f"{city_name}",
        }
    try:
        data = requests.get(url, params=params)
        data_json = data.json()
        location = data_json["records"]["location"]

        # 檢查API回應是否成功
        if data.status_code == 200:
            # 解析API回應並取得天氣資訊
            wx8 = location[0]['weatherElement'][0]['time'][0]['parameter']['parameterName']
            maxt8 = location[0]['weatherElement'][4]['time'][0]['parameter']['parameterName']
            mint8 = location[0]['weatherElement'][2]['time'][0]['parameter']['parameterName']
            pop8 = location[0]['weatherElement'][1]['time'][0]['parameter']['parameterName']

            # 組合回傳訊息
            message = {
                "type": "text",
                "text": f"{city_name}現在天氣{wx8}，最高溫度{maxt8}度，最低溫度{mint8}度，降雨機率{pop8}%"
            }
            return message
        else:
            return "無法獲取天氣資訊。"

    except requests.exceptions.RequestException as e:
        return f"請求錯誤: {e}"
    
# city = input("請輸入要查詢的縣市名稱: ")
# result = get_weather(city)
# print(result)
# 尋找停車場功能
def get_parking_lots(latitude, longitude):
    # 使用 Google Maps API 搜尋目標座標半徑500公尺內的停車場
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{latitude},{longitude}',
        'radius': 1000,
        'keyword': '停車場',
        'type': 'parking',
        'language': 'zh-TW',
        'key': 'AIzaSyAm2daNnuoTdVsIKke-4MhvQ6qFTTg7IKE'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if len(data['results']) == 0:
        # 如果找不到停車場，回覆「附近沒有停車場」的訊息
        message = {'type': 'text', 'text': '附近沒有停車場'}
    else:
        columns = []
        for item in data['results'][:5]:
            column = {
                'title': item['name'],
                'text': item['vicinity'],
                'actions': [
                    {'type': 'uri', 'label': '在地圖上檢視', 'uri': f"https://www.google.com.tw/maps/place/?q=place_id:{item['place_id']}"},
                ]
            }
            columns.append(column)
        carousel_template = {'type': 'carousel', 'columns': columns}
        message = {
            'type': 'template',
            'altText': '以下是附近的停車場：',
            'template': carousel_template
        }

    return message

# 我的功能
def store_information():
    message = {
    "type": "template",
    "altText": "This is a buttons template",
    "template": {
        "type": "buttons",
        "title": "個人功能",
        "text": "請點選需要的功能",
        "actions": [
        {
            "type": "uri",
            "label": '附近停車場',
            "uri": 'line://nv/location'
        },
        {
            "type": "message",
            "label": '匯率查詢',
            "text": '匯率查詢'
        },
        {
            "type": "message",
            "label": '股價查詢',
            "text": '股價查詢'
        },
        {
            "type": "message",
            "label": '天氣查詢',
            "text": '天氣查詢'
        },
        ]
    }
}
    return message