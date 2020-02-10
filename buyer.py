from dataclasses import dataclass
import requests
import logging
from datetime import datetime
from pytz import timezone

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

    def get_camps(self):
        params = {
            'access_token': self.token
        }
        url = f'https://graph.facebook.com/v6.0/act_{self.ad_acc}/campaigns'

        try:
            res = requests.get(url, params=params, proxies=self.proxies)
            if res.status_code == requests.codes.ok:
                res = res.json()

                if res['data']:
                    camps = [camp['id'] for camp in res['data']]
                    log.debug(camps)

                    return camps
            else:
                log.error(f'Request {url} : {res.status_code}')
        except requests.exceptions.RequestException as e:
            log.error(f'Getting camps error: {e}')

    def _get_camp_stat(self, camp_id):
        params = {
            'fields': 'account_name,'
                      'campaign_name,'
                      'clicks,'
                      'actions,'
                      'spend,'
                      'cost_per_ad_click,'
                      'cost_per_inline_link_click,'
                      'cost_per_outbound_click,'
                      'cost_per_unique_click,'
                      'cost_per_unique_inline_link_click,'
                      'cost_per_unique_outbound_click',
            'access_token': self.token
        }

        url = f'https://graph.facebook.com/v6.0/{camp_id}/insights'
        try:
            res = requests.get(url, params=params, proxies=self.proxies)
            if res.status_code == requests.codes.ok:
                return res.json()
            else:
                log.error(f'Request {url} : {res.status_code}')
        except requests.exceptions.RequestException as e:
            log.error(f'Getting stat error: {e}')

    def generate_rows(self, camps: list, rows_list: list):
        for camp in camps:
            time = datetime.now(_moscow).strftime("%d.%m.%Y %H:%M")

            data = self._get_camp_stat(camp)
            log.debug(data)
            if data["data"]:
                data = data["data"][0]

                spend = float(data["spend"].replace(',', '.'))
                clicks = int(data['clicks'])

                user_actions = {
                    'mobile_app_install': 0,
                    'app_custom_event.fb_mobile_complete_registration': 0,
                    'app_custom_event.fb_mobile_purchase': 0,
                }
                for action in data["actions"]:
                    try:
                        user_actions[action["action_type"]] = int(action["value"])
                    except KeyError:
                        continue

                cost_per_click = 0
                if clicks > 0:
                    cost_per_click = spend / clicks
                cost_per_install = 0
                if user_actions['mobile_app_install'] > 0:
                    cost_per_install = spend / user_actions['mobile_app_install']
                cost_per_reg = 0
                if user_actions['app_custom_event.fb_mobile_complete_registration'] > 0:
                    cost_per_reg = spend / user_actions['app_custom_event.fb_mobile_complete_registration']
                cost_per_purchase = 0
                if user_actions['app_custom_event.fb_mobile_purchase'] > 0:
                    cost_per_purchase = spend / user_actions['app_custom_event.fb_mobile_purchase']

                rows_list.extend(
                    [
                        [
                            f'{self.name} / {data["account_name"]} / {time}',
                            f'{data["campaign_name"]} ({camp})'
                        ],
                        [
                            '',
                            '',
                            'Clicks',
                            clicks
                        ],
                        [
                            '',
                            '',
                            'Spend',
                            spend
                        ],
                        [
                            '',
                            '',
                            'Cost per click',
                            cost_per_click
                        ],
                        [
                            '',
                            '',
                            'Installs',
                            user_actions['mobile_app_install']
                        ],
                        [
                            '',
                            '',
                            'Cost per install',
                            cost_per_install
                        ],
                        [
                            '',
                            '',
                            'Registrations',
                            user_actions['app_custom_event.fb_mobile_complete_registration']
                        ],
                        [
                            '',
                            '',
                            'Cost per registration',
                            cost_per_reg
                        ],
                        [
                            '',
                            '',
                            'Purchases',
                            user_actions['app_custom_event.fb_mobile_purchase']
                        ],
                        [
                            '',
                            '',
                            'Cost per purchase',
                            cost_per_purchase
                        ],
                    ])

                # return rows_list
            else:
                log.debug('Empty response')
                continue
