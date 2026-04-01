from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import FollowEvent

import threading
import datetime
import time
import os
import requests
import json

LINEBOT_PUSH_API_URL = 'https://api.line.me/v2/bot/message/push'

#大冠鷲的機器人
#ACCESS_TOKEN = 'KjWVkMZ3K5vnTE4XHTf/VJWhyOTk03T2e5OoCeatsoCa9LQK7Y76rDlyoEl+9/wHD+x3p44HxsIG3KYNbWEDXWMiDa90Ip2oJgBqk8vMXJotJp6Gi0cVTOnzfiFLZd4CRJtdertC3nkV2Av0P2FrJgdB04t89/1O/w1cDnyilFU='
#WEBHOOK_SECRET = '5e3d684df6cfc85dfe9e03ae14bf235a' #大冠鷲的機器人
#GUO_USER_ID = 'U98a0698b53411305cfac5ad1a111a775' #我的(大冠鷲的機器人user id)

#台灣特有種鳥_黃腹琉璃
ACCESS_TOKEN = '+KntHahgcVf9CPZeazx0NKXQFRsu3cWk2Ia8pveQcRz0e8Bp89BPBf/oI6i1fdc9YeHN8sW1zktHp42HPZOCeRJB0iZbJShkzJH/x353KwzlyT+db1hKg9yyZq3Fg926mHCBMWkDuHJqOn5Kb414lwdB04t89/1O/w1cDnyilFU='
WEBHOOK_SECRET = '28dedebbd130f0a616c532466aaaa7e1' #台灣特有種鳥_黃腹琉璃
GUO_USER_ID = 'Udefd9b07997ca535ee61d89ac2489cb9' #我的(台灣特有種鳥_黃腹琉璃user id)

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(WEBHOOK_SECRET)

class RunSearch:
    def __init__(self):
        print("init RunSearch object",flush=True)
        #self.app = Flask(__name__)
        self.data = None
        # same lock can only be acquire once before release
        self.mutex = threading.Lock()
        #self.app.config['JSON_AS_ASCII'] = False  # jsonify allow none-ascii
        #self.app.add_url_rule('/api/search', 'search', self.http_server)
    
    """
    def http_server(self):
        try:
            query_key = request.args.get("key", type=str)
            ret, result = self.get_data(query_key)
            result = {"code": ret, "result": result}
        except Exception as e:
            print(e)
            result = {"code": -1, "result": []}
        return jsonify(result)


    def get_data(self, query_key):
        # prohibit data update while get
        try:
            self.mutex.acquire()
            if not isinstance(self.data, dict):
                return -1, []
            elif query_key not in self.data:
                return -2, []
            return 0, self.data[query_key]
        except Exception as e:
            print(e)
            return -1, []
        finally:
            self.mutex.release()
"""

    def update_data(self, new_data):
        try:
            self.mutex.acquire()
            self.data = new_data
            print("data update successful",flush=True)
        except Exception as e:
            print(e)
        finally:
            self.mutex.release()


class runningThread(threading.Thread):
    # hold instance of http server
    def __init__(self, http_server):
        super().__init__()  # threading.Thread.__init__(self)
        self.thSleepTime = 3
        self.timeformatStr = "%M%S"
        print("init runningThread object",flush=True)
        self.http_server = http_server
        self.last_update_logdate = None
        # self.daemon = True

    def run(self):
        while True:
            logdate = datetime.datetime.now() + datetime.timedelta(seconds=-7)
            print("logdate: ",logdate,flush=True)
            print("last_update_logdate", self.last_update_logdate,flush=True)
            #if logdate.strftime("%Y%m%d") == self.last_update_logdate:
            if logdate.strftime(self.timeformatStr) == self.last_update_logdate:
                print("already have latest data",flush=True)
                time.sleep(self.thSleepTime)
                continue
            print("Update latest data",flush=True)
            new_data = self.generate_new_data(logdate)
            self.http_server.update_data(new_data)
            #self.last_update_logdate = logdate.strftime("%Y%m%d")
            self.last_update_logdate = logdate.strftime(self.timeformatStr)
            time.sleep(self.thSleepTime)

    def generate_new_data(self, logdate):
        print("Generate new data",flush=True)
        return {"example": logdate}


@app.route("/getcwd")
def getcwd():
    print("current path: ", os.getcwd(), flush=True)
    return "current path: " + os.getcwd()

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
   # body = request.get_json() # body will be a python "dict", but not a json
   # body = request.json # is the same as request.get_json()

    print("this is callback", flush=True)
    http_server = RunSearch()
    th = runningThread(http_server)
    th.start() #->call run()
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

'''
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.source.user_id))
'''

# when a user join/unblock the linebot
@handler.add(FollowEvent)
def handle_follow(event):
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    payload = {
        'to': GUO_USER_ID,
        'messages': [
            {'type': 'text',
             'text': event.source.user_id
            }
         ]
    }
    
    # get the use id of somebody who joins the linebot and send it to my line account
    try:
        response = requests.post(LINEBOT_PUSH_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print('Push Message 傳送成功！')
    except requests.exceptions.RequestException as e:
        print('Push Message 傳送失敗：', e)

#When a user adds your bot, LINE sends:
'''
{
  "type": "follow",
  "source": {
    "type": "user",
    "userId": "Uxxxxxxxxxxxx"
  }
}
'''


################### use for postman TEST only #####################
# can use postman to send post(got to set body data for username and password) to: http://127.0.0.1:5000/submit
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == "POST":
        username = request.values['username']
        password = request.values['password']
        if username=='david' and password=='1234':
            return '歡迎光臨本網站！'
        else:
            return '帳號或密碼錯誤！'

#get the userID
@app.route("/linebot", methods=['POST'])
def linebot():
    try:
        data = request.get_json() # data will be a python dict, but not json
        #json.dumps(data) # will get a json string
        if not data:
            return {"error": "Invalid JSON"}, 400
        for event in body['events']:
            if event['type'] == 'follow':
                user_id = event['source']['userId']
                print("User joined:", user_id)
        print("data is: ", data)
        return {"message": "Data received", "data": data}
    except Exception as e:
        return {"error": str(e)}, 500

 #https://vocus.cc/article/67be7413fd897800011fef50




####################End Test #####################



if __name__ == '__main__':
    #render.com's free instance will shutdown automatically when it is inactive about 15~17 minutes.
    #http_server = RunSearch()
    #th = runningThread(http_server)
    #th.start() #->call run()
    
    # host = 0.0.0.0 表示無論本地位址或真實位址都能連上Falsh server。當網店開區完成時，要將host設為 0.0.0.0讓所有人都能瀏覽網站
    #defaut value: # app.run(host='127.0.0.1', port = 5000, debug=false)
    app.run()
    #app.run(debug = True)
