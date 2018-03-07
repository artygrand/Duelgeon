#!/usr/bin/env python3


class Hero:
    def __init__(self, params):
        self.params = params
        # TODO init sizes, armor, abilities and weapons

        self.params['height'] = 1.75
        self.params['crouch_height'] = 1.2
        self.params['width'] = .8
        self.params['mass'] = 80
        self.params['speed'] = 5.5
        self.params['jumps_limit'] = 2
        self.params['jump_height'] = 10

        self.__jumps_limit = self.params['jumps_limit']

    def get(self, key):
        return self.params[key]

    def for_kcc(self):
        return {
            'height': self.params['height'],
            'crouch_height': self.params['crouch_height'],
            'radius': self.params['width'] / 2,
            'mass': self.params['mass'],
            'name': self.params['name'],
        }

    @property
    def jumps_limit(self):
        self.__jumps_limit -= 1
        return self.__jumps_limit + 1

    def reset_jumps_limit(self):
        self.__jumps_limit = self.params['jumps_limit']


def get_active_hero():
    params = {  # TODO get dict from saved file
            'name': 'Players first Hero',
            'health': 200,
            'speed_deg': 2,
            'mana': 50,
            'mana_regen': 5,
            'weapon_1': {
                'some_params': 20,
                'modifiers': [],
                'traits': []
            },
            'weapon_2': {
                'obj': 'Initialized object with params',
                'some_params': 20,
                'modifiers': [],
                'traits': []
            },
            'ability_1': {
                'class': 'ClassName1',
                'stage': 1,
            },
            'ability_2': {
                'class': 'ClassName2',
                'stage': 2,
            },
            'ability_3': {
                'class': 'ClassName3',
            },
            'armor': {
                'type': 'light',
                'modifiers': []
            }
        }

    return Hero(params)


def make_enemy():
    params = {}  # TODO Overlord should generate it

    return Hero(params)
