import os
import pygame
from math import sin, radians, degrees, radians, copysign, atan2, pi, hypot
from pygame.math import Vector2

class Satellite:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x,y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle                                # angle is respect to the plane
        self.length = length                              # this is length of the satellite. Used for rotation
        self.max_acceleration = max_acceleration          #
        self.max_steering = max_steering                  # this is limit to how much the wheels can
        self.max_velocity = 20
        self.brake_deceleration = 10
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0
        self.max_angular_velocity = 1.0
        self.angular_velocity = 0.0

    def update_velocity(self):
        return
    def update_rotation(self):
        return

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        # send velocity delta (x,y)
        # send rotation degrees or radians
        # this goes to pierre navigation portion

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

    def generate_commands(self, dt, target_position):
        move_command_list = ["right", "left", "forward", "back"]

        commands = dict.fromkeys(move_command_list, 0)
        min_dist = 1

        rel_x, rel_y = target_position.x - self.position.x, target_position.y - self.position.y
        rel_angle = (180 / pi) * -atan2(rel_y, rel_x)
        rel_dist = hypot(rel_x, rel_y)
        ang_dif = abs(abs(rel_angle) - abs(self.angle))

        if dt != 0:
            required_angle_velocity = radians(ang_dif / dt)
        else:
            required_angle_velocity = 0

        print("required angle velocity", required_angle_velocity)
        print("ang_dif", ang_dif)
        print("rel_angle", rel_angle)
        print("self.angle", self.angle)

        if self.angle > rel_angle:
            commands["right"] = min(self.max_angular_velocity, required_angle_velocity)
        elif self.angle < rel_angle:
            commands["left"] = max(-self.max_angular_velocity, -required_angle_velocity)
        else:                                               # Moving forward only get's called if the angle is set.
            if rel_dist > min_dist:
                commands["forward"] = self.max_velocity

        print(commands, '\n')
        return commands

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("CubeSat Simulator")
        width = 720
        height = 720
        self.window = (width, height)
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "car.png")
        car_image = pygame.image.load(image_path)
        cubesat = Satellite(0, 0)
        target = Satellite(10, 20)
        ppu = 32

        while not self.exit:
            dt = self.clock.get_time() / 1000

            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            manual_move = False

            if not manual_move:
                command = cubesat.generate_commands(dt, target.position)

                if "forward" in command.keys():
                    if cubesat.velocity.x < 0:
                        cubesat.acceleration = cubesat.brake_deceleration
                    else:
                        cubesat.acceleration += 1* dt
                if "right" in command.keys():
                    cubesat.steering -= 30 * dt
                elif "left" in command.keys():
                    cubesat.steering += 30 * dt

            if manual_move:
                # User input
                pressed = pygame.key.get_pressed()

                if pressed[pygame.K_UP]:
                    if cubesat.velocity.x < 0:
                        cubesat.acceleration = cubesat.brake_deceleration
                    else:
                        cubesat.acceleration += 1 * dt
                elif pressed[pygame.K_DOWN]:
                    if cubesat.velocity.x > 0:
                        cubesat.acceleration = -cubesat.brake_deceleration
                    else:
                        cubesat.acceleration -= 1 * dt
                elif pressed[pygame.K_SPACE]:
                    if abs(cubesat.velocity.x) > dt * cubesat.brake_deceleration:
                        cubesat.acceleration = -copysign(cubesat.brake_deceleration, cubesat.velocity.x)
                    else:
                        cubesat.acceleration = -cubesat.velocity.x / dt
                else:
                    if abs(cubesat.velocity.x) > dt * cubesat.free_deceleration:
                        cubesat.acceleration = -copysign(cubesat.free_deceleration, cubesat.velocity.x)
                    else:
                        if dt != 0:
                            cubesat.acceleration = -cubesat.velocity.x / dt
                cubesat.acceleration = max(-cubesat.max_acceleration, min(cubesat.acceleration, cubesat.max_acceleration))

                if pressed[pygame.K_RIGHT]:
                    cubesat.steering -= 30 * dt
                elif pressed[pygame.K_LEFT]:
                    cubesat.steering += 30 * dt
                else:
                    cubesat.steering = 0
                cubesat.steering = max(-cubesat.max_steering, min(cubesat.steering, cubesat.max_steering))

            # Logic
            cubesat.update(dt)

            # rel_x, rel_y = target.position.x - cubesat.position.x, target.position.y - cubesat.position.y
            # rel_angle = (180 / pi) * -atan2(rel_y, rel_x)
            # print("rel_angle", rel_angle)
            # print("cubesat angle", cubesat.angle)

            # print("relative distance:", hypot(rel_x, rel_y))
            # Drawing
            self.screen.fill((0, 0, 0))

            # Draws a car which will represent the target
            targeted = pygame.transform.rotate(car_image, target.angle)
            rect = targeted.get_rect()
            self.screen.blit(targeted, target.position * ppu - (rect.width/2, rect.height/2))

            # Draws the car(which will represent cube satellite for now)
            rotated = pygame.transform.rotate(car_image, cubesat.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, cubesat.position * ppu - (rect.width / 2, rect.height / 2))

            pygame.display.flip()

            # Drawing target

            

            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
