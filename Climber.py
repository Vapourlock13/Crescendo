import wpilib
import phoenix5

left_climb_motor = phoenix5.WPI_TalonFX(53)
left_climb_motor.setInverted(True)
#right_climb_motor = phoenix5.WPI_TalonFX(54)  # may need to be inverted
# index_motor.setInverted(True)



def zero_encoders() -> None:
    #left_climb_motor.configSelectedFeedbackSensor(phoenix5.FeedbackDevice.CTRE_MagEncoder_Relative)
    # zero the sensor
    left_climb_motor.setSelectedSensorPosition(200)

    #right_climb_motor.configSelectedFeedbackSensor(phoenix5.FeedbackDevice.CTRE_MagEncoder_Relative)
    # zero the sensor
    #right_climb_motor.setSelectedSensorPosition(0)

def climb(speed: float) -> float:
    left_climb_motor.set(speed * 0.5)
    #right_climb_motor.set(speed * 0.1)

    left_encoder = left_climb_motor.getSelectedSensorPosition()
    #right_encoder = right_climb_motor.getSelectedSensorPosition()

    return left_encoder#, right_encoder

