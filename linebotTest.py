from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import threading
import datetime
import time

line_bot_api = LineBotApi('KjWVkMZ3K5vnTE4XHTf/VJWhyOTk03T2e5OoCeatsoCa9LQK7Y76rDlyoEl+9/wHD+x3p44HxsIG3KYNbWEDXWMiDa90Ip2oJgBqk8vMXJotJp6Gi0cVTOnzfiFLZd4CRJtdertC3nkV2Av0P2FrJgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5e3d684df6cfc85dfe9e03ae14bf235a')

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




@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("this is callback", flush=True)
    http_server = RunSearch()
    th = runningThread(http_server)
    th.start() #->call run()
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

if __name__ == '__main__':
    #http_server = RunSearch()
    #th = runningThread(http_server)
    #th.start() #->call run()
    app.run()
