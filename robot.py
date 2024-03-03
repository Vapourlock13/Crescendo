import phoenix5
import wpilib
import ntcore
import navx
import rev
# import phoenix5.sensors

import II
import Shooter



from swerve import Swerve


class MyRobot(wpilib.TimedRobot):
    def robotInit(self):

        #Basics
        self.timer = wpilib.Timer()
        self.sd = ntcore.NetworkTableInstance.getDefault().getTable('SmartDashboard')
        self.navx = navx.AHRS.create_spi()
        self.crap = wpilib.DigitalInput(1)

        #power on limelights
        wpilib.PowerDistribution().setSwitchableChannel(enabled=True)  # USE THIS FOR SWITCHABLE CHANNEL

        #Limelight table instances
        self.limeF = ntcore.NetworkTableInstance.getDefault().getTable("limelight-intake")
        self.limeB = ntcore.NetworkTableInstance.getDefault().getTable("limelight-shooter")

        self.swerve = Swerve(self.sd, self.navx)

        #Controller assignment
        self.driver = wpilib.XboxController(0)
        self.shotgun = wpilib.XboxController(1)


        #self.pivotL = phoenix5.WPI_TalonFX(52) # Set these into brake mode!
        #self.pivotR = phoenix5.WPI_TalonFX(51) #
        #self.pivotR.setInverted(True)

        #self.shooterB = rev.CANSparkFlex(4, rev.CANSparkFlex.MotorType.kBrushless)
        #self.shooterT = rev.CANSparkFlex(6, rev.CANSparkFlex.MotorType.kBrushless)
        #self.shooterT.setInverted(True)

        #self.beaam = wpilib.DigitalInput(9)

        self.sd.putNumber("Intake Speed:", .1)
        self.sd.putNumber("Pivot Speed:", .1)
        self.sd.putNumber("Shooter Speed:", .1)
        self.sd.putNumber("Feed Speed", .8)


    def teleopInit(self):
        self.timer.reset()
        self.timer.start()
        self.navx.zeroYaw()

        II.intake_speed = self.sd.getNumber("Intake Speed:", .1)
        II.feed_speed = self.sd.getNumber("Feed Speed", .8)

        Shooter.shooter_speed = self.sd.getNumber("Shooter Speed:", .1)
        Shooter.pivot_speed = self.sd.getNumber("Pivot Speed:", .1)



    def teleopPeriodic(self):
        # grab limelight positions
        #tx = self.lime.getNumber("tx", 2)
        #ty = self.lime.getNumber("ty", 2)
        #ta = self.lime.getNumber("ta", 2)

        # Main Drive functions and encoder reporting
        self.swerve.drive(self.driver, self.limeF)
        self.swerve.Report_Encoder_Positions()

        #Pivot Controls
        #self.pivotL.set(self.driver.getLeftY() * pivot_speed)
        #self.pivotR.set(self.driver.getLeftY() * pivot_speed)


        #Shooter.manual_aim(self.driver.getLeftY())
        #Shooter.unsafe_rotate(self.driver.getLeftY())


        if self.driver.getAButton():
            II.intake()
        elif self.driver.getBButton():
            II.feed()
        else:
            II.stop()

        if self.driver.getRightBumper():
            Shooter.run()
            #self.shooterT.set(shooter_speed)
            #self.shooterB.set(shooter_speed)
        else:
            Shooter.stop()
            #self.shooterT.set(0)
            #self.shooterB.set(0)



        # display limelight positions
        if self.timer.hasElapsed(0.5):
            self.sd.putNumber("Left Y Stick", self.driver.getLeftY())

            #self.sd.putNumber("tx", tx)
            #self.sd.putNumber("ty", ty)
            #self.sd.putNumber("ta", ta)

            #self.sd.putBoolean("Beam Break", self.beaam.get())

            self.sd.putNumber("Pivot", Shooter.position())

            self.sd.putNumber("BotAngle",self.navx.getYaw())

            self.sd.putBoolean("OhCrapSwitch", self.crap.get())

            #self.sd.putBoolean("Limelights", wpilib.PowerDistribution.getSwitchableChannel())



