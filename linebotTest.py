from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line_bot_api = LineBotApi('KjWVkMZ3K5vnTE4XHTf/VJWhyOTk03T2e5OoCeatsoCa9LQK7Y76rDlyoEl+9/wHD+x3p44HxsIG3KYNbWEDXWMiDa90Ip2oJgBqk8vMXJotJp6Gi0cVTOnzfiFLZd4CRJtdertC3nkV2Av0P2FrJgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5e3d684df6cfc85dfe9e03ae14bf235a')

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
    app.run()
