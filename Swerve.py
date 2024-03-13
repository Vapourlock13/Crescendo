import rev
import ntcore
import math
import phoenix5.sensors

from SimplePID import SimplePID



# cancoder Absolute start values
cancoder1_absolute_forward = 0.0  # 133.4 #313.4 #148.8
cancoder3_absolute_forward = 0.0  # 328.6 #148.6 #263.5
cancoder5_absolute_forward = 0.0  # 323.7 #143.7 #323.96
cancoder7_absolute_forward = 0.0  # 195.5 #15.5 #195.58


# Returns an angle in the bounds 0 to 360
def clean_angle(angle):
    while angle < 0.0:
        angle += 360.0
    while angle > 360.0:
        angle -= 360
    return angle


# Returns an angle in the bounds -180 to 180
def dirty_angle(angle):
    while angle < -180.0:
        angle += 360.0
    while angle > 180.0:
        angle -= 360.0
    return angle


# Converts a Vector into its constituent components
def Vector_To_Components(ang: float, mag: float) -> (float, float):
    x = -1.0 * mag * math.sin(math.radians(ang))
    y = -1.0 * mag * math.cos(math.radians(ang))

    return x, y


# Combines Components into a Vector
def Components_To_Vector(x: float, y: float) -> (float, float):
    ang = 0.0
    mag = math.sqrt(x * x + y * y)

    if y == 0.0 and x == 0.0:
        return ang, mag

    if y == 0.0:
        if x < 0.0:
            ang = 90.0
        else:
            ang = 270.0
    else:
        ang = math.degrees(math.atan(x / y))
        # fix for quadrant
        if y > 0:
            ang += 180.0
        if ang < 0:
            ang += 360.0

    return ang, mag


