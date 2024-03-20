from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('qejvWAVTU83QlMnSBKY786eFQMUfXycNQ9stoykXmtl96bXB9dUc0r5sAxWN01C2oY2b84nuE51NcnBJA++lnOT6SNt7wdhIVfKfLu+mFckrwY6qqiO8Ykdrs8i527Ju/VkXSNurBv8f3LPJqNdEfAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c77ee99d1b99455f6f94ba1dcc7283a4')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
