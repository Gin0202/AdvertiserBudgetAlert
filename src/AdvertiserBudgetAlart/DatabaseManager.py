# DatabaseManager.py
import os
import sqlite3
from typing import Dict

import requests

from .Settings.config import keys


def get_json_data(advertiser_name, max_retries=5, backoff_factor=0.5):
    import time
    retries = 0
    config = keys[advertiser_name]
    api_url = config['request_url']
    top_key = config['top_key']

    daily_cap_column = config.get('daily_cap', 'daily_cap')
    click_cap_column = config.get('click_cap', 'click_cap')
    payout_column = config.get('payout', 'payout')

    while retries < max_retries:
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            campaigns = data.get(top_key, [])

            for campaign in campaigns:
                campaign[daily_cap_column] = int(float(campaign.get(daily_cap_column, '9999')))
                campaign[click_cap_column] = int(float(campaign.get(click_cap_column, '0')))
                campaign[payout_column] = float(campaign.get(payout_column, '0.000'))

            return campaigns
        except requests.RequestException as e:
            print(f"Request fail，code：{e.response.status_code if e.response else '无'}，retries：{retries + 1}")
            retries += 1
            time.sleep(backoff_factor * (2 ** retries))


class DatabaseManager:
    def __init__(self, advertiser_name):
        self.advertiser_name: str = advertiser_name
        self.db_path: str = self._get_db_path(advertiser_name)
        self.config: Dict = keys[advertiser_name]

        self.adv_campaign_id_column: str = self.config.get('adv_campaign_id', 'adv_campaign_id') \
            if self.config.get('adv_campaign_id') != '' \
            else 'adv_campaign_id'
        self.campaign_name_column: str = self.config.get('campaign_name', 'campaign_name') \
            if self.config.get('campaign_name') != '' \
            else 'campaign_name'
        self.daily_cap_column: str = self.config.get('daily_cap', 'daily_cap') \
            if self.config.get('daily_cap') != '' \
            else 'daily_cap'
        self.click_cap_column: str = self.config.get('click_cap', 'click_cap') \
            if self.config.get('click_cap') != '' \
            else 'click_cap'
        self.payout_column: str = self.config.get('payout', 'payout') \
            if self.config.get('payout') != '' \
            else 'payout'

    @staticmethod
    def _get_db_path(advertiser_name):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        database_path = os.path.join(script_dir, 'Database')
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return os.path.join(database_path, f"{advertiser_name}.db")

    def create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS campaigns (
                    {self.adv_campaign_id_column} TEXT,
                    {self.campaign_name_column} TEXT,
                    {self.daily_cap_column} INT,
                    {self.click_cap_column} INT,
                    {self.payout_column} REAL
                )
            ''')
            conn.commit()

    def insert_or_update_data(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT {self.adv_campaign_id_column} FROM campaigns")
            existing_ids = {row[0] for row in cursor.fetchall()}

            for item in data:
                campaign_id = str(item[self.adv_campaign_id_column]).strip()
                if campaign_id in existing_ids:
                    self._update_campaign(cursor, item)
                else:
                    self._insert_campaign(cursor, item)
            conn.commit()

    def _update_campaign(self, cursor, campaign):
        id_value: str = campaign.get(self.adv_campaign_id_column)
        name_value: str = campaign.get(self.campaign_name_column)

        daily_cap_value: int = int(float(campaign.get(self.daily_cap_column, 0)))
        click_cap_value: int = int(float(campaign.get(self.click_cap_column, 0)))

        payout_value: float = round(float(campaign.get(self.payout_column, 0.000)), 3)

        cursor.execute(
            f'''
            UPDATE campaigns SET 
                {self.campaign_name_column} = ?, 
                {self.daily_cap_column} = ?, 
                {self.click_cap_column} = ?, 
                {self.payout_column} = ?
            WHERE 
                {self.adv_campaign_id_column} = ?
            ''',
            (name_value, daily_cap_value, click_cap_value, payout_value, id_value)
        )

    def _insert_campaign(self, cursor, campaign):
        id_value: str = campaign.get(self.adv_campaign_id_column)
        name_value: str = campaign.get(self.campaign_name_column)

        daily_cap_value: int = int(float(campaign.get(self.daily_cap_column, 0)))
        click_cap_value: int = int(float(campaign.get(self.click_cap_column, 0)))

        payout_value: float = round(float(campaign.get(self.payout_column, 0.000)), 3)
        cursor.execute(
            f'''
            INSERT INTO campaigns (
                {self.adv_campaign_id_column}, 
                {self.campaign_name_column}, 
                {self.daily_cap_column}, 
                {self.click_cap_column}, 
                {self.payout_column})
            VALUES (?, ?, ?, ?, ?)
            ''',
            (id_value, name_value, daily_cap_value, click_cap_value, payout_value)
        )


def main():
    for advertiser_name in keys:
        data = get_json_data(advertiser_name)
        if data:
            db_manager = DatabaseManager(advertiser_name)
            db_manager.create_table()
            db_manager.insert_or_update_data(data)


if __name__ == "__main__":
    main()
