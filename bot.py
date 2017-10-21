#! /usr/bin/env python
import vk_api
import csv
import datetime
from datetime import timedelta
import io
import argparse
import time

token = '62c3be70c2ca81fb42ac7b27a191519631c6f053c4d6a6261ffec1194a259825869fb70eca214a0f3694f'
vk = vk_api.VkApi(token = token)

values = {'out': 0,'count': 100,'time_offset': 5}


class Text:
    def __init__(self, file_name):
        self.item = {}
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.item[int(row['Номер'])] = (row['Текст'], int(row['Время']))

    def get_by_id(self, id):
        return self.item.get(id)

    def get_items(self):
        return self.item


text = Text('main.csv')
secondary= {}
secondary[1] = Text('1.csv')

answers = {}
answers[1] = ['Да', 'ДА', 'да', 'ок', 'Ок']


class Writer:
    def __init__(self):
        pass

    def add_text_main_db(self, text):
        self.text = text

    def write_message(self, user_id, message):
        vk.method('messages.send', {'user_id' : user_id, 'message' : message})

    def write_main_message_by_id(self, user_id, text, item_id):
        self.write_message(user_id, text.get_by_id(item_id)[0])


writer = Writer()
writer.add_text_main_db(text)


class User:
    def __init__(self, user_id):
        self.id = user_id
        self.last_message_id = 0
        self.root_message_id = 0
        self.time = 0
        self.text = text

    def set_last_message_id(self, message_id):
        self.last_message_id = message_id

    def set_time_of_last_message(self, time):
        self.time = time

    def is_branch_here(self):
        if self.root_message_id == 0 and self.last_message_id in secondary.keys():
            return True
        return False

    def is_right_answer(self, answer):
        if not answer == 0 and answer in answers.get(self.root_message_id):
            return True
        return False

    def send_message_if_needed(self, answer = 0):
        if self.last_message_id == 0:
            writer.write_main_message_by_id(self.id, self.text, 1)
            self.last_message_id += 1
            self.time = datetime.datetime.now()
        else:
            if self.is_branch_here():
                self.root_message_id = self.last_message_id
                self.last_message_id = 0
                self.text = secondary[self.root_message_id]
            if not self.root_message_id == 0:
                if self.is_right_answer(answer):
                    self.text = text
                    self.last_message_id = self.root_message_id
                    self.root_message_id = 0
            delay = self.text.get_by_id(self.last_message_id)[1]
            delta = timedelta(seconds=delay)

            if self.time + delta < datetime.datetime.now() and self.last_message_id < len(self.text.get_items()) - 1:
                writer.write_main_message_by_id(self.id, self.text, self.last_message_id + 1)
                self.last_message_id += 1
                self.time = datetime.datetime.now()


class Users:
    def __init__(self):
        self.user_ids = []
        self.users = []
        self.answers = {}

    def backup_user_ids(self):
        with open('users.txt', 'w') as file:
            file.seek(0)
            file.truncate()
            for user in self.users:
                file.write(str(user.id) + ',' + str(user.last_message_id) + ',' + str(user.time.toordinal()))

    def restore_from_backup(self):
        with open('users.txt') as file:
            for line in file:
                line = line.split(',')
                user = User(int(line[0]))
                user.set_last_message_id(int(line[1]))
                user.set_time_of_last_message(datetime.datetime.utcfromtimestamp(int(line[2])))
                self.users.append(user)
                self.user_ids.append(int(line[0]))

    def check_user(self, user_id):
        if user_id not in self.user_ids:
            new_user = User(user_id)
            self.users.append(new_user)
            self.user_ids.append(user_id)

    def set_answer(self, user_id, answer):
        self.answers[user_id] = answer

    def update(self):
        for user in self.users:
            print(self.answers.get(user.id))
            if user.id in self.answers.keys():
                user.send_message_if_needed(self.answers.pop(user.id))
            else:
                user.send_message_if_needed()
        self.backup_user_ids()

    def check_debug(self, item):
        if (item[u'body'] == '/ping'):
            writer.write_message(item[u'user_id'], 'Все в порядке')
            return True
        if (item[u'body'] == '/count'):
            writer.write_message(item[u'user_id'], str(len(self.user_ids)))
            return True
        return False


def main():
    parser = argparse.ArgumentParser(description='Lovely bot.')
    parser.add_argument('--backup', dest='backup', action='store_true',
                        default=False,
                        help='Restore from backup')
    args = parser.parse_args()

    users = Users()
    if args.backup:
        users.restore_from_backup()
    already_read = {}

    # Main loop
    while True:
        response = vk.method('messages.get', values)
        for item in response['items']:
            if already_read.get(item[u'user_id']) and already_read.get(item[u'user_id'])  >= item[u'id']:
                continue
            if not users.check_debug(item):
                users.check_user(int(item[u'user_id']))

            users.set_answer(int(item[u'user_id']), item[u'body'])
            already_read[item[u'user_id']] = item[u'id']

        users.update()
        time.sleep(1)


if __name__ == "__main__":
    main()