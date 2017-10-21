#! /usr/bin/env python

from writer import Text

text = Text('main.csv')
secondary = {1: Text('1.csv'), 9: Text('9.csv')}
answers = {1: ['Да', 'ДА', 'да', 'ок', 'Ок'], 9: ['Да', 'ДА', 'да', 'ок', 'Ок']}

with open('stupid_answers.txt') as file:
    stupid_answers = [line for line in file]