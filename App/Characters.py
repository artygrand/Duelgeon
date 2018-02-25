#!/usr/bin/env python3

from copy import copy
from panda3d.core import Vec3

import App
from App.KCC import CharacterController


class Dummy:
    def __init__(self):
        self.body = render.attachNewNode('Free camera')
        self.movement = Vec3(0)
        self.omega = 0
        self.pitch = 0

        base.taskMgr.add(self.__update, 'update_dummy_character')

        self.getHpr = self.body.getHpr
        self.getPos = self.body.getPos
        self.setHpr = self.body.setHpr
        self.setPos = self.body.setPos

    def __update(self, task):
        self.body.setPos(self.body.getPos() + self.body.getQuat(render).xform(self.movement) / 4)
        self.body.setHpr(self.body.getH() + self.omega * globalClock.getDt(), self.pitch, 0)

        return task.cont


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

        self.getHpr = self.char.getHpr
        self.getPos = self.char.getPos

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
