#! /usr/bin/env python
import argparse
import csv
import resources
import time
import writer
from users import Users


def main():
    parser = argparse.ArgumentParser(description='Lovely bot.')
    parser.add_argument('--backup', dest='backup', action='store_true',
                        default=False, help='Restore from backup')
    args = parser.parse_args()

    users = Users()
    if args.backup:
        users.restore_from_backup()
    already_read = {}

    # Main loop
    while True:
        response = writer.vk.method('messages.get', writer.values)
        for item in response['items']:
            if already_read.get(item[u'user_id']) and already_read.get(item[u'user_id']) >= item[u'id']:
                continue
            if not users.check_debug(item):
                users.check_user(int(item[u'user_id']))

            users.set_answer(int(item[u'user_id']), item[u'body'])
            already_read[item[u'user_id']] = item[u'id']

        users.update()
        time.sleep(1)


if __name__ == "__main__":
    main()