class Swerve:

    def __init__(self, sd, navx):
        self.sd = sd
        self.navx = navx

        self.fl = Module(3, cancoder3_absolute_forward, 3, 44, sd, drive_flip=True, turn_flip=True)  # Reversed motors
        self.fr = Module(1, cancoder1_absolute_forward, 1, 42, sd, turn_flip=True)  # Reversed turning motor
        self.bl = Module(5, cancoder5_absolute_forward, 5, 46, sd)
        self.br = Module(7, cancoder7_absolute_forward, 2, 48, sd)

        self.fr_drive_encoder = self.fr._drive_motor.getEncoder()
        self.fr_drive_CPR = self.fr_drive_encoder.getCountsPerRevolution()

        self.last_fl_ang = 0.0
        self.last_fr_ang = 0.0
        self.last_bl_ang = 0.0
        self.last_br_ang = 0.0

        self.odometry_x = 0.0
        self.odometry_y = 0.0

        self.facing_PID = SimplePID(.01, 0.0, 0.0, 1.0)
        self.hold_facing_PID = SimplePID(.01,0.0,0.0,0.1)
        self.last_facing = 0.0
        self.MAX_AUTO_TURN_SPEED = 0.5
        self.SPEED_LIMIT = 1.0

        self.sd.putString("Swerve", "Ready")

    def field_orientate(self, x: float, y: float) -> (float, float):
        # vectorize left joystick
        ang, mag = Components_To_Vector(x, y)

        # compensate for field orientation
        ang = clean_angle(ang + self.navx.getYaw())

        # return components
        return Vector_To_Components(ang, mag)

    def drive(self, x, y, turn, field_orientation=True, report=False):

        self.update_odometry()

        # self.sd.putNumber("BotAngle", self.navx.getYaw())
        # self.sd.putNumber("y", y)
        # self.sd.putNumber("x", x)
        # self.sd.putNumber("turn", turn)
        # self.sd.putNumber("FL Angle", self.fl.current_angle)
        # self.sd.putNumber("FR Angle", self.fr.current_angle)

        if field_orientation:
            x, y = self.field_orientate(x, y)

        if turn == 0 and math.sqrt(x**2+y**2) > .05:
            # keep previous facing
           turn = self.hold_facing_PID.get_speed(self.last_facing, self.navx.getYaw())
        else:
            self.last_facing = self.navx.getYaw()

        turn_size = .707 * turn

        # combine turn and ortho and convert to vector
        fl_ang, fl_mag = Components_To_Vector(x + turn_size, y - turn_size)
        fr_ang, fr_mag = Components_To_Vector(x + turn_size, y + turn_size)
        bl_ang, bl_mag = Components_To_Vector(x - turn_size, y - turn_size)
        br_ang, br_mag = Components_To_Vector(x - turn_size, y + turn_size)

        # Normalize the vectors if needed
        max_mag = max(fl_mag, fr_mag, bl_mag, br_mag)
        if max_mag > 1.0:
            fl_mag /= max_mag
            fr_mag /= max_mag
            bl_mag /= max_mag
            br_mag /= max_mag

        """
        # if the input was below a threshold - don't make any changes
        if max_mag < 0.04:
            fl_mag = fr_mag = bl_mag = br_mag = 0.0
            fl_ang = self.last_fl_ang
            fr_ang = self.last_fr_ang
            bl_ang = self.last_bl_ang
            br_ang = self.last_br_ang
        else:
            self.last_fl_ang = fl_ang
            self.last_fr_ang = fr_ang
            self.last_bl_ang = bl_ang
            self.last_br_ang = br_ang
        """
        if fl_mag == 0.0: fl_ang = self.last_fl_ang
        if fr_mag == 0.0: fr_ang = self.last_fl_ang
        if bl_mag == 0.0: bl_ang = self.last_fl_ang
        if br_mag == 0.0: br_ang = self.last_fl_ang

        self.fl.set_module(fl_ang, fl_mag * self.SPEED_LIMIT)
        self.fr.set_module(fr_ang, fr_mag * self.SPEED_LIMIT)
        self.bl.set_module(bl_ang, bl_mag * self.SPEED_LIMIT)
        self.br.set_module(br_ang, br_mag * self.SPEED_LIMIT)

        if report:
            self.sd.putNumber("FL ANG", fl_ang)
            self.sd.putNumber("FL MAG", fl_mag)
            self.sd.putNumber("FR ANG", fr_ang)
            self.sd.putNumber("FR MAG", fr_mag)
            self.sd.putNumber("BL ANG", bl_ang)
            self.sd.putNumber("BL MAG", bl_mag)
            self.sd.putNumber("BR ANG", br_ang)
            self.sd.putNumber("BR MAG", br_mag)

        self.update_odometry()

        self.last_fl_ang = fl_ang
        self.last_fr_ang = fr_ang
        self.last_bl_ang = bl_ang
        self.last_br_ang = br_ang

    def Report_Encoder_Positions(self):
        self.sd.putNumber("FL Encoder Actual", self.fl.encoder_position)
        # self.sd.putNumber("FL Encoder Modified", self.fl.current_angle)
        self.sd.putNumber("FR Encoder Actual", self.fr.encoder_position)
        # self.sd.putNumber("FR Encoder Modified", self.fr.current_angle)
        self.sd.putNumber("BL Encoder Actual", self.bl.encoder_position)
        # self.sd.putNumber("BL Encoder Modified", self.bl.current_angle)
        self.sd.putNumber("BR Encoder Actual", self.br.encoder_position)
        # self.sd.putNumber("BR Encoder Modified", self.br.current_angle)

    def turn_to_face(self,x:float, y:float, angle: float) -> None:

        self.sd.putNumber("angle to hit", angle)
        self.sd.putNumber("current angle", self.navx.getYaw())
        turn_speed = self.facing_PID.get_speed(angle, self.navx.getYaw())
        self.sd.putNumber("turn speed", turn_speed)
        # limit max turn speed
        if not turn_speed == 0.0:
            turn_speed = turn_speed / abs(turn_speed) * min(abs(turn_speed), self.MAX_AUTO_TURN_SPEED)

        self.drive(x,y,turn_speed)

    def aim_at_target(self, x:float, y:float, tag_x:float) -> None:
        if not -4<tag_x<-2:
            #direction = tag_x/abs(tag_x)
            turn_speed = tag_x * 0.01
            if turn_speed != 0.00:
                turn_speed = turn_speed / abs(turn_speed) * min(abs(turn_speed), self.MAX_AUTO_TURN_SPEED)
            #turn_speed = direction * turn_speed
        else:
            turn_speed = 0
        self.drive(x,y,turn_speed)

    def note_aim(self, x:float, y:float, tag_x:float) -> None:
        if not -3<tag_x<3:
            #direction = tag_x/abs(tag_x)
            turn_speed = tag_x * 0.01
            if turn_speed != 0.00:
                turn_speed = turn_speed / abs(turn_speed) * min(abs(turn_speed), self.MAX_AUTO_TURN_SPEED)
            #turn_speed = direction * turn_speed
        else:
            turn_speed = 0
        self.drive(x,y,turn_speed,field_orientation= False)

    def update_odometry(self):
        # revolutions of motor (which is count/CPR) * gear ratio * wheel diameter * fudge
        magnitude = self.fr_drive_encoder.getPosition() / self.fr_drive_CPR * 6.75 * 8 * math.pi * -60      # Reset Encoder for next tick
        self.fr_drive_encoder.setPosition(0.0)
        # Break distance into x,y components
        x_traveled, y_traveled = Vector_To_Components(self.last_fr_ang, magnitude)
        # add to odometry_x_y
        self.odometry_x += x_traveled
        self.odometry_y += y_traveled

    def reset_odometry(self):
        self.odometry_x = 0.0
        self.odometry_y = 0.0
        self.fr_drive_encoder.setPosition(0.0)

        ...

    def odometry(self) -> (float, float):
        """
        Get the distance traveled in x and y since last call to reset_odometry

        :return: The distance traveled in inches (x, y)
        :rtype: (float, float)
        """
        return self.odometry_x, self.odometry_y

    @property
    def x_travel(self):
        return self.odometry_x

    @property
    def y_travel(self):
        return self.odometry_y

    @property
    def speed_limit(self):
        return self.SPEED_LIMIT

    def set_speed_limit(self, new_limit: float):
        self.SPEED_LIMIT = new_limit


