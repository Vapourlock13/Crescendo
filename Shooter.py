import wpilib
import rev
import phoenix5.sensors
from SimplePID import SimplePID

MAX_RPM = 6000

encoder = phoenix5.sensors.CANCoder(9)

left_pivot_motor = phoenix5.WPI_TalonFX(52)  # Set these into brake mode!
right_pivot_motor = phoenix5.WPI_TalonFX(51)  #
right_pivot_motor.setInverted(True)
manual_max_pivot_speed = 0.1
auto_max_pivot_speed = 0.1

pivot_PID = SimplePID(.06, 0.004, 0.0, 0.25)

bottom_shooter = rev.CANSparkFlex(4, rev.CANSparkFlex.MotorType.kBrushless)
bottom_PID =  bottom_shooter.getPIDController()
bottom_encoder = bottom_shooter.getEncoder()
top_shooter = rev.CANSparkFlex(6, rev.CANSparkFlex.MotorType.kBrushless)
top_shooter.setInverted(True)
top_PID = top_shooter.getPIDController()
top_encoder = top_shooter.getEncoder()
shooter_speed = 0.1


targetA = 0.0
targetB = 0.0
targetX = 0.0


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

def current_speed():
    return bottom_encoder.getVelocity()


def run( gunspeed = shooter_speed):
    top_shooter.set(gunspeed)
    bottom_shooter.set(gunspeed)



def stop():
    top_shooter.set(0.0)
    bottom_shooter.set(0.0)


def set_to(angle: float) -> float:

    speed = pivot_PID.get_speed(angle, position())
    if not speed == 0.0:
        speed = speed/abs(speed) * min(abs(speed), auto_max_pivot_speed)

    # smooth out start slew limiting just the increase in speed
    # if(speed - last_rotation_speed >  rot_speed_increase_step  )

    left_pivot_motor.set(speed)
    right_pivot_motor.set(speed)

    return speed

def unsafe_rotate(amount: float):
    left_pivot_motor.set(amount * manual_max_pivot_speed)
    right_pivot_motor.set(amount * manual_max_pivot_speed)
