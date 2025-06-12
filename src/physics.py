import pygame
import Box2D
from Box2D import b2World, b2PolygonShape, b2CircleShape, b2_staticBody, b2_dynamicBody
import numpy as np


class PhysicsWorld:
    def __init__(self, gravity=(0, 9.8), pixels_per_meter=100, time_step=1 / 60.0, velocity_iterations=6,
                 position_iterations=2):

        self.world = b2World(gravity=gravity)
        self.PPM = pixels_per_meter
        self.time_step = time_step
        self.velocity_iterations = velocity_iterations
        self.position_iterations = position_iterations
        self.bodies = {}
        self.rotation_center = None

    def set_gravity(self, gravity):

        self.world.gravity = gravity

    def create_ball(self, position, radius, density=1.0, friction=0.1, restitution=0.1):

        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        radius_m = radius / self.PPM


        body_def = Box2D.b2BodyDef()
        body_def.type = b2_dynamicBody
        body_def.position = position_m
        body_def.allowSleep = False


        body = self.world.CreateBody(body_def)

        shape = b2CircleShape(radius=radius_m)
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            density=density,
            friction=friction,
            restitution=restitution
        )
        body.CreateFixture(fixture_def)

        self.bodies[id(body)] = {
            'type': 'ball',
            'radius': radius,
            'body': body
        }
        return body

    def create_static_box(self, position, size):

        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        half_width = size[0] / (2 * self.PPM)
        half_height = size[1] / (2 * self.PPM)


        body_def = Box2D.b2BodyDef()
        body_def.type = b2_staticBody
        body_def.position = position_m

        body = self.world.CreateBody(body_def)


        shape = b2PolygonShape(box=(half_width, half_height))
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            friction=0.4,
            restitution=0.1
        )
        body.CreateFixture(fixture_def)

        self.bodies[id(body)] = {
            'type': 'wall',
            'size': size,
            'body': body
        }
        return body

    def create_static_circle(self, position, radius):

        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        radius_m = radius / self.PPM


        body_def = Box2D.b2BodyDef()
        body_def.type = b2_staticBody
        body_def.position = position_m


        body = self.world.CreateBody(body_def)


        shape = b2CircleShape(radius=radius_m)
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            friction=0.3,
            restitution=0.1
        )
        body.CreateFixture(fixture_def)


        self.bodies[id(body)] = {
            'type': 'obstacle',
            'radius': radius,
            'body': body
        }
        return body

    def create_guard(self, position, radius):

        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        radius_m = radius / self.PPM


        body_def = Box2D.b2BodyDef()
        body_def.type = b2_staticBody
        body_def.position = position_m


        body = self.world.CreateBody(body_def)


        shape = b2CircleShape(radius=radius_m)
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            friction=0.3,
            restitution=0.1
        )
        body.CreateFixture(fixture_def)


        self.bodies[id(body)] = {
            'type': 'guard',
            'radius': radius,
            'body': body
        }
        return body

    def remove_body(self, body):

        if body and id(body) in self.bodies:
            self.world.DestroyBody(body)
            del self.bodies[id(body)]

    def set_rotation_center(self, center):

        self.rotation_center = center

    def rotate_world(self, angle):

        if self.rotation_center:
            center_m = (self.rotation_center[0] / self.PPM,
                        self.rotation_center[1] / self.PPM)

            self.world.gravity = (0, 9.8)


            for body_id, data in self.bodies.items():
                if data['type'] == 'ball':
                    body = data['body']
                    body.angle += angle

                    pos = body.position
                    rel_x = pos[0] - center_m[0]
                    rel_y = pos[1] - center_m[1]


                    new_x = rel_x * np.cos(angle) - rel_y * np.sin(angle)
                    new_y = rel_x * np.sin(angle) + rel_y * np.cos(angle)

                    new_pos = (center_m[0] + new_x, center_m[1] + new_y)
                    body.position = new_pos


                    vel_x, vel_y = body.linearVelocity
                    new_vel_x = vel_x * np.cos(angle) - vel_y * np.sin(angle)
                    new_vel_y = vel_x * np.sin(angle) + vel_y * np.cos(angle)
                    body.linearVelocity = (new_vel_x, new_vel_y)

    def step(self):

        self.world.Step(
            self.time_step,
            self.velocity_iterations,
            self.position_iterations
        )
        self.world.ClearForces()

    def get_body_position(self, body):

        pos_m = body.position
        return (pos_m[0] * self.PPM, pos_m[1] * self.PPM)

    def get_body_velocity(self, body):

        vel_m = body.linearVelocity
        return (vel_m[0] * self.PPM, vel_m[1] * self.PPM)

    def get_body_angle(self, body):

        return body.angle

    def apply_force_to_ball(self, body, force):

        force_m = (force[0] / self.PPM, force[1] / self.PPM)
        body.ApplyForce(force_m, body.position, True)

    def set_ball_velocity(self, body, velocity):
        velocity_m = (velocity[0] / self.PPM, velocity[1] / self.PPM)
        body.linearVelocity = velocity_m