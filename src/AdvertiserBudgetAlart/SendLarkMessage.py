# SendLarkMessage.py
import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from Settings.config import keys


class LarkNotifier:
    def __init__(self, _app_id, _app_secret):
        self.app_id = _app_id
        self.app_secret = _app_secret
        self.tenant_access_token = ""
        self.last_update_time = datetime.now()
        self.expire_time = 0

    def get_tenant_access_token(self):
        if self.tenant_access_token == "" or (datetime.now() - self.last_update_time).seconds > self.expire_time - 600:
            response = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/",
                                     json={
                                         "app_id": self.app_id,
                                         "app_secret": self.app_secret
                                     })
            self.tenant_access_token = response.json()["tenant_access_token"]
            self.expire_time = response.json()["expire"]
            self.last_update_time = datetime.now()
        return self.tenant_access_token

    def send(self, _changes_text, _chat_id):
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        params = {"receive_id_type": "chat_id"}
        msgContent = {"text": _changes_text}
        req = {
            "receive_id": _chat_id,
            "msg_type": "text",
            "content": json.dumps(msgContent)
        }
        payload = json.dumps(req)
        headers = {
            'Authorization': f'Bearer {self.get_tenant_access_token()}',
            'Content-Type': 'application/json'
        }
        requests.request("POST", url, params=params, headers=headers, data=payload)


# unit test
if __name__ == "__main__":
    load_dotenv()
    advertiser_name = ''
    app_id = os.getenv('APP_ID')
    app_secret = os.getenv('APP_SECRET')
    config = keys[advertiser_name]
    chat_id = config['chat_id']
    message_text = ''
    lark_notifier = LarkNotifier(app_id, app_secret)
    lark_notifier.send(message_text, chat_id)
