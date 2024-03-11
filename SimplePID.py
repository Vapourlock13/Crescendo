def dirty_angle(angle):
    while angle < -180.0:
        angle += 360.0
    while angle > 180.0:
        angle -= 360.0
    return angle


class SimplePID:
    def __init__ (self,kP: float, kI: float, kD: float, tolerance: float, flip: bool = False) -> None:
        self.kP: float = kP
        self.kI: float = kI
        self.kD: float = kD
        self.tolerance: float = tolerance
        self.flip = flip

        self.last_error: float = 0.0
        self.integral: float = 0.0
        self.last_target: float = 0.0

    def get_speed (self, target: float, current_position: float) -> float:
        # If we are aiming to a new point, reset variables
        if not target == self.last_target:
            self.last_target = target
            self.integral = 0.0
            self.last_error = 0.0

        # Find Error
        error = dirty_angle(target - current_position)
        self.integral += error * .02
        derivative = (error - self.last_error) / .02

        # reset integral if within tolerance
        if -1.0 * self.tolerance <= error <= self.tolerance:
            self.integral = 0.0
            self.last_error = 0.0
            speed = 0.0

        else:
            # update persistent variables
            self.last_error = error
            speed = error * self.kP + self.integral * self.kI + derivative * self.kD

        return speed if not self.flip else -1.0 * speed

