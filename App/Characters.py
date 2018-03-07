#!/usr/bin/env python3

from panda3d.core import Vec3

from App.KCC import CharacterController


class Dummy:
    def __init__(self):
        self.body = render.attachNewNode('Free camera')
        self.__move = Vec3(0)
        self.__yaw = 0
        self.__pitch = 0
        self.speed = 50

        self.getPos = self.body.getPos
        self.setPos = self.body.setPos
        self.setHpr = self.body.setHpr
        self.getHpr = self.body.getHpr
        self.get_cam_pos = self.body.getPos

    def update(self, dt):
        self.body.setPos(self.body.getPos() + self.body.getQuat().xform(self.__move) * self.speed * dt)
        self.body.setH(self.body.getH() + self.__yaw * dt)

        pitch = self.body.getP() + self.__pitch * dt
        if pitch > 90:
            pitch = 90
        elif pitch < -90:
            pitch = -90
        self.body.setP(pitch)

    def turn(self, omega):
        self.__yaw = omega

class Character:
    name = 'Buster'
    height = 1.75
    crouch_height = 1.3
    step_height = 0.3
    radius = 0.4
    speed = 5.5
    jump_height = 1.5


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
        print('ability1', start)

    def ability2(self, start):
        print('ability2', start)

    def ability3(self):
        print('ultimate start')

    def fire1(self):
        print('primary fired')

    def fire2(self):
        print('secondary fired')
