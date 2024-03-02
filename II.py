import wpilib
import rev
import phoenix5

intake_motor = rev.CANSparkMax(43, rev.CANSparkMax.MotorType.kBrushless)
intake_motor.setInverted(True)
index_motor = phoenix5.WPI_TalonFX(57)  # may need to be inverted
index_motor.setInverted(True)
#beam = wpilib.DigitalInput(2)




intake_speed = .1
feed_speed = .1


def hey_hello ():
    #hey = hello.get()
    hello = wpilib.DigitalInput(0).get()
    return hello

def init():
     hi = wpilib.DigitalInput(0).get()





def intake():
    if True: #not beam.get():
        intake_motor.set(intake_speed)
        index_motor.set(intake_speed)
    #else:
        #intake_motor.set(0)
        #index_motor.set(0)


def feed():
    intake_motor.set(0.0)
    index_motor.set(feed_speed)


def stop():
    intake_motor.set(0.0)
    index_motor.set(0.0)


def reload():
    intake_motor.set(0.0)
    index_motor.set(-0.1)



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