class Module:  # sets up each module
    def __init__(self, encoder_id, abs_forward, drive_id, turn_id, sd, turn_flip=False, drive_flip=False):
        self._encoder_id = encoder_id
        self._encoder_abs_forward = abs_forward
        self._drive_id = drive_id
        self._turn_id = turn_id
        self.sd = sd
        self.turn_flip = turn_flip
        self.drive_flip = drive_flip

        self.encoder = phoenix5.sensors.CANCoder(self._encoder_id)
        self._drive_motor = rev.CANSparkFlex(self._drive_id, rev.CANSparkFlex.MotorType.kBrushless)
        self._turn_motor = rev.CANSparkMax(self._turn_id, rev.CANSparkMax.MotorType.kBrushless)
        self._turn_con = Turn_Controller(sd)

    def set_module(self, angle, speed):
        # self.sd.putNumber("abs encode", self.encoder.getAbsolutePosition() )

        # self.sd.putNumber("target", angle)
        # self.sd.putNumber("current", self.current_angle)

        angle_diff = angle - self.current_angle

        # if angle_diff < -90.0 or angle_diff > 90:
        # angle = clean_angle(angle)  # removed + 180
        # speed *= -1.0

        turn_speed = self._turn_con.Rot_Velocity(angle, self.current_angle)

        turn_direction = 1.0 if self.turn_flip else -1.0
        drive_direction = 1.0 if self.drive_flip else -1.0

        self._turn_motor.set(turn_speed * turn_direction)
        self._drive_motor.set(speed * drive_direction)

    @property
    def current_angle(self):
        return self.encoder.getAbsolutePosition() - self._encoder_abs_forward

    @property
    def encoder_position(self):
        return self.encoder.getAbsolutePosition()


class Turn_Controller:

    def __init__(self, sd):
        self._kP = 0.008 #sd.getNumber("kP", .008)
        self._kI = 0.0 #sd.getNumber("kI", 0.0)
        self._kD = 0.0 #sd.getNumber("kD", 0.0)
        self._angle_integral = 0.0
        self._last_angle_error = 0.0
        self.sd = sd

    def Rot_Velocity(self, target_angle, current_angle):
        angle_error = dirty_angle(target_angle - current_angle)
        self._angle_integral += angle_error * .02
        angle_derivative = (angle_error - self._last_angle_error) / .02

        # reset integral if within range
        if -0.5 < angle_error <= 0.5:
            self._angle_integral = 0.0

        # update persistent variables
        self._last_angle_error = angle_error

        self.sd.putNumber("angle_error", angle_error)
        self.sd.putNumber("integral", self._angle_integral)
        self.sd.putNumber("angle derivative", angle_derivative)

        speed = angle_error * self._kP + self._angle_integral * self._kI + angle_derivative * self._kD
        self.sd.putNumber("speed", speed)
        return speed
