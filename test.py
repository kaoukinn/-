import requests
from bs4 import BeautifulSoup

# 設置要查詢的股票代碼
stock_code = "2330.TW"

# 構建API請求URL
url = f"https://finance.yahoo.com/quote/{stock_code}?p={stock_code}"

# 發送API請求並獲取回應
response = requests.get(url)
content = response.content.decode("utf-8")

# 使用BeautifulSoup庫解析HTML內容
soup = BeautifulSoup(content, "html.parser")

# 提取所需的數據
current_price = soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.replace(",", "")
change = soup.find("span", {"class": "Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)"}).text.replace(",", "")
change_percent = soup.find("span", {"class": "Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)"}).find_all("span")[1].text
days_range = soup.find("td", {"data-test": "DAYS_RANGE-value"}).text.replace(",", "").replace(" - ", "/")
fifty_two_week_range = soup.find("td", {"data-test": "FIFTY_TWO_WK_RANGE-value"}).text.replace(",", "").replace(" - ", "/")
volume = soup.find("td", {"data-test": "TD_VOLUME-value"}).text.replace(",", "")

# 格式化並輸出結果
print(f"股票代碼: {stock_code}")
print(f"當前價格: {current_price}")
print(f"漲跌: {change}")
print(f"漲跌幅: {change_percent}")
print(f"最高價/最低價: {days_range}")
print(f"52周最高價/最低價: {fifty_two_week_range}")
print(f"成交量: {volume}")
