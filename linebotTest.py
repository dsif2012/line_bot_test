import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import sqlite3
from invoice_checker import check_invoice

app = Flask(__name__)

line_bot_api = LineBotApi('elXhK9mReraLH+vbGiKZEu6rK299ZSts/29WWgv8RzlHeK+6jkP1nv1rIsPkendKoY2b84nuE51NcnBJA++lnOT6SNt7wdhIVfKfLu+mFclSi3zaAKc0mpCVdRGdlBq/M3FJX0qAPA/jH3FELHKTqwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c77ee99d1b99455f6f94ba1dcc7283a4')

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    if 'invoice_number' not in data:
        return jsonify({'error': '請提供 invoice_number'}), 400

    invoice_number = data['invoice_number']
    result = check_invoice(invoice_number)
    return jsonify({'result': result})



# Line Bot 的 Webhook 處理
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理使用者發送的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    
    # 檢查是否為 8 位數的數字
    if user_input.isdigit() and len(user_input) == 8:
        result = check_invoice(user_input)
        # 回覆訊息
        if result in prize_messages:
            reply_message = prize_messages[result]
        else:
            reply_message = result
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"您輸入的發票號碼為：{user_input}\n {reply_message}"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入 8 位數的發票號碼。"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
