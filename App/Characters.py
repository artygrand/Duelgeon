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

    def pitch(self, omega):
        self.__pitch = omega

    def move(self, vector):
        self.__move = vector


class Character:
    def __init__(self, world, parent, hero):
        self.hero = hero
        self.name = hero.get('name')
        self.speed = hero.get('speed')
        self.height = hero.get('height')

        self.body = CharacterController(world, parent, self.height, hero.get('crouch_height'), .3, hero.get('width') / 2)

        self.__move = Vec3(0)
        self.__y_omega = 0
        self.__p_omega = 0
        self.__pitch = 0

        self.getPos = self.body.node.getPos
        self.setPos = self.body.node.setPos
        self.getH = self.body.node.getH

    def update(self, dt):
        self.body.update(dt, self.__move * self.speed, self.__y_omega)

        pitch = self.__pitch + self.__p_omega * dt
        if pitch > 90:
            pitch = 90
        elif pitch < -90:
            pitch = -90
        self.__pitch = pitch

    def getHpr(self):
        # pitch = self.body.node.getNetTransform().getMat().getRow3(0)
        # pitch = pitch.x * self.__pitch + pitch.y * self.__pitch + pitch.z * self.__pitch
        return Vec3(self.body.node.getH(), self.__pitch, self.body.node.getR())

    def getP(self):
        return self.__pitch

    def setHpr(self, hpr):
        self.body.node.setH(hpr[0])
        self.__pitch = hpr[1]

    def get_cam_pos(self):
        return self.body.node.getPos() + self.body.node.getQuat(render).xform(Vec3(0, 0, self.height - .15))

    def move(self, vector):
        if vector.getY() > 0:
            vector.setY(vector.getY() * 1.5)
        self.__move = vector

    def stop(self):
        self.__move = Vec3(0)

    def pitch(self, omega):
        self.__p_omega = omega

    def turn(self, omega):
        self.__y_omega = omega

    def jump(self):
        self.body.jump(self.hero.get('jump_height'), limit=self.hero.jumps_limit, on_stop=self.hero.reset_jumps_limit)

    def crouch(self, start):
        self.body.crouch(start)

    def fly(self, start):
        self.body.float() if start else self.body.fall()

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
