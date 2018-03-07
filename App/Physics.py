#!/usr/bin/env python3

import math

from panda3d.core import NodePath, Vec3, Point3, BitMask32, TransformState
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletCapsuleShape, BulletGhostNode, ZUp, BulletRigidBodyNode
from direct.showbase.DirectObject import DirectObject

from App.Events import Events


class World(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)

        self.node = NodePath('World')
        self.debug_node = self.node.attachNewNode(BulletDebugNode('Debug'))

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debug_node.node())

        self.accept('f1', self.debug)

    def update(self, dt):
        self.world.doPhysics(dt)

    def debug(self):
        if self.debug_node.isHidden():
            self.debug_node.show()
            base.setFrameRateMeter(True)
        else:
            self.debug_node.hide()
            base.setFrameRateMeter(False)


class KCC:
    """Kinematic character controller
    KCC(world, parent, hero.for_kcc())
    """

    max_fall_speed = 55.0  # Terminal velocity of a sky diver in m/s
    up = Vec3(0, 0, 1)

    step_offset = .3
    skin_width = 0.04
    min_slope_dot = .64  # 50 deg

    def __init__(self, world, parent, params):
        self.params = params
        self.__world = world
        self.__g = world.getGravity().z  # negative value
        self.__events = Events()

        self.__shape_stand = BulletCapsuleShape(params['radius'], params['height'] - 2 * params['radius'], ZUp)
        self.__shape_crouch = BulletCapsuleShape(params['radius'], params['crouch_height'] - 2 * params['radius'], ZUp)
        self.__ghost = BulletGhostNode('Capsule for ' + params['name'])
        self.__ghost.addShape(self.__shape_stand, TransformState.makePos((0, 0, params['height'] / 2)))
        self.node = parent.attachNewNode(self.__ghost)
        self.node.setCollideMask(BitMask32.allOn())
        world.attachGhost(self.__ghost)

        self.__foot_contact = self.__head_contact = None
        self.velocity = Vec3()
        self.__outer_motion = Vec3()
        self.__motion_time_ival = 0
        self.__ignore_player_motion = False
        self.__outer_rotation = self.__rotation_time_ival = 0
        self.__ignore_player_rotation = False

        self.__falling = False
        self.__crouches = False
        # controls
        self.__want_crouch = False
        self.__want_fly = False

    def update(self, dt, move=Vec3(), turn=0):
        old_foot = {'len': 11} if self.__foot_contact is None else self.__foot_contact

        self.__update_contacts()

        print(self.on_ground(), self.node.getPos(),
              self.__foot_contact['len'] if self.__foot_contact is not None else 'None')

        can_fall = True
        if self.__foot_contact is None:
            if old_foot is not None:
                can_fall = False
        elif self.velocity.z < 0 and old_foot['len'] < self.__foot_contact['len']:
            can_fall = False

        if not can_fall and 'pos' in old_foot:
            print('->', old_foot['pos'])
            self.node.setPos(old_foot['pos'])
            old_foot['len'] = 0
            self.__foot_contact = old_foot
            # TODO fix fall on volcano

        motion = self.__compute_motion(move, dt)
        # TODO add jump and gravity to motion

        self.__apply_gravity(dt)

        penetrated, pos = self.__fix_collisions(self.node.getPos(), motion)
        # TODO remove penetrated?

        self.node.setPos(pos + motion + self.node.getQuat(render).xform(self.velocity * dt))
        self.node.setH(self.node, self.__compute_rotation(turn, dt))

    def __update_contacts(self):
        def find_closest(f, t):
            result = self.__world.rayTestAll(f, t)

            if not result.hasHits():
                return None

            sorted_hits = sorted(result.getHits(), key=lambda h: (f - h.getHitPos()).length())

            for hit in sorted_hits:
                if type(hit.getNode()) is not BulletGhostNode:
                    return {'pos': hit.getHitPos(), 'node': hit.getNode(), 'normal': hit.getHitNormal(),
                            'len': (f - hit.getHitPos()).length()}

        foot = self.node.getPos(render)
        head = foot + self.node.getQuat(render).xform(Point3(0, 0, self.params['height']))
        dist = self.node.getQuat(render).xform(self.up * 1)
        self.__foot_contact = find_closest(foot, foot - dist)
        self.__head_contact = find_closest(head, head + dist)

    def move(self, vec, time_interval=0, forced=None):
        """Add linear velocity to body from outer source
        If forced is True, player will not be able to control the body until he is released or interval is ended
        If time_interval is provided, velocity will be affected only during this period
        :param Vec3 vec:
        :param Float time_interval: in seconds
        :param Bool forced:
        """
        self.velocity = Vec3()
        self.__outer_motion = vec
        self.__motion_time_ival = time_interval
        if forced is not None:
            self.__ignore_player_motion = forced

    def release_motion(self):
        self.__ignore_player_motion = False

    def __compute_motion(self, move, dt):
        total = self.__outer_motion * dt
        if not self.__ignore_player_motion:
            total += self.node.getQuat(render).xform(move) * dt

        if self.__motion_time_ival > 0:
            self.__motion_time_ival -= dt
            if self.__motion_time_ival <= 0:
                self.__outer_motion = 0
                self.__ignore_player_motion = False

        return total

    def rotate(self, omega, time_interval=0, forced=None):
        """Add angular velocity to body from outer source
        If forced is True, player will not be able to control the body until he is released or interval is ended
        If time_interval is provided, velocity will be affected only during this period
        :param Int omega:
        :param Float time_interval: in seconds
        :param Bool forced:
        """
        self.__outer_rotation = omega
        self.__rotation_time_ival = time_interval
        if forced is not None:
            self.__ignore_player_rotation = forced

    def release_rotation(self):
        self.__ignore_player_rotation = False

    def __compute_rotation(self, turn, dt):
        total = self.__outer_rotation
        if not self.__ignore_player_rotation:
            yaw = self.node.getNetTransform().getMat().getRow3(2)
            turn = yaw.x * turn + yaw.y * turn + yaw.z * turn
            total += turn

        if self.__rotation_time_ival > 0:
            self.__rotation_time_ival -= dt
            if self.__rotation_time_ival <= 0:
                self.__outer_rotation = 0
                self.__ignore_player_rotation = False

        return total * dt

    def __fix_collisions(self, pos, motion):
        penetrated = False

        for m in self.__world.getManifolds():
            if not (m.getNumManifoldPoints() and self.__ghost in [m.getNode0(), m.getNode1()]):  # not with me
                continue

            if m.getNode0() == self.__ghost:
                he = m.getNode1()
                sign = 1
            else:
                he = m.getNode0()
                sign = -1

            if type(he) is BulletGhostNode:  # ignore other ghosts
                continue

            mass = he.getMass()

            reflection = False
            if mass != 0 and self.params['mass'] > mass:
                reflection = self.compute_reflection_vector(motion * (self.params['mass'] - mass), motion.normalized())
                reflection.z = 0

            for point in m.getManifoldPoints():
                dist = point.getDistance()
                if dist < 0:
                    penetrated = True
                    pos -= point.getNormalWorldOnB() * dist * sign
                    # normal = point.getNormalWorldOnB() * sign  # TODO need?
                    if reflection:
                        he.setActive(True)
                        he.applyCentralForce(-reflection)  # , point.getLocalPointA()

        return penetrated, pos

    def __apply_gravity(self, dt):
        if self.velocity.z <= 0 and self.on_ground():
            self.velocity.z = 0
        else:
            self.velocity.z += self.__g * dt
            if self.velocity.z < -self.max_fall_speed:
                self.velocity.z = -self.max_fall_speed

    def on_ground(self):
        return self.__foot_contact is not None and self.__foot_contact['len'] <= .01

    @staticmethod
    def compute_reflection_vector(direction, normal):
        return direction - normal * direction.dot(normal) * 2

    def set_max_slope(self, deg):
        """Limits the body to only climb slopes that are less steep than the this value
        :param Int deg: in degrees
        """
        self.min_slope_dot = round(math.cos(math.radians(deg)), 2)

    def set_gravity(self, val=None):
        """Gravity for this body
        :param Float val:
        """
        self.__g = self.__world.getGravity().z if val is None else val

    def jump(self, power=3, vec=Vec3(0, 0, 1), limit=1, on_stop=None):
        """Apply impulse to body with provided power
        If vec is provided, body jumps not to top
        :param Float power:
        :param Vec3 vec:
        :param Int limit: how many hero can jump
        :param Callable on_stop: this will be called once body grounded
        """
        if self.__falling:
            limit -= 1
        if limit < 1:
            return

        self.velocity += vec * power

        if on_stop is not None:
            self.__events.once('grounded', on_stop)

    def crouch(self, start=True, on_stop=None):
        self.__want_crouch = start

        if not start:
            return

        self.__crouches = True

        if on_stop is not None:
            self.__events.once('stand_up', on_stop)
        # TODO duck

    def float(self):
        """Ignore gravity"""
        self.__want_fly = True

    def fall(self):
        """Gravity will affect"""
        self.__want_fly = False
