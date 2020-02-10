import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('cfg/client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('FB Stat wowfactor').sheet1

fields = ['Name', 'Campaign', 'Field', 'Value']


def insert_rows(rows_list: list):
    if creds.access_token_expired:
        client.login()

    sheet.clear()

    rows_list.insert(0, fields)
    log.debug(f'{rows_list=}')
    for row in rows_list:
        log.debug(f'{row=}')
        sheet.append_row(row)
