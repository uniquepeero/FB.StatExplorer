from os import path
from configparser import ConfigParser
from buyer import Buyer
import csv


def get_users():
    users = []
    if path.isfile('cfg/users.cfg') and path.isfile('cfg/names.cfg'):
        with open('cfg/names.cfg', 'r') as names_file:
            names = names_file.read().splitlines()
        config = ConfigParser()
        config.read('cfg/users.cfg')
        for name in names:
            token = config[name]['token']
            ad_acc = config[name]['ad_acc']
            proxies = {
                'http': config[name]['proxy'],
                'https': config[name]['proxy']
            }
            users.append(Buyer(name, token, ad_acc, proxies))
    else:
        # log.critical('Config file not found')
        raise IOError

    return users


def create_csv(data_dict: dict):
    with open('temp/stat.csv', mode='a', encoding="utf-8", newline='') as out_file:
        writer = csv.writer(out_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Buyer',
                         'Ad Account',
                         'Campaign ID',
                         'Campaign Statistic',
                         'Ad Set ID',
                         'Ad Set Statistic',
                         'Ad ID',
                         'Ad Statistic'])

        for user, ad_accs in data_dict.items():
            writer.writerow([user])

            for ad_acc, camps in ad_accs.items():
                writer.writerow(['', ad_acc])

                for camp, camp_stats in camps.items():
                    writer.writerow(['', '', camp])

                    for camp_stat, values in camp_stats.items():
                        if camp_stat != 'AdSets':
                            writer.writerow(['', '', '', camp_stat, values])
                        else:
                            writer.writerow(['', '', '', camp_stat])

                        for adset_id, adset_stats in camp_stats['AdSets'].items():
                            writer.writerow(['', '', '', '', adset_id])

                            for adset_stat_name, adset_stat_value in adset_stats.items():
                                if adset_stat_name != 'Ads':
                                    writer.writerow(['', '', '', '', '', adset_stat_name, adset_stat_value])
                                else:
                                    writer.writerow(['', '', '', '', '', adset_stat_name])

                                for ad_id, ad_stats in adset_stats['Ads'].items():
                                    writer.writerow(['', '', '', '', '', '', ad_id])

                                    for ad_stat_name, ad_stat_value in ad_stats.items():
                                        writer.writerow(['', '', '', '', '',  '',  '', ad_stat_name, ad_stat_value])

    with open('temp/stat.csv', mode='r', encoding="utf-8") as csv_file:
        return csv_file.read()
