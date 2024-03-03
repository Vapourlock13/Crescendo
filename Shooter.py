import wpilib
import rev
import phoenix5.sensors
from SimplePID import SimplePID


encoder = phoenix5.sensors.CANCoder(9)

left_pivot_motor = phoenix5.WPI_TalonFX(52)  # Set these into brake mode!
right_pivot_motor = phoenix5.WPI_TalonFX(51)  #
right_pivot_motor.setInverted(True)
pivot_speed = 0.1

pivot_PID = SimplePID(.005,0.0,0.0,1.0)


bottom_shooter = rev.CANSparkFlex(4, rev.CANSparkFlex.MotorType.kBrushless)
top_shooter = rev.CANSparkFlex(6, rev.CANSparkFlex.MotorType.kBrushless)
top_shooter.setInverted(True)
shooter_speed = 0.1


def manual_aim(adjust_speed):
    #if wpilib.DigitalInput(0).get():
        #left_pivot_motor.set(0.0)
        #right_pivot_motor.set(0.0)
    if (position() > 0.0  and adjust_speed < 0.0) or (position() < 135.0 and adjust_speed > 0.0):
        left_pivot_motor.set(adjust_speed * pivot_speed)
        right_pivot_motor.set(adjust_speed * pivot_speed)
    else:
        left_pivot_motor.set(0.0)
        right_pivot_motor.set(0.0)

def position():
    return encoder.getAbsolutePosition()

def run():
    top_shooter.set(shooter_speed)
    bottom_shooter.set(shooter_speed)

def stop():
    top_shooter.set(0.0)
    bottom_shooter.set(0.0)

def set_to(angle: float) -> float:

    speed = pivot_PID.get_speed(angle, position())

    left_pivot_motor.set(speed * .2)
    right_pivot_motor.set(speed * .2)



    return speed

#def OhCrap() -> bool:
#    return wpilib.DigitalInput(0).get()

#def unsafe_rotate(amount):
    #left_pivot_motor.set(amount * pivot_speed)
    #right_pivot_motor.set(amount * pivot_speed)


