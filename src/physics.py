import pygame
import Box2D
from Box2D import b2World, b2PolygonShape, b2CircleShape, b2_staticBody, b2_dynamicBody
import numpy as np


class PhysicsWorld:
    def __init__(self, gravity=(0, 9.8), pixels_per_meter=100, time_step=1 / 60.0, velocity_iterations=6,
                 position_iterations=2):
        # 创建 Box2D 世界
        self.world = b2World(gravity=gravity)
        self.PPM = pixels_per_meter
        self.time_step = time_step
        self.velocity_iterations = velocity_iterations
        self.position_iterations = position_iterations
        self.bodies = {}
        self.rotation_center = None

    def create_ball(self, position, radius, density=1.0, friction=0.1, restitution=0.3):
        """创建球体物理实体"""
        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        radius_m = radius / self.PPM

        # 创建动态物体定义
        body_def = Box2D.b2BodyDef()
        body_def.type = b2_dynamicBody
        body_def.position = position_m
        body_def.allowSleep = False

        # 创建物体
        body = self.world.CreateBody(body_def)

        # 创建圆形夹具
        shape = b2CircleShape(radius=radius_m)
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            density=density,
            friction=friction,
            restitution=restitution
        )
        body.CreateFixture(fixture_def)

        # 存储物体信息
        self.bodies[id(body)] = {
            'type': 'ball',
            'radius': radius,
            'body': body
        }
        return body

    def create_static_box(self, position, size):
        """创建静态矩形障碍物"""
        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        half_width = size[0] / (2 * self.PPM)
        half_height = size[1] / (2 * self.PPM)

        # 创建静态物体定义
        body_def = Box2D.b2BodyDef()
        body_def.type = b2_staticBody
        body_def.position = position_m

        # 创建物体
        body = self.world.CreateBody(body_def)

        # 创建多边形夹具
        shape = b2PolygonShape(box=(half_width, half_height))
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            friction=0.4,
            restitution=0.1
        )
        body.CreateFixture(fixture_def)

        # 存储物体信息
        self.bodies[id(body)] = {
            'type': 'wall',
            'size': size,
            'body': body
        }
        return body

    def create_static_circle(self, position, radius):
        """创建静态圆形障碍物"""
        position_m = (position[0] / self.PPM, position[1] / self.PPM)
        radius_m = radius / self.PPM

        # 创建静态物体定义
        body_def = Box2D.b2BodyDef()
        body_def.type = b2_staticBody
        body_def.position = position_m

        # 创建物体
        body = self.world.CreateBody(body_def)

        # 创建圆形夹具
        shape = b2CircleShape(radius=radius_m)
        fixture_def = Box2D.b2FixtureDef(
            shape=shape,
            friction=0.3,
            restitution=0.1
        )
        body.CreateFixture(fixture_def)

        # 存储物体信息
        self.bodies[id(body)] = {
            'type': 'obstacle',
            'radius': radius,
            'body': body
        }
        return body

    def set_rotation_center(self, center):
        """设置旋转中心点"""
        self.rotation_center = center

    def rotate_world(self, angle):
        """旋转物理世界"""
        if self.rotation_center:
            center_m = (self.rotation_center[0] / self.PPM,
                        self.rotation_center[1] / self.PPM)

            self.world.gravity = (0, 9.8)

            # 旋转所有动态物体
            for body_id, data in self.bodies.items():
                if data['type'] == 'ball':
                    body = data['body']
                    body.angle += angle
                    # 计算相对于旋转中心的位置
                    pos = body.position
                    rel_x = pos[0] - center_m[0]
                    rel_y = pos[1] - center_m[1]

                    # 应用旋转
                    new_x = rel_x * np.cos(angle) - rel_y * np.sin(angle)
                    new_y = rel_x * np.sin(angle) + rel_y * np.cos(angle)

                    # 更新位置
                    new_pos = (center_m[0] + new_x, center_m[1] + new_y)
                    body.position = new_pos

                    # 更新速度
                    vel_x, vel_y = body.linearVelocity
                    new_vel_x = vel_x * np.cos(angle) - vel_y * np.sin(angle)
                    new_vel_y = vel_x * np.sin(angle) + vel_y * np.cos(angle)
                    body.linearVelocity = (new_vel_x, new_vel_y)

    def step(self):
        """推进物理世界"""
        self.world.Step(
            self.time_step,
            self.velocity_iterations,
            self.position_iterations
        )
        self.world.ClearForces()


    def get_body_position(self, body):
        """获取物理实体的位置（像素单位）"""
        pos_m = body.position
        return (pos_m[0] * self.PPM, pos_m[1] * self.PPM)

    def get_body_velocity(self, body):
        """获取物理实体的速度（像素单位）"""
        vel_m = body.linearVelocity
        return (vel_m[0] * self.PPM, vel_m[1] * self.PPM)

    def get_body_angle(self, body):
        """获取物理实体的旋转角度"""
        return body.angle

    def apply_force_to_ball(self, body, force):
        """对球体施加力"""
        force_m = (force[0] / self.PPM, force[1] / self.PPM)
        body.ApplyForce(force_m, body.position, True)

    def set_ball_velocity(self, body, velocity):
        """直接设置球体速度"""
        velocity_m = (velocity[0] / self.PPM, velocity[1] / self.PPM)
        body.linearVelocity = velocity_m