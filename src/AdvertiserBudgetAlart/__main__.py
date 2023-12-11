# __main__.py

from CampaignDataSync import check_for_changes
from SendFeishuMessage import LarkNotifier
from .Settings.config import keys


def sync_and_alert_changes(_advertiser_name):
    import os
    from dotenv import load_dotenv
    load_dotenv()

    _advertiser_name: str
    app_id = os.getenv('APP_ID')
    app_secret = os.getenv('APP_SECRET')
    config = keys[_advertiser_name]
    chat_id = config['chat_id']
    advertiser_id = config['advertiser_id']

    _changes_text = {}
    _changes_text = check_for_changes(_advertiser_name)

    if _changes_text:
        lark_notifier = LarkNotifier(app_id, app_secret)
        message_text = f"{_advertiser_name}({advertiser_id}): \n{_changes_text}"
        lark_notifier.send(message_text, chat_id)
    else:
        return


def advertiser_budget_alart():
    for advertiser_name in keys:
        sync_and_alert_changes(advertiser_name)


if __name__ == "__main__":
    advertiser_budget_alart()
