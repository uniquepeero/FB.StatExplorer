import sheets
import logging
import utils

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/app.log', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

data_dict = dict()

if __name__ == '__main__':
    log.info('Started')
    users = utils.get_users()

    for user in users:
        data_dict[user.name] = user.generate_report()

    log.debug(f'Dict after process {data_dict}')

    csv = utils.create_csv(data_dict)
    sheets.client.import_csv(sheets.sheet.id, csv)

    log.info('Closed')
