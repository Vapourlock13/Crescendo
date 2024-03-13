import wpilib
import rev
import phoenix5.sensors
from SimplePID import SimplePID

MAX_RPM = 6000

"""
RPM = 0
kP = 0.0
kI = 0.0
kD = 0.0
maxOut = 1.0
minOut = -1.0
"""

shooter_kI = 0.0
shooter_kP = 0.0001
RPM = 0
encoder = phoenix5.sensors.CANCoder(9)

left_pivot_motor = phoenix5.WPI_TalonFX(52)  # Set these into brake mode!
right_pivot_motor = phoenix5.WPI_TalonFX(51)  #
right_pivot_motor.setInverted(True)
manual_max_pivot_speed = 0.1
auto_max_pivot_speed = 0.4

pivot_PID = SimplePID(.06, 0.004, 0.0, 0.25)

bottom_shooter = rev.CANSparkFlex(4, rev.CANSparkFlex.MotorType.kBrushless)
bottom_PID = bottom_shooter.getPIDController()
bottom_encoder = bottom_shooter.getEncoder()
top_shooter = rev.CANSparkFlex(6, rev.CANSparkFlex.MotorType.kBrushless)
top_shooter.setInverted(True)
top_PID = top_shooter.getPIDController()
top_encoder = top_shooter.getEncoder()
shooter_speed = 0.1
last_rpm_set = 0
# bottom_speed = 0
# top_speed = 0

top_integral = 0.0
bottom_integral = 0.0

targetA = 0.0
targetB = 0.0
targetX = 0.0

"""
def set_shooter_PID():
    bottom_PID.setP(kP)
    top_PID.setP(kP)

    bottom_PID.setI(kI)
    top_PID.setI(kI)

    bottom_PID.setD(kD)
    top_PID.setD(kD)

    bottom_PID.setIZone(0.0)
    top_PID.setIZone(0.0)

    bottom_PID.setOutputRange(minOut,maxOut)
    top_PID.setOutputRange(minOut,maxOut)

    bottom_PID.setFF(0)
    top_PID.setFF(0)
"""


# def set_shooter_speed(speed:float):
#     bottom_PID.setReference(speed,rev.CANSparkFlex.ControlType.kVelocity)
#     top_PID.setReference(speed,rev.CANSparkFlex.ControlType.kVelocity)
#

def manual_aim(adjust_speed: float = 0.0):
    if wpilib.DigitalInput(0).get():
        left_pivot_motor.set(0.0)
        right_pivot_motor.set(0.0)
    elif (position() > 0.0 and adjust_speed < 0.0) or (position() < 135.0 and adjust_speed > 0.0):
        left_pivot_motor.set(adjust_speed * manual_max_pivot_speed)
        right_pivot_motor.set(adjust_speed * manual_max_pivot_speed)
    else:
        left_pivot_motor.set(0.0)
        right_pivot_motor.set(0.0)


def position():
    return encoder.getAbsolutePosition()


def current_speed(side: str) -> float:
    return bottom_encoder.getVelocity() if side.upper() == 'B' else top_encoder.getVelocity()


def run(gun_speed=shooter_speed):
    if gun_speed == 0.0:
        stop_shooter()
    top_shooter.set(gun_speed)
    bottom_shooter.set(gun_speed)


def stop_shooter():
    top_shooter.set(0.0)
    bottom_shooter.set(0.0)
    global bottom_integral
    global top_integral
    bottom_integral = 0
    top_integral = 0


def stop_pivot():
    left_pivot_motor.set(0)
    right_pivot_motor.set(0)


def set_angle(angle: float) -> float:
    speed = pivot_PID.get_speed(angle, position())
    if not speed == 0.0:
        speed = speed / abs(speed) * min(abs(speed), auto_max_pivot_speed)

    # smooth out start slew limiting just the increase in speed
    # if(speed - last_rotation_speed >  rot_speed_increase_step  )

    left_pivot_motor.set(speed)
    right_pivot_motor.set(speed)

    return speed


def set_rpm(rpm: int) -> float:
    global top_integral
    global bottom_integral

    if rpm == 0:
        top_shooter.set(0)
        bottom_shooter.set(0)
        bottom_integral = 0
        top_integral = 0

        return 0

    # VERSION 1
    # """
    # set the desired rpm
    # :param rpm:
    # :return current rpm:
    # """
    # feed_forward = max(.0002 * rpm - 0.1, 0.0)
    # top_error = rpm - current_speed('T')
    # top_shooter.set(feed_forward + top_error * shooter_kP)
    # bottom_error = rpm - current_speed('B')
    # bv = feed_forward + bottom_error * shooter_kP
    # bottom_shooter.set(feed_forward + bottom_error * shooter_kP)
    # return bv

    # VERSION 2

    #
    # global last_rpm_set
    # global bottom_speed
    # global top_speed
    #
    # if not rpm == last_rpm_set:
    #     last_rpm_set = rpm
    #     top_speed = 0
    #     bottom_speed = 0
    #
    # top_speed += (rpm - current_speed('T')) * shooter_kP
    # top_shooter.set(top_speed)
    # bottom_speed += (rpm - current_speed('B')) * shooter_kP
    # bottom_shooter.set(bottom_speed)
    # return bottom_speed

    # VERSION 3

    base_speed = .0002 * rpm - .001

    top_error = rpm - current_speed('T')
    bottom_error = rpm - current_speed('B')

    top_integral += top_error
    bottom_integral += bottom_error

    top_speed = base_speed + top_error * shooter_kP + top_integral * shooter_kI
    bottom_speed = base_speed + bottom_error * shooter_kP + bottom_integral * shooter_kI
    top_shooter.set(top_speed)
    bottom_shooter.set(bottom_speed)

    return bottom_speed


def unsafe_rotate(amount: float):
    left_pivot_motor.set(amount * manual_max_pivot_speed)
    right_pivot_motor.set(amount * manual_max_pivot_speed)
