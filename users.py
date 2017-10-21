#! /usr/bin/env python

from datetime import datetime, timedelta
import random
from resources import *
import time
from writer import Writer


class User:
    def __init__(self, user_id):
        self.id = user_id

        self.text = text
        self.last_message_id = 0
        self.root_message_id = 0
        self.time = 0

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
        if not answer == 0 and answer not in answers.get(self.root_message_id):
            Writer.write_message(self.id, stupid_answers[random.randint(0, 6)])
        return False

    def send_message(self):
        Writer.write_main_message_by_id(self.id, self.text, self.last_message_id + 1)
        self.last_message_id += 1
        self.time = datetime.now()

    def checkout_master(self):
        if not self.root_message_id == 0:
            self.text = text
            self.last_message_id = self.root_message_id
            self.root_message_id = 0

    def checkout_secondary(self):
        self.root_message_id = self.last_message_id
        self.last_message_id = 0
        self.text = secondary[self.root_message_id]

    def send_message_if_needed(self, answer=0):
        if self.last_message_id == 0 and self.root_message_id == 0:
            self.send_message()
        else:
            if self.is_branch_here():
                self.checkout_secondary()
            if self.is_right_answer(answer):
                self.checkout_master()
            delay = self.text.get_by_id(self.last_message_id)[1]
            delta = timedelta(seconds=delay)

            if self.time + delta < datetime.now() and self.last_message_id < len(self.text.get_items()) - 1:
                self.send_message()


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
            if user.id in self.answers.keys():
                user.send_message_if_needed(self.answers.pop(user.id))
            else:
                user.send_message_if_needed()
        self.backup_user_ids()

    def check_debug(self, item):
        if item[u'body'] == '/ping':
            Writer.write_message(item[u'user_id'], 'Все в порядке')
            return True
        if item[u'body'] == '/count':
            Writer.write_message(item[u'user_id'], str(len(self.user_ids)))
            return True
        return False
