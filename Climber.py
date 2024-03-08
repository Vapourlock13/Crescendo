import wpilib
import phoenix5

left_climb_motor = phoenix5.WPI_TalonFX(53)
left_climb_motor.setInverted(True)
right_climb_motor = phoenix5.WPI_TalonFX(54)  # may need to be inverted
right_climb_motor.setInverted(True)
# index_motor.setInverted(True)


MAX_EXTENSION_ENCODER_VALUE = -1200000
MIN_RETRACT_ENCODER_VALUE = -10000
MAX_CLIMBER_SPEED = 0.5


def zero_encoders() -> None:
    # zero the sensor
    left_climb_motor.setSelectedSensorPosition(0)
    right_climb_motor.setSelectedSensorPosition(0)


def climb(left_speed: float, right_speed: float) -> (float, float):

    left_encoder = left_climb_motor.getSelectedSensorPosition()
    right_encoder = right_climb_motor.getSelectedSensorPosition()

    if (left_speed < 0.0 and left_encoder > MAX_EXTENSION_ENCODER_VALUE) or (left_speed > 0.0 and left_encoder < MIN_RETRACT_ENCODER_VALUE):
        left_climb_motor.set(left_speed * MAX_CLIMBER_SPEED)
    else:
        left_climb_motor.set(0.0)
    if (right_speed < 0.0 and left_encoder < MAX_EXTENSION_ENCODER_VALUE) or (right_speed > 0.0 and left_encoder > MIN_RETRACT_ENCODER_VALUE):
        right_climb_motor.set(right_speed * MAX_CLIMBER_SPEED)
    else:
        right_climb_motor.set(0.0)

    return left_encoder, right_encoder

def unsafe_climb(left_speed: float, right_speed: float) -> float:
    left_climb_motor.set(left_speed * 0.5)
    right_climb_motor.set(right_speed * 0.5)

def position(side: str) -> float:
    return left_climb_motor.getSelectedSensorPosition() if side.upper() == 'L' else right_climb_motor.getSelectedSensorPosition()

def pos2():
    return right_climb_motor.getSelectedSensorPosition()

