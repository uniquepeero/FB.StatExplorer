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
    pass