#!/usr/bin/env python3

"""Kinetic Character Controller

Based on panda3d-bullet-kcc for python 2.x
see https://github.com/peterpodgorski/panda3d-bullet-kcc
"""

from panda3d.core import Vec3, Point3, Quat, BitMask32
from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, BulletGhostNode

import math


class CharacterController:
    def __init__(self, world, parent, walk_height, crouch_height, step_height, radius, gravity=None):

        self.capsule, self.capsule_node, self.__capsule_h, self.__levitation = None, None, None, None
        self.__capsule_r, self.__h, self.__capsule_offset, self.__foot_distance = None, None, None, None

        self.__world = world
        self.__parent = parent
        self.__time_step = 0
        self.__current_pos = Vec3(0, 0, 0)

        self.movement_parent = self.__parent.attachNewNode("Movement Parent")
        self.__setup(walk_height, crouch_height, step_height, radius)
        self.__map_methods()

        self.gravity = self.__world.getGravity().z if gravity is None else gravity
        self.set_max_slope(50.0, True)
        self.set_active_jump_limiter(True)

        self.movement_state = "ground"
        self.movementStateFilter = {
            "ground": ["ground", "jumping", "falling"],
            "jumping": ["ground", "falling"],
            "falling": ["ground"],
            "flying": [],
        }

        # Prevent the KCC from moving when there's not enough room for it in the next frame
        # It doesn't work right now because I can't figure out how to add sliding. Sweep test could work,
        # but it would cause problems with penetration testing and steps
        # That said, you probably won't need it, if you design your levels correctly
        self.predict_future_space = False
        self.future_space_prediction_distance = 10.0

        self.isCrouching = False

        self.__fall_time = 0.0
        self.__fall_start_pos = self.__current_pos.z
        self.__linear_velocity = Vec3(0, 0, 0)
        self.__head_contact = None
        self.__foot_contact = None
        self.__enabled_crouch = False

        self.__stand_up_callback = [None, [], {}]
        self.__fall_callback = [None, [], {}]

    def setCollideMask(self, *args):
        self.__walk_capsule_node.setCollideMask(*args)
        self.__crouch_capsule_node.setCollideMask(*args)

    def set_fall_callback(self, method, *args, **kwargs):
        """Callback called when the character falls on the ground.
        The position where falling started is passed as the first argument, the additional argument and keyword
        arguments follow.
        """
        self.__fall_callback = [method, args, kwargs]

    def set_stand_up_callback(self, method, *args, **kwargs):
        """Callback called when the character stands up from crouch.
        This is needed because standing up might be prevented by spacial awareness.
        """
        self.__stand_up_callback = [method, args, kwargs]

    def set_max_slope(self, degrees, affect_speed):
        """
        degrees -- (float) maximum slope in degrees. 0, False or None means don't limit slope.
        affectSpeed -- (bool) if True, the character will walk slower up slopes
        
        Both options are independent.
        
        By default, affectSpeed is enabled and maximum slope is 50 deg.
        """
        if not degrees:
            self.min_slope_dot = None

            return

        self.min_slope_dot = round(math.cos(math.radians(degrees)), 2)

        self.__slope_affects_speed = affect_speed

    def set_active_jump_limiter(self, val):
        """
        Enable or disable the active jump limiter, which is the mechanism that changes the maximum jump height based
        on the space available above the character's head.
        """
        self.__intelligent_jump = val

    def start_crouch(self):
        if self.isCrouching:
            return
        self.isCrouching = True
        self.__enabled_crouch = True

        self.capsule = self.__crouch_capsule
        self.capsule_node = self.__crouch_capsule_node

        self.__capsule_h = self.__crouch_capsule_h
        self.__levitation = self.__crouch_levitation
        self.__capsule_r = self.__crouch_capsule_r
        self.__h = self.__crouch_h

        self.__world.removeRigidBody(self.__walk_capsule_node.node())
        self.__world.attachRigidBody(self.__crouch_capsule_node.node())

        self.__capsule_offset = self.__capsule_h * 0.5 + self.__levitation
        self.__foot_distance = self.__capsule_offset + self.__levitation

    def stop_crouch(self):
        """
        Note that spacial awareness may prevent the character from standing up immediately, which is what
        you usually want. Use stand up callback to know when the character stands up.
        """
        self.__enabled_crouch = False

    def is_on_ground(self):
        """
        Check if the character is on ground. You may also check if the movement_state variable is set to 'ground'
        """
        if self.__foot_contact is None:
            return False
        elif self.movement_state == "ground":
            elevation = self.__current_pos.z - self.__foot_contact[0].z
            return elevation <= self.__levitation + 0.02
        else:
            return self.__current_pos <= self.__foot_contact[0]

    def start_jump(self, max_height=3.0):
        """
        max height is 3.0 by default. Probably too much for most uses.
        """
        self.__jump(max_height)

    def start_fly(self):
        self.movement_state = 'flying'

    def stop_fly(self):
        """
        Stop flying and start falling
        """
        self.__fall()

    def set_angular_movement(self, omega):
        self.movement_parent.setH(self.movement_parent, omega * self.__time_step)

    def set_linear_movement(self, speed):
        self.__linear_velocity = speed

    def update(self):
        """
        Update method. Call this around doPhysics.
        """
        process_states = {
            "ground": self.__process_ground,
            "jumping": self.__process_jumping,
            "falling": self.__process_falling,
            "flying": self.__process_flying,
        }

        self.__time_step = globalClock.getDt()

        self.__update_foot_contact()
        self.__update_head_contact()

        process_states[self.movement_state]()

        self.__apply_linear_velocity()
        self.__prevent_penetration()

        self.__update_capsule()

        if self.isCrouching and not self.__enabled_crouch:
            self.__stand_up()

    def __land(self):
        self.movement_state = "ground"

    def __fall(self):
        self.movement_state = "falling"

        self.__fall_start_pos = self.__current_pos.z
        self.fall_delta = 0.0
        self.__fall_time = 0.0

    def __jump(self, max_z=3.0):
        if "jumping" not in self.movementStateFilter[self.movement_state]:
            return

        max_z += self.__current_pos.z

        if self.__intelligent_jump and self.__head_contact is not None and self.__head_contact[0].z < max_z + self.__h:
            max_z = self.__head_contact[0].z - self.__h * 1.2

        max_z = round(max_z, 2)

        self.jump_start_pos = self.__current_pos.z
        self.jump_time = 0.0

        bsq = -4.0 * self.gravity * (max_z - self.jump_start_pos)
        try:
            b = math.sqrt(bsq)
        except:
            return
        self.jump_speed = b
        self.jump_max_height = max_z

        self.movement_state = "jumping"

    def __stand_up(self):
        self.__update_head_contact()

        if self.__head_contact is not None\
                and self.__current_pos.z + self.__walk_levitation + self.__walk_capsule_h >= self.__head_contact[0].z:
            return

        self.isCrouching = False

        self.capsule = self.__walk_capsule
        self.capsule_node = self.__walk_capsule_node

        self.__capsule_h = self.__walk_capsule_h
        self.__levitation = self.__walk_levitation
        self.__capsule_r = self.__walk_capsule_r
        self.__h = self.__walk_h

        self.__world.removeRigidBody(self.__crouch_capsule_node.node())
        self.__world.attachRigidBody(self.__walk_capsule_node.node())

        self.__capsule_offset = self.__capsule_h * 0.5 + self.__levitation
        self.__foot_distance = self.__capsule_offset + self.__levitation

        if self.__stand_up_callback[0] is not None:
            self.__stand_up_callback[0](*self.__stand_up_callback[1], **self.__stand_up_callback[2])

    def __process_ground(self):
        if not self.is_on_ground():
            self.__fall()
        else:
            self.__current_pos.z = self.__foot_contact[0].z

    def __process_falling(self):
        self.__fall_time += self.__time_step
        self.fall_delta = self.gravity * self.__fall_time ** 2

        new_pos = Vec3(self.__current_pos)
        new_pos.z = self.__fall_start_pos + self.fall_delta

        self.__current_pos = new_pos

        if self.is_on_ground():
            self.__land()
            if self.__fall_callback[0] is not None:
                self.__fall_callback[0](self.__fall_start_pos, *self.__fall_callback[1], **self.__fall_callback[2])

    def __process_jumping(self):
        if self.__head_contact is not None and self.__capsuleTop >= self.__head_contact[0].z:
            self.__fall()
            return

        old_pos = float(self.__current_pos.z)

        self.jump_time += self.__time_step

        self.__current_pos.z = self.gravity * self.jump_time ** 2\
            + self.jump_speed * self.jump_time + self.jump_start_pos

        if round(self.__current_pos.z, 2) >= self.jump_max_height:
            self.__fall()

    def __process_flying(self):
        if self.__foot_contact and self.__current_pos.z - 0.1 < self.__foot_contact[0].z\
                and self.__linear_velocity.z < 0.0:
            self.__current_pos.z = self.__foot_contact[0].z
            self.__linear_velocity.z = 0.0

        if self.__head_contact and self.__capsuleTop >= self.__head_contact[0].z and self.__linear_velocity.z > 0.0:
            self.__linear_velocity.z = 0.0

    def __check_future_space(self, global_vel):
        global_vel = global_vel * self.future_space_prediction_distance

        p_from = Point3(self.capsule_node.getPos(render) + global_vel)
        p_up = Point3(p_from + Point3(0, 0, self.__capsule_h * 2.0))
        p_down = Point3(p_from - Point3(0, 0, self.__capsule_h * 2.0 + self.__levitation))

        up_test = self.__world.rayTestClosest(p_from, p_up)
        down_test = self.__world.rayTestClosest(p_from, p_down)

        if not (up_test.hasHit() and down_test.hasHit()):
            return True

        up_node = up_test.getNode()
        if up_node.getMass():
            return True

        space = abs(up_test.getHitPos().z - down_test.getHitPos().z)

        if space < self.__levitation + self.__capsule_h + self.capsule.getRadius():
            return False

        return True

    def __update_foot_contact(self):
        p_from = Point3(self.capsule_node.getPos(render))
        p_to = Point3(p_from - Point3(0, 0, self.__foot_distance))
        result = self.__world.rayTestAll(p_from, p_to)

        if not result.hasHits():
            self.__foot_contact = None
            return

        sorted_hits = sorted(result.getHits(), key=lambda h: (p_from - h.getHitPos()).length())

        for hit in sorted_hits:
            if type(hit.getNode()) is BulletGhostNode:
                continue

            self.__foot_contact = [hit.getHitPos(), hit.getNode(), hit.getHitNormal()]
            break

    def __update_head_contact(self):
        p_from = Point3(self.capsule_node.getPos(render))
        p_to = Point3(p_from + Point3(0, 0, self.__capsule_h * 20.0))
        result = self.__world.rayTestAll(p_from, p_to)

        if not result.hasHits():
            self.__head_contact = None
            return

        sorted_hits = sorted(result.getHits(), key=lambda h: (p_from - h.getHitPos()).length())

        for hit in sorted_hits:
            if type(hit.getNode()) is BulletGhostNode:
                continue

            self.__head_contact = [hit.getHitPos(), hit.getNode()]
            break

    def __update_capsule(self):
        self.movement_parent.setPos(self.__current_pos)
        self.capsule_node.setPos(0, 0, self.__capsule_offset)

        self.__capsuleTop = self.__current_pos.z + self.__levitation + self.__capsule_h * 2.0

    def __apply_linear_velocity(self):
        global_vel = self.movement_parent.getQuat(render).xform(self.__linear_velocity) * self.__time_step

        if self.predict_future_space and not self.__check_future_space(global_vel):
            return

        if self.__foot_contact is not None and self.min_slope_dot and self.movement_state != "flying":
            normal_vel = Vec3(global_vel)
            normal_vel.normalize()

            floor_normal = self.__foot_contact[2]
            abs_slope_dot = round(floor_normal.dot(Vec3.up()), 2)

            def apply_gravity():
                self.__current_pos -= Vec3(floor_normal.x, floor_normal.y, 0.0) * self.gravity * self.__time_step * 0.1

            if abs_slope_dot <= self.min_slope_dot:
                apply_gravity()

                if global_vel != Vec3():
                    global_vel_dir = Vec3(global_vel)
                    global_vel_dir.normalize()

                    fn = Vec3(floor_normal.x, floor_normal.y, 0.0)
                    fn.normalize()

                    vel_dot = 1.0 - global_vel_dir.angleDeg(fn) / 180.0
                    if vel_dot < 0.5:
                        self.__current_pos -= Vec3(fn.x * global_vel.x, fn.y * global_vel.y, 0.0) * vel_dot

                    global_vel *= vel_dot

            elif self.__slope_affects_speed and global_vel != Vec3():
                apply_gravity()

        self.__current_pos += global_vel

    def __prevent_penetration(self):
        collisions = Vec3()

        for mf in self.__world.getManifolds():
            if not (mf.getNumManifoldPoints() and self.capsule_node.node() in [mf.getNode0(), mf.getNode1()]):
                continue

            sign = 1 if mf.getNode0() == self.capsule_node.node() else -1

            for m_point in mf.getManifoldPoints():
                direction = m_point.getPositionWorldOnB() - m_point.getPositionWorldOnA()
                normal = Vec3(direction)
                normal.normalize()

                if m_point.getDistance() < 0:
                    collisions -= direction * m_point.getDistance() * 2.0 * sign

        collisions.z = 0.0
        self.__current_pos += collisions

    def __map_methods(self):
        self.getHpr = self.movement_parent.getHpr
        self.getH = self.movement_parent.getH
        self.getP = self.movement_parent.getP
        self.getR = self.movement_parent.getR

        self.getPos = self.movement_parent.getPos
        self.getX = self.movement_parent.getX
        self.getY = self.movement_parent.getY
        self.getZ = self.movement_parent.getZ

        self.getQuat = self.movement_parent.getQuat

        self.setHpr = self.movement_parent.setHpr
        self.setH = self.movement_parent.setH
        self.setP = self.movement_parent.setP
        self.setR = self.movement_parent.setR

        self.setQuat = self.movement_parent.setQuat

    def setPos(self, *args):
        self.movement_parent.setPos(*args)
        self.__current_pos = self.movement_parent.getPos(render)

    def setX(self, *args):
        self.movement_parent.setX(*args)
        self.__current_x = self.movement_parent.getX(render)

    def setY(self, *args):
        self.movement_parent.setY(*args)
        self.__current_y = self.movement_parent.getY(render)

    def setZ(self, *args):
        self.movement_parent.setZ(*args)
        self.__current_z = self.movement_parent.getZ(render)

    def __setup(self, walk_h, crouch_h, step_h, radius):
        def set_data(full, step, r):
            if full - step <= r * 2.0:
                length = 0.1
                r = (full * 0.5) - (step * 0.5)
                lev = step + r
            else:
                length = full - step - r * 2.0
                lev = full - r - length / 2.0

            return length, lev, r

        self.__walk_h = walk_h
        self.__crouch_h = crouch_h

        self.__walk_capsule_h, self.__walk_levitation, self.__walk_capsule_r = set_data(walk_h, step_h, radius)
        self.__crouch_capsule_h, self.__crouch_levitation, self.__crouch_capsule_r = set_data(crouch_h, step_h, radius)

        self.__capsule_h = self.__walk_capsule_h
        self.__levitation = self.__walk_levitation
        self.__capsule_r = self.__walk_capsule_r
        self.__h = self.__walk_h

        self.__capsule_offset = self.__capsule_h * 0.5 + self.__levitation
        self.__foot_distance = self.__capsule_offset + self.__levitation

        self.__add_elements()

    def __add_elements(self):
        # Walk Capsule
        self.__walk_capsule = BulletCapsuleShape(self.__walk_capsule_r, self.__walk_capsule_h)

        self.__walk_capsule_node = self.movement_parent.attachNewNode(BulletRigidBodyNode('Capsule'))
        self.__walk_capsule_node.node().addShape(self.__walk_capsule)
        self.__walk_capsule_node.node().setKinematic(True)
        self.__walk_capsule_node.setCollideMask(BitMask32.allOn())

        self.__world.attachRigidBody(self.__walk_capsule_node.node())

        # Crouch Capsule
        self.__crouch_capsule = BulletCapsuleShape(self.__crouch_capsule_r, self.__crouch_capsule_h)

        self.__crouch_capsule_node = self.movement_parent.attachNewNode(BulletRigidBodyNode('crouchCapsule'))
        self.__crouch_capsule_node.node().addShape(self.__crouch_capsule)
        self.__crouch_capsule_node.node().setKinematic(True)
        self.__crouch_capsule_node.setCollideMask(BitMask32.allOn())

        # Set default
        self.capsule = self.__walk_capsule
        self.capsule_node = self.__walk_capsule_node
        self.capsule_node.node().setMass(7.0)

        # Init
        self.__update_capsule()
