import mysql.connector

# 建立 MySQL 資料庫連線
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="haohao0118",
    database="cafe"
)

def deposit(account, amount):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="haohao0118",
    database="cafe"
)
    cursor = db.cursor()

    # 檢查帳戶是否存在
    cursor.execute("SELECT * FROM cafe.money_table WHERE bank_name = %s", (account,))
    result = cursor.fetchone()
    if result is None:
        return "帳戶不存在"

    # 更新帳戶餘額
    cursor.execute("UPDATE cafe.money_table SET balance = balance + %s WHERE bank_name = %s", (amount, account))
    db.commit()
    db.close()
    return "存款已完成"

def withdraw(account, amount):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="haohao0118",
    database="cafe"
)
    cursor = db.cursor()

    # 檢查帳戶是否存在
    cursor.execute("SELECT * FROM cafe.money_table WHERE bank_name = %s", (account,))
    result = cursor.fetchone()
    if result is None:
        return "帳戶不存在"

    # 檢查餘額是否足夠
    balance = result[1]
    if balance < amount:
        return "餘額不足"

    # 更新帳戶餘額
    cursor.execute("UPDATE cafe.money_table SET balance = balance - %s WHERE bank_name = %s", (amount, account))
    db.commit()
    db.close()
    return "提款已完成"

def check_balance(account):
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="haohao0118",
    database="cafe"
)
    cursor = db.cursor()

    # 檢查帳戶是否存在
    cursor.execute("SELECT * FROM cafe.money_table WHERE bank_name = %s", (account,))
    result = cursor.fetchone()
    if result is None:
        return "帳戶不存在"

    balance = result[1]
    db.close()
    return f"目前餘額為 {balance} 元"
    

# 測試程式碼
# account = input("請輸入帳戶名稱：")
# action = input("請輸入要執行的操作（存款、提款、查詢餘額、新增帳戶）：")

# if action == "存款":
#     amount = float(input("請輸入存款金額："))
#     result = deposit(account, amount)
# elif action == "提款":
#     amount = float(input("請輸入提款金額："))
#     result = withdraw(account, amount)
# elif action == "查詢餘額":
#     result = check_balance(account)
# else:
#     result = "無效的操作"

# print(result)

# 關閉資料庫連線
db.close()
