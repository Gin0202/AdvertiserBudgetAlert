# CampaignDataSync.py:
import os
import sqlite3

from DatabaseManager import DatabaseManager, get_json_data


def notify_campaign_changed(changes_text, adv_campaign_id, campaign_name, daily_cap, click_cap, payout):
    changes_text += f"ID: {adv_campaign_id}({campaign_name}), PO: {payout}, Cap: {daily_cap}, Click: {click_cap}\n"
    return changes_text


def notify_new_campaign(changes_text, adv_campaign_id, campaign_name, daily_cap, click_cap, payout):
    changes_text += f"New Active ID: {adv_campaign_id}({campaign_name}), PO: {payout}, Cap: {daily_cap}, Click: {click_cap}\n"
    return changes_text


def calculate_change(old, new, is_float=False):
    try:
        old_val = float(old) if is_float else int(old)
        new_val = float(new) if is_float else int(new)
        change = round(new_val - old_val, 3) if is_float else int(new_val - old_val)
        return f"+{change}" if change > 0 else str(change)
    except ValueError:
        return "0"


def check_for_changes(_advertiser_name):
    dbm = DatabaseManager(_advertiser_name)
    data = get_json_data(_advertiser_name)
    if not data:
        return

    if not os.path.exists(dbm.db_path):
        dbm.create_table()
        dbm.insert_or_update_data(data)
        return

    conn = sqlite3.connect(dbm.db_path)
    cursor = conn.cursor()
    new_data_dict = {}

    for campaign in data:
        campaign_id = str(campaign.get(dbm.adv_campaign_id_column, ''))
        if campaign_id:
            new_data_dict[campaign_id] = {
                dbm.adv_campaign_id_column: campaign_id,
                dbm.campaign_name_column: str(campaign.get(dbm.campaign_name_column, '')),
                dbm.daily_cap_column: int(float(campaign.get(dbm.daily_cap_column, 9999))),
                dbm.click_cap_column: int(campaign.get(dbm.click_cap_column, 0)),
                dbm.payout_column: round(float(campaign.get(dbm.payout_column, 0.0)), 3)
            }

    new_ids = set(new_data_dict.keys())
    cursor.execute(f"SELECT * FROM campaigns")
    stored_campaigns = {str(row[0]): row for row in cursor.fetchall()}
    existing_ids = set(stored_campaigns.keys())

    changes_text = ""

    new_campaigns = new_ids - existing_ids
    for campaign_id in new_campaigns:
        campaign = new_data_dict[campaign_id]
        new_text = notify_new_campaign(
            "",
            campaign_id,
            campaign[dbm.campaign_name_column],
            campaign.get(dbm.daily_cap_column, 9999),
            campaign.get(dbm.click_cap_column, 0),
            round(campaign.get(dbm.payout_column, 0.0), 3),
        )
        changes_text += new_text

    for campaign_id in (new_ids & existing_ids):
        campaign = new_data_dict[campaign_id]
        old_data = stored_campaigns[campaign_id]
        old_data_dict = {
            dbm.adv_campaign_id_column: str(old_data[0]),
            dbm.campaign_name_column: str(old_data[1]),
            dbm.daily_cap_column: int(float(old_data[2])),
            dbm.click_cap_column: int(old_data[3] if dbm.click_cap_column else 0),
            dbm.payout_column: round(float(old_data[4]), 3)
        }

        differences = {}
        for k in campaign:
            if k in [dbm.payout_column, dbm.daily_cap_column, dbm.click_cap_column]:
                old_value = old_data_dict.get(k, 0.0 if k == dbm.payout_column else 0)
                new_value = campaign.get(k, 0.0 if k == dbm.payout_column else 0)
                if old_value != new_value:
                    differences[k] = new_value

        if differences:
            daily_cap_change = calculate_change(old_data_dict[dbm.daily_cap_column], campaign[dbm.daily_cap_column]) \
                if dbm.daily_cap_column in differences \
                else "0"
            click_cap_change = calculate_change(old_data_dict[dbm.click_cap_column], campaign[dbm.click_cap_column]) \
                if dbm.click_cap_column in differences \
                else "0"
            payout_change = calculate_change(old_data_dict[dbm.payout_column], campaign[dbm.payout_column], True) \
                if dbm.payout_column in differences \
                else "0"

            c_text = notify_campaign_changed(
                "",
                campaign_id,
                campaign[dbm.campaign_name_column],
                daily_cap_change,
                click_cap_change,
                payout_change
            )
            changes_text += c_text

    dbm.insert_or_update_data(data)
    conn.commit()
    conn.close()

    if changes_text == "":
        return
    else:
        return changes_text


# unit test
if __name__ == "__main__":
    advertiser_name = 'advertiser_name1'
    check_for_changes(advertiser_name)
