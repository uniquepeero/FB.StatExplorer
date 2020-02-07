from dataclasses import dataclass
import requests


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
        res = requests.get(url, params=params, proxies=self.proxies)
        res = res.json()

        camps = [camp['id'] for camp in res['data']]

        return camps

    def get_camp_stat(self, camp_id):
        params = {
            'fields': 'account_name,'
                      'campaign_name,'
                      'clicks,'
                      'actions,'
                      'spend,'
                      'cost_per_ad_click,'
                      'cost_per_inline_link_click,'
                      'cost_per_outbound_click'
                      'cost_per_unique_click'
                      'cost_per_unique_inline_link_click'
                      'cost_per_unique_outbound_click',
            'access_token': self.token
        }

        url = f'https://graph.facebook.com/v6.0/{camp_id}/insights'
        res = requests.get(url, params=params, proxies=self.proxies)

        return res.json()

    def generate_dict(self, stat):
        info = {
            'name': self.name
        }
