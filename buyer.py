from dataclasses import dataclass
import requests
import logging
from datetime import datetime
from pytz import timezone
from time import sleep

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

_moscow = timezone('Europe/Moscow')


@dataclass
class Buyer:
    name: str
    token: str
    ad_acc: int
    proxies: dict

    def _get_ids(self, path: str) -> list:
        if path not in ('campaigns', 'adsets', 'ads'):
            return None

        params = {
            'access_token': self.token
        }
        url = f'https://graph.facebook.com/v6.0/act_{self.ad_acc}/{path}'

        try:
            res = requests.get(url, params=params, proxies=self.proxies)
            if res.status_code == 200:
                res = res.json()

                if res['data']:
                    ids = [_id['id'] for _id in res['data']]
                    log.debug(f'{path}: {ids}')

                    return ids
            else:
                log.error(f'Request {url} : {res.status_code}')
                return None
        except requests.exceptions.RequestException as e:
            log.error(f'Get ids: {e}')
            self._get_ids(path)
            return None

    def _get_stat(self, path: str, path_id):
        if path == 'campaign':
            additional_field = 'campaign_name,'
        elif path == 'adset':
            additional_field = 'adset_name,campaign_id,'
        elif path == 'ad':
            additional_field = 'ad_name,adset_id,'
        else:
            return None

        params = {
            'fields': 'account_name,'
                      f'{additional_field}'
                      'clicks,'
                      'actions,'
                      'spend',
            'access_token': self.token
        }

        url = f'https://graph.facebook.com/v6.0/{path_id}/insights'
        try:
            res = requests.get(url, params=params, proxies=self.proxies)
            if res.status_code == 200:
                return res.json()
            else:
                log.error(f'Request {url} : {res.status_code}')
                return None
        except requests.exceptions.RequestException as e:
            log.error(f'Get {path} stat ({path_id}): {e}')
            sleep(20)
            self._get_stat(path, path_id)

    def _process_adsets(self, adsets: dict, names: list, ads: list):
        for ad in ads:
            ad_data = self._get_stat('ad', ad)
            log.debug(f'{ad=} : {ad_data=}')
            if ad_data is not None and ad_data['data']:
                ad_data = ad_data['data'][0]
                spend = float(ad_data["spend"].replace(',', '.'))
                clicks = int(ad_data['clicks'])

                user_actions = {
                    'mobile_app_install': 0,
                    'app_custom_event.fb_mobile_complete_registration': 0,
                    'app_custom_event.fb_mobile_purchase': 0,
                }
                for action in ad_data["actions"]:
                    try:
                        user_actions[action["action_type"]] = int(action["value"])
                    except KeyError:
                        continue

                cost_per_click = 0
                if clicks > 0:
                    cost_per_click = round(spend / clicks, 2)
                cost_per_install = 0
                if user_actions['mobile_app_install'] > 0:
                    cost_per_install = round(spend / user_actions['mobile_app_install'], 2)
                cost_per_reg = 0
                if user_actions['app_custom_event.fb_mobile_complete_registration'] > 0:
                    cost_per_reg = round(spend / user_actions[
                        'app_custom_event.fb_mobile_complete_registration'], 2)
                cost_per_purchase = 0
                if user_actions['app_custom_event.fb_mobile_purchase'] > 0:
                    cost_per_purchase = round(spend / user_actions['app_custom_event.fb_mobile_purchase'], 2)

                adsets_dict[ad_data['adset_id']][ad] = {
                    'Ad name': ad_data['ad_name'],
                    'Clicks': clicks,
                    'Spend': spend,
                    'Cost per click': cost_per_click,
                    'Installs': user_actions['mobile_app_install'],
                    'Cost per install': cost_per_install,
                    'Registrations': user_actions['app_custom_event.fb_mobile_complete_registration'],
                    'Cost per registration': cost_per_reg,
                    'Purchases': user_actions['app_custom_event.fb_mobile_purchase'],
                    'Cost per purchase': cost_per_purchase
                }
                acc_names.append(ad_data['account_name'])
                log.debug(f'Processed {ad} for {ad_data["adset_id"]}\n{adsets_dict}')
            else:
                log.debug(f'Empty response ({ad}): {ad_data=}')

    def _process_camps(self, camps: dict, adsets: list):
        for adset in adsets:
            adset_data = self._get_stat('adset', adset)
            log.debug(f'{adset=} : {adset_data=}')
            if adset_data is not None and adset_data['data']:
                adset_data = adset_data['data'][0]
                spend = float(adset_data["spend"].replace(',', '.'))
                clicks = int(adset_data['clicks'])

                user_actions = {
                    'mobile_app_install': 0,
                    'app_custom_event.fb_mobile_complete_registration': 0,
                    'app_custom_event.fb_mobile_purchase': 0,
                }
                for action in adset_data["actions"]:
                    try:
                        user_actions[action["action_type"]] = int(action["value"])
                    except KeyError:
                        continue

                cost_per_click = 0
                if clicks > 0:
                    cost_per_click = round(spend / clicks, 2)
                cost_per_install = 0
                if user_actions['mobile_app_install'] > 0:
                    cost_per_install = round(spend / user_actions['mobile_app_install'], 2)
                cost_per_reg = 0
                if user_actions['app_custom_event.fb_mobile_complete_registration'] > 0:
                    cost_per_reg = round(spend / user_actions['app_custom_event.fb_mobile_complete_registration'], 2)
                cost_per_purchase = 0
                if user_actions['app_custom_event.fb_mobile_purchase'] > 0:
                    cost_per_purchase = round(spend / user_actions['app_custom_event.fb_mobile_purchase'], 2)
                try:
                    camps_dict[adset_data['campaign_id']][adset] = {
                        'Adset name': adset_data['adset_name'],
                        'Clicks': clicks,
                        'Spend': spend,
                        'Cost per click': cost_per_click,
                        'Installs': user_actions['mobile_app_install'],
                        'Cost per install': cost_per_install,
                        'Registrations': user_actions['app_custom_event.fb_mobile_complete_registration'],
                        'Cost per registration': cost_per_reg,
                        'Purchases': user_actions['app_custom_event.fb_mobile_purchase'],
                        'Cost per purchase': cost_per_purchase,
                        'Ads': adsets_dict[adset]
                    }
                    log.debug(f'Processed {adset} for {adset_data["campaign_id"]}\n{camps_dict}')
                except KeyError as e:
                    log.error(f'{e} not found {adsets_dict=}')
            else:
                log.debug(f'Empty response ({adset}): {adset_data=}')

    def _process_users(self, users: dict, camps: list):
        for camp in camps:
            camp_data = self._get_stat('campaign', camp)
            log.debug(f'{camp=} : {camp_data=}')
            if camp_data is not None and camp_data['data']:
                camp_data = camp_data['data'][0]
                spend = float(camp_data["spend"].replace(',', '.'))
                clicks = int(camp_data['clicks'])

                user_actions = {
                    'mobile_app_install': 0,
                    'app_custom_event.fb_mobile_complete_registration': 0,
                    'app_custom_event.fb_mobile_purchase': 0,
                }
                for action in camp_data["actions"]:
                    try:
                        user_actions[action["action_type"]] = int(action["value"])
                    except KeyError:
                        continue

                cost_per_click = 0
                if clicks > 0:
                    cost_per_click = round(spend / clicks, 2)
                cost_per_install = 0
                if user_actions['mobile_app_install'] > 0:
                    cost_per_install = round(spend / user_actions['mobile_app_install'], 2)
                cost_per_reg = 0
                if user_actions['app_custom_event.fb_mobile_complete_registration'] > 0:
                    cost_per_reg = round(spend / user_actions['app_custom_event.fb_mobile_complete_registration'], 2)
                cost_per_purchase = 0
                if user_actions['app_custom_event.fb_mobile_purchase'] > 0:
                    cost_per_purchase = round(spend / user_actions['app_custom_event.fb_mobile_purchase'], 2)
                try:
                    user_dict[camp_data["account_name"]][camp] = {
                        'Campaign name': camp_data['campaign_name'],
                        'Clicks': clicks,
                        'Spend': spend,
                        'Cost per click': cost_per_click,
                        'Installs': user_actions['mobile_app_install'],
                        'Cost per install': cost_per_install,
                        'Registrations': user_actions['app_custom_event.fb_mobile_complete_registration'],
                        'Cost per registration': cost_per_reg,
                        'Purchases': user_actions['app_custom_event.fb_mobile_purchase'],
                        'Cost per purchase': cost_per_purchase,
                        'AdSets': camps_dict[camp]
                    }
                    log.debug(f'Processed {camp} for {camp_data["account_name"]}\n{user_dict}')
                except KeyError as e:
                    log.error(f'{e} not found {camps_dict=}')
            else:
                log.debug(f'Empty response ({camp}): {camp_data=}')

    def generate_report(self) -> dict:
        time = datetime.now(_moscow).strftime("%d.%m.%Y %H:%M")

        camps = self._get_ids('campaigns')
        adsets = self._get_ids('adsets')
        ads = self._get_ids('ads')
        acc_names = []

        adsets_dict = {}
        camps_dict = {}
        user_dict = {}
        if adsets is not None:
            for adset in adsets:
                adsets_dict[adset] = {}

        if ads is not None:
            self._process_adsets(adsets_dict, acc_names, ads)

        if adsets_dict and camps:
            for camp in camps:
                camps_dict[camp] = {}
            self._process_camps(camps_dict, adsets)

        if camps_dict and acc_names:
            for acc_name in acc_names:
                user_dict[acc_name] = {}
            self._process_users(user_dict, campsa)

        if user_dict:
            return user_dict
        else:
            return None
