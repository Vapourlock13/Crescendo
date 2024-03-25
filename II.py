import wpilib
import rev
import phoenix5

intake_motor = rev.CANSparkMax(43, rev.CANSparkMax.MotorType.kBrushless)
#intake_motor.setInverted(True)
index_motor = phoenix5.WPI_TalonFX(57)  # may need to be inverted
#index_motor.setInverted(True)

intake_speed = -0.4
feed_speed = -0.8
index_state = "intake"  #In real comp: "load"


# def hey_hello ():
# hey = hello.get()
# hello = wpilib.DigitalInput(0).get()
# return hello

# def init():
# hi = wpilib.DigitalInput(0).get()


def intake():
    global index_state

    if index_state == "intake":
        if wpilib.DigitalInput(9).get():
            intake_motor.set(intake_speed)
            index_motor.set(intake_speed)
        else:
            intake_motor.set(0)
            intake_motor.set(0)
            index_state = "locked"

    elif index_state == "locked":
        intake_motor.set(0)
        index_motor.set(0.15)
        if wpilib.DigitalInput(9).get():
            index_state = "loaded"
    else:
        intake_motor.set(0)
        index_motor.set(0)

def reverse_intake():
    intake_motor.set(-0.5)


def feed():
    global index_state
    index_state = "intake"
    intake_motor.set(0.0)
    index_motor.set(feed_speed)


def stop():
    intake_motor.set(0.0)
    index_motor.set(0.0)


def reload():
    intake_motor.set(0.0)
    index_motor.set(0.1)

def stop_index():
    index_motor.set(0.0)

def stop_intake():
    intake_motor.set(0.0)


"""
class II():
    intake_motor = rev.CANSparkMax(43,rev.CANSparkMax.MotorType.kBrushless)
    intake_motor.setInverted(True)
    index_motor = phoenix5.WPI_TalonFX(57)  # may need to be inverted
    index_motor.setInverted(True)
    beam = wpilib.DigitalInput(9)

    @classmethod
    def intake(cls):
        if cls.beam.get():
            cls.intake_motor.set(0.0)
            cls.index_motor.set(0.0)
        else:
            cls.intake_motor.set(.25)
            cls.index_motor.set(.4)


    @classmethod
    def feed(cls):
        cls.intake_motor.set(0.0)
        cls.index_motor.set(1.0)


    @classmethod
    def stop(cls):
        cls.intake_motor.set(0.0)
        cls.index_motor.set(0.0)


    @classmethod
    def reload(cls):
        cls.intake_motor.set(0.0)
        cls.index_motor.set(-0.1)

"""
