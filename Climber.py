import wpilib
import phoenix5

left_climb_motor = phoenix5.WPI_TalonFX(53)
left_climb_motor.setInverted(True)
right_climb_motor = phoenix5.WPI_TalonFX(54)  # may need to be inverted
right_climb_motor.setInverted(True)

# Tell the motors to use the integrated encoders
falcon_settings = phoenix5.TalonFXConfiguration()
falcon_settings.primaryPID.selectedFeedbackSensor = phoenix5.FeedbackDevice.IntegratedSensor
left_climb_motor.configAllSettings(falcon_settings)
right_climb_motor.configAllSettings(falcon_settings)

MAX_EXTENSION_ENCODER_VALUE = -1_200_000
MIN_RETRACT_ENCODER_VALUE = -60_000
MAX_CLIMBER_SPEED = 1.0
MAX_UNSAFE_SPEED = 0.2

rpm = 0
kP = 0
kI = 0
kD = 0
maxOut = 0
minOut = 0


def zero_encoders() -> None:
    # zero the sensor
    left_climb_motor.setSelectedSensorPosition(0)
    right_climb_motor.setSelectedSensorPosition(0)


def climb(left_speed: float, right_speed: float) -> (float, float):
    left_encoder = left_climb_motor.getSelectedSensorPosition()
    right_encoder = right_climb_motor.getSelectedSensorPosition()

    if (left_speed < 0.0 and left_encoder > MAX_EXTENSION_ENCODER_VALUE) or (
            left_speed > 0.0 and left_encoder < MIN_RETRACT_ENCODER_VALUE):
        left_climb_motor.set(left_speed * MAX_CLIMBER_SPEED)
    else:
        left_climb_motor.set(0.0)

    if (right_speed < 0.0 and right_encoder > MAX_EXTENSION_ENCODER_VALUE) or (
            right_speed > 0.0 and right_encoder < MIN_RETRACT_ENCODER_VALUE):
        right_climb_motor.set(right_speed * MAX_CLIMBER_SPEED)
    else:
        right_climb_motor.set(0.0)

    return left_encoder, right_encoder


def unsafe_climb(left_speed: float, right_speed: float) -> None:
    """
    Changes the climber position with NO safety checks
    :param left_speed:
    :param right_speed:
    :return None:
    """
    left_climb_motor.set(left_speed * MAX_UNSAFE_SPEED)
    right_climb_motor.set(right_speed * MAX_UNSAFE_SPEED)


def position(side: str) -> float:
    """
    Returns the encoder value.  More neg is more extended. "L" for left, "R" (or anything) for right
    :param side:
    :return:
    """
    return left_climb_motor.getSelectedSensorPosition() if side.upper() == 'L' \
        else right_climb_motor.getSelectedSensorPosition()

