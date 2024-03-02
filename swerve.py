import rev
import ntcore
import math
import phoenix5.sensors

# cancoder Absolute start values
cancoder1_absolute_forward = 313.4 #133.4 #313.4 #148.8
cancoder3_absolute_forward = 148.6 #328.6 #148.6 #263.5
cancoder5_absolute_forward = 143.7 #323.7 #143.7 #323.96
cancoder7_absolute_forward = 15.5 #195.5 #15.5 #195.58


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


class Swerve:

    def __init__(self, sd, navx):
        self.sd = sd
        self.navx = navx

        self.fr = Module(1, cancoder1_absolute_forward, 1, 42, sd, turn_flip=True) #Reversed turning motor
        self.fl = Module(3, cancoder3_absolute_forward, 3, 44, sd, drive_flip=True, turn_flip=True) #Reversed motors
        self.bl = Module(5, cancoder5_absolute_forward, 5, 46, sd)
        self.br = Module(7, cancoder7_absolute_forward, 2, 48, sd)

        self.last_fl_ang = 0.0
        self.last_fr_ang = 0.0
        self.last_bl_ang = 0.0
        self.last_br_ang = 0.0

        self.sd.putString("Swerve", "Ready")

    def drive(self, driver):
        #joystick inputs:
        joy_y = -driver.getLeftY()                                      #Remove The Negatives
        joy_x = -driver.getLeftX()
        turn = -driver.getRightX()


        self.sd.putNumber("BotAngle", self.navx.getYaw())
        self.sd.putNumber("y", joy_y)
        self.sd.putNumber("x", joy_x)
        self.sd.putNumber("turn", turn)
        self.sd.putNumber("FL Angle", self.fl.current_angle)
        self.sd.putNumber("FR Angle", self.fr.current_angle)

        if not driver.getRightBumper(): #Using Field orientation
            # vectorize left joystick
            ang, mag = self.Components_To_Vector(joy_x, joy_y)

            # compensate for field orientation
            ang = clean_angle(ang + self.navx.getYaw())

            # add rotation
            x, y = self.Vector_To_Components(ang, mag)

        turn_size = 0.0
        if turn < -0.05 or turn > 0.05:                                 ##Test if dead zone needed
            turn_size = math.sqrt(2) * turn                             ##Get rid of the *sqrt

        # fl
        fl_x = x + turn_size
        fl_y = y - turn_size
        fl_ang, fl_mag = self.Components_To_Vector(fl_x, fl_y)

        # fr
        fr_x = x + turn_size
        fr_y = y + turn_size
        fr_ang, fr_mag = self.Components_To_Vector(fr_x, fr_y)

        # bl
        bl_x = x - turn_size
        bl_y = y - turn_size
        bl_ang, bl_mag = self.Components_To_Vector(bl_x, bl_y)

        # br
        br_x = x - turn_size
        br_y = y + turn_size
        br_ang, br_mag = self.Components_To_Vector(br_x, br_y)

        # Normalize the vectors if needed / vectors in standard pos?
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

        self.fl.set_module(fl_ang, fl_mag)
        self.fr.set_module(fr_ang, fr_mag)
        self.bl.set_module(bl_ang, bl_mag)
        self.br.set_module(br_ang, br_mag)



    def Report_Encoder_Positions(self):
        self.sd.putNumber("FL Encoder Actual", self.fl.encoder_position)
        self.sd.putNumber("FL Encoder Modified", self.fl.current_angle)
        self.sd.putNumber("FR Encoder Actual", self.fr.encoder_position)
        self.sd.putNumber("FR Encoder Modified", self.fr.current_angle)
        self.sd.putNumber("BL Encoder Actual", self.bl.encoder_position)
        self.sd.putNumber("BL Encoder Modified", self.bl.current_angle)
        self.sd.putNumber("BR Encoder Actual", self.br.encoder_position)
        self.sd.putNumber("BR Encoder Modified", self.br.current_angle)

    def Vector_To_Components(self, ang, mag):
        x = -1.0 * mag * math.sin(math.radians(ang))
        y = -1.0 * mag * math.cos(math.radians(ang))

        return x, y

    def Components_To_Vector(self, x, y):

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


class Module: # sets up each module
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

        self.sd.putNumber("target", angle)
        self.sd.putNumber("current", self.current_angle)

        angle_diff = angle - self.current_angle
            
        if angle_diff < -90.0 or angle_diff > 90:
            angle = clean_angle(angle) #removed + 180
            speed *= -1.0

        turn_speed = self._turn_con.Rot_Velocity(angle, self.current_angle)

        turn_direction = 1.0 if self.turn_flip else -1.0
        drive_direction = 1.0 if self.drive_flip else -1.0

        self._turn_motor.set(turn_speed * turn_direction)
        self._drive_motor.set(speed * drive_direction * .2)

    @property
    def current_angle(self):
        return self.encoder.getAbsolutePosition() - self._encoder_abs_forward
    @property
    def encoder_position(self):
        return self.encoder.getAbsolutePosition()


class Turn_Controller:

    def __init__(self, sd):
        self._kP = sd.getNumber("kP", .008)
        self._kI = sd.getNumber("kI", 0.0)
        self._kD = sd.getNumber("kD", 0.0)
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
