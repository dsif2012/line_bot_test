import os
import sqlite3
import requests
import xml.etree.ElementTree as ET

# SQLite 數據庫文件路徑
DB_FILE_PATH = 'invoice_data.db'

# 初始化 SQLite 數據庫
def init_db():
    if not os.path.exists(DB_FILE_PATH):
        conn = sqlite3.connect(DB_FILE_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        special_prize TEXT UNIQUE,
                        grand_prize TEXT,
                        big_prize1 TEXT,
                        big_prize2 TEXT,
                        big_prize3 TEXT)''')
        conn.commit()
        conn.close()

# 更新數據庫
def update_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    count = c.fetchone()[0]
    if count == 0:
        url = 'https://invoice.etax.nat.gov.tw/invoice.xml'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                tree = ET.fromstring(response.text)
                item = tree.find('.//item')
                description = item.find('description').text
                special_prize = description.split('<p>特別獎：')[1].split('</p>')[0]
                grand_prize = description.split('<p>特獎：')[1].split('</p>')[0]
                first_prizes_str = [x.split('</p>')[0] for x in description.split('<p>頭獎：')[1:]]
                first_prizes = []
                for prize_str in first_prizes_str:
                    first_prizes.extend(prize_str.split('、'))
                c.execute("INSERT INTO invoices (special_prize, grand_prize, big_prize1, big_prize2, big_prize3) VALUES (?, ?, ?, ?, ?)", (special_prize, grand_prize, first_prizes[0], first_prizes[1], first_prizes[2]))
                conn.commit()
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
    conn.close()

# 解析中獎號碼的函數
def check_invoice(invoice_number):
    conn = sqlite3.connect(DB_FILE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM invoices")
    data = c.fetchone()
    answer = ""
    if data is not None:
        _, special_prize, grand_prize, big_prize1, big_prize2, big_prize3 = data
        if invoice_number == special_prize:
            answer = "特別獎"
        elif invoice_number == grand_prize:
            answer = "特獎"
        elif invoice_number in {big_prize1, big_prize2, big_prize3}:
            answer = "頭獎"
        elif invoice_number[-7:] in {big_prize1[-7:], big_prize2[-7:], big_prize3[-7:]}:
            answer = "二獎"
        elif invoice_number[-6:] in {big_prize1[-6:], big_prize2[-6:], big_prize3[-6:]}:
            answer = "三獎"
        elif invoice_number[-5:] in {big_prize1[-5:], big_prize2[-5:], big_prize3[-5:]}:
            answer = "四獎"
        elif invoice_number[-4:] in {big_prize1[-4:], big_prize2[-4:], big_prize3[-4:]}:
            answer = "五獎"
        elif invoice_number[-3:] in {big_prize1[-3:], big_prize2[-3:], big_prize3[-3:]}:
            answer = "六獎"
        else:
            answer = "可惜，您沒有中獎"
    else:
        answer = "資料庫中無資料，請稍後再試"
    conn.close()
    return answer

# 初始化並更新數據庫
init_db()
update_db()
