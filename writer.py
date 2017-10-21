#! /usr/bin/env python

import csv
import vk_api

token = '62c3be70c2ca81fb42ac7b27a191519631c6f053c4d6a6261ffec1194a259825869fb70eca214a0f3694f'
vk = vk_api.VkApi(token=token)

values = {'out': 0, 'count': 100, 'time_offset': 5}


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


class Writer:
    def __init__(self):
        pass

    @staticmethod
    def write_message(user_id, message):
        vk.method('messages.send', {'user_id': user_id, 'message': message})

    @staticmethod
    def write_main_message_by_id(user_id, text, item_id):
        Writer.write_message(user_id, text.get_by_id(item_id)[0])
