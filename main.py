import sheets
import logging
from utils import get_users

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

data_dict = dict()

if __name__ == '__main__':
    log.info('Started')
    users = get_users()

    for user in users:
        user.generate_report(data_dict)

    log.debug(f'dict after process {data_dict}')
    # sheets.insert_rows(rows)
    log.info('Closed')
