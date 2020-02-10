import sheets
import logging
from utils import get_users

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

rows = []

if __name__ == '__main__':
    log.info('Started')
    users = get_users()

    for user in users:
        camps = user.get_camps()
        log.debug(f'{user.name=} {camps=}')
        user.generate_rows(camps, rows)
        log.debug(f'rows after append {rows}')

    sheets.insert_rows(rows)
    log.info('Closed')

# TODO добавить группировку по ад сетам и крео
# TODO изменить логику вставки в таблицы
