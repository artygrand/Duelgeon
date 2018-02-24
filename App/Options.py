#!/usr/bin/env python3

import os

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

from Utils import win


class Options:
    __path = ''
    __config = None
    __default = {}

    win_size = ''
    fullscreen = 1
    fov = 90

    volume = 80
    music_vol = 100
    sfx_vol = 100

    key_forward = 'w'
    key_left = 'a'
    key_back = 's'
    key_right = 'd'
    key_crouch = 'lcontrol'
    key_jump = 'space'
    key_ability1 = 'lshift'
    key_ability2 = 'e'
    key_ability3 = 'q'
    key_fire1 = 'mouse1'
    key_fire2 = 'mouse3'

    mouse_sensitivity = 7
    invert_mouse = 0

    @classmethod
    def load(cls, file):
        cls.win_size = '{} {}'.format(base.pipe.getDisplayWidth(), base.pipe.getDisplayHeight())
        cls.__path = file
        cls.__config = ConfigParser()

        if not os.path.exists(file):
            cls.__config['opts'] = {}
            return

        cls.__config.read(file)

        for name, val in cls.__config['opts'].items():
            if hasattr(cls, name):
                cls.__default[name] = getattr(cls, name)
                setattr(cls, name, val)

    @classmethod
    def update(cls, name, val):
        if name in cls.__default:
            if val == cls.__default[name]:
                del cls.__default[name]
                del cls.__config['opts'][name]
            else:
                cls.__config['opts'][name] = str(val)
        elif val != getattr(cls, name):
            cls.__default[name] = getattr(cls, name)
            cls.__config['opts'][name] = str(val)

        setattr(cls, name, val)

    @classmethod
    def default(cls, name):
        return cls.__default[name] if name in cls.__default else getattr(cls, name)

    @classmethod
    def apply(cls):
        base.messenger.send('Options-changed')

        win.toggle_fullscreen(cls.fullscreen)
        win.change_resolution(*cls.win_size.split())
        base.camLens.setFov(float(cls.fov))

    @classmethod
    def save(cls):
        with open(cls.__path, 'w') as file:
            cls.__config.write(file)

    @classmethod
    def menu_items(cls):
        return [
            {'title': 'Video', 'type': 'label'},

            {
                'title': 'Resolution',
                'name': 'win_size',
                'type': 'options',
                'value': cls.win_size,
                'items': ['640 480', '1280 720', '1366 768', '1440 900', '1600 900', '1920 1080']
            },
            {
                'title': 'Fullscreen',
                'name': 'fullscreen',
                'type': 'check',
                'value': cls.fullscreen,
            },
            {
                'title': 'Field of view',
                'name': 'fov',
                'type': 'slider',
                'value': cls.fov,
                'range': (60, 120)
            },

            {'type': 'separator'},
            {'title': 'Audio', 'type': 'label'},

            {
                'title': 'Master volume',
                'name': 'volume',
                'type': 'slider',
                'value': cls.volume,
                'range': (0, 100)
            },
            {
                'title': 'Music volume',
                'name': 'music_vol',
                'type': 'slider',
                'value': cls.music_vol,
                'range': (0, 100)
            },
            {
                'title': 'Sound effects volume',
                'name': 'sfx_vol',
                'type': 'slider',
                'value': cls.sfx_vol,
                'range': (0, 100)
            },

            {'type': 'separator'},
            {'title': 'Controls', 'type': 'label'},

            {
                'title': 'Mouse sensitivity',
                'name': 'mouse_sensitivity',
                'type': 'slider',
                'value': cls.mouse_sensitivity,
                'range': (0, 100)
            },
            {
                'title': 'Invert mouse',
                'name': 'invert_mouse',
                'type': 'check',
                'value': cls.invert_mouse,
            },
            {'title': 'Forward',        'name': 'key_forward',  'type': 'key', 'value': cls.key_forward},
            {'title': 'Back',           'name': 'key_back',     'type': 'key', 'value': cls.key_back},
            {'title': 'Left',           'name': 'key_left',     'type': 'key', 'value': cls.key_left},
            {'title': 'Right',          'name': 'key_right',    'type': 'key', 'value': cls.key_right},
            {'title': 'Crouch',         'name': 'key_crouch',   'type': 'key', 'value': cls.key_crouch},
            {'title': 'Jump',           'name': 'key_jump',     'type': 'key', 'value': cls.key_jump},
            {'title': 'Ability 1',      'name': 'key_ability1', 'type': 'key', 'value': cls.key_ability1},
            {'title': 'Ability 2',      'name': 'key_ability2', 'type': 'key', 'value': cls.key_ability2},
            {'title': 'Ultimate',       'name': 'key_ability3', 'type': 'key', 'value': cls.key_ability3},
            {'title': 'Primary fire',   'name': 'key_fire1',    'type': 'key', 'value': cls.key_fire1},
            {'title': 'Secondary fire', 'name': 'key_fire2',    'type': 'key', 'value': cls.key_fire2}
        ]
