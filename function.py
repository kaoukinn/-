import twder
import twstock
import requests


# 取得匯率資訊(輸入的參數為貨幣代號)
def get_dollar(target_currency):
    rates = twder.now(target_currency)
    return f"即期匯率 : 1 TWD = {rates[3]} {target_currency}"

# a = input("請輸入要查詢的貨幣代號: ")
# result = get_dollar(a)
# print(result)

# 取得及時股價資訊(輸入的參數為股票代號)
def get_stock(stock_code):
    stock = twstock.realtime.get(stock_code)
    print(stock['success'])
    
    if stock is None:
        return f"無法獲取股票代號 {stock_code} 的即時股價資訊"
    
    price = stock['realtime']['latest_trade_price']
    print(price)
    return f"股票代號: {stock_code}，現在股價為: {price}"

# stock_code = input("請輸入要查詢的股票代號: ")
# result = get_stock(stock_code)
# print(result)

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
            message = f"{city_name}現在天氣{wx8}，最高溫度{maxt8}度，最低溫度{mint8}度，降雨機率{pop8}%"
            return message
        else:
            return "無法獲取天氣資訊。"

    except requests.exceptions.RequestException as e:
        return f"請求錯誤: {e}"
    
# city = input("請輸入要查詢的縣市名稱: ")
# result = get_weather(city)
# print(result)