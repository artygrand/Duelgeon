#!/usr/bin/env python3

from copy import copy
from panda3d.core import Vec3
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject

from Utils import win
import App
from App.KCC import CharacterController
from App.Options import Options


class Character:
    name = 'Buster'
    height = 1.75
    crouch_height = 1.3
    step_height = 0.3
    radius = 0.4
    speed = 5.5
    jump_height = 1.5

    paused = False

    yaw = 0
    pitch = 0
    crouching = False
    movement = Vec3(0, 0, 0)
    omega = 0

    def __init__(self, world, parent, name):
        self.name = name
        self.char = CharacterController(world, parent, self.height, self.crouch_height, self.step_height, self.radius)

        self.resume()
        base.taskMgr.add(self.__update, 'update_char_' + self.name)

    def resume(self):
        App.paused = False

    def pause(self):
        App.paused = True

    def destroy(self):
        base.taskMgr.remove('update_char_' + self.name)

    def __update(self, task):
        if App.paused:
            return task.cont

        movement = copy(self.movement)
        if movement.getY() > 0:
            movement.setY(movement.getY() * 1.5)

        self.char.set_linear_movement(movement * self.speed)
        self.char.set_angular_movement(self.omega)
        self.char.update()

        return task.cont

    def move(self, vector):
        self.movement = vector

    def stop(self):
        self.movement = Vec3(0, 0, 0)

    def rotate(self, omega):
        self.omega = omega

    def jump(self):
        if App.paused:
            return

        self.char.start_jump(self.jump_height)

    def crouch(self, start):
        self.crouching = start

        if start:
            self.char.start_crouch()
        else:
            self.char.stop_crouch()

    def fly(self, start):
        if start:
            self.char.start_fly()
        else:
            self.char.stop_fly()

    def ability1(self, start):
        if App.paused:
            return

        print('ability1', start)

    def ability2(self, start):
        if App.paused:
            return

        print('ability2', start)

    def ability3(self):
        if App.paused:
            return

        print('ultimate start')

    def fire1(self):
        if App.paused:
            return

        print('primary fired')

    def fire2(self):
        if App.paused:
            return

        print('secondary fired')


class Player(Character):
    camera = None

    def attach_controls(self):
        inputState.watchWithModifiers('forward', Options.key_forward)
        inputState.watchWithModifiers('left', Options.key_left)
        inputState.watchWithModifiers('back', Options.key_back)
        inputState.watchWithModifiers('right', Options.key_right)

        base.accept(Options.key_crouch, self.crouch, [True])
        base.accept(Options.key_crouch + '-up', self.crouch, [False])
        base.accept(Options.key_jump, self.jump)
        base.accept(Options.key_ability1, self.ability1, [True])
        base.accept(Options.key_ability1 + '-up', self.ability1, [False])
        base.accept(Options.key_ability2, self.ability2, [True])
        base.accept(Options.key_ability2 + '-up', self.ability2, [False])
        base.accept(Options.key_ability3, self.ability3)

        base.taskMgr.add(self.keyboard_watcher, 'player_keyboard_watcher')

        if base.mouseWatcherNode.hasMouse():
            win.center_cursor()
            base.taskMgr.add(self.mouse_watcher, 'player_mouse_watcher', appendTask=True,
                             extraArgs=[int(Options.mouse_sensitivity), Options.invert_mouse])

            inputState.watchWithModifiers('fire1', Options.key_fire1)
            inputState.watchWithModifiers('fire2', Options.key_fire2)

    def mouse_watcher(self, sens, invert, task):
        if App.paused:
            return task.cont

        md = base.win.getPointer(0)
        x, y = md.getX(), md.getY()

        win.center_cursor()
        self.omega = (base.win.getXSize() / 2 - x) * sens * 5  # TODO проверить на разных разрешениях
        self.yaw = self.yaw + self.omega

        delta = (base.win.getYSize() / 2 - y) * sens / 50
        delta *= [1, -1][invert]
        self.pitch = self.pitch + delta
        if self.pitch > 90:
            self.pitch = 90
        if self.pitch < -90:
            self.pitch = -90

        if inputState.isSet('fire1'):
            self.fire1()
        if inputState.isSet('fire2'):
            self.fire2()

        return task.cont

    def keyboard_watcher(self, task):
        if App.paused:
            return task.cont

        m = Vec3(0, 0, 0)
        if inputState.isSet('forward'):
            m.setY(1)
        elif inputState.isSet('back'):
            m.setY(-1)
        if inputState.isSet('left'):
            m.setX(-1)
        elif inputState.isSet('right'):
            m.setX(1)
        self.movement = m

        return task.cont

    def set_camera(self, camera):
        self.camera = camera
        base.taskMgr.add(self.update_camera, 'player_camera')

    def update_camera(self, task):
        self.camera.setHpr(self.char.getH(), self.pitch, 0)
        self.camera.setPos(self.char.movement_parent, 0, 0, (self.crouch_height if self.crouching else self.height)-.2)

        return task.cont

    def destroy(self):
        Character.destroy(self)
        base.taskMgr.remove('player_keyboard_watcher')
        base.taskMgr.remove('player_mouse_watcher')
        base.taskMgr.remove('player_camera')
