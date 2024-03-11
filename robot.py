import phoenix5
import wpilib
import ntcore
from ntcore import NetworkTableInstance
from cscore import CameraServer
import navx
import rev
# import phoenix5.sensors

import II
import Shooter
import Climber



from Swerve import Swerve


class MyRobot(wpilib.TimedRobot):
    def robotInit(self):

        #Basics
        self.timer = wpilib.Timer()
        self.sd = ntcore.NetworkTableInstance.getDefault().getTable('SmartDashboard')
       # self.cameraSelection = NetworkTableInstance.getDefault().getTable("").getEntry("CameraSelection")
        self.navx = navx.AHRS.create_spi()

        #power on limelights
        wpilib.PowerDistribution().setSwitchableChannel(enabled=True)  # USE THIS FOR SWITCHABLE CHANNEL

        #Limelight table instances
        self.limeF = ntcore.NetworkTableInstance.getDefault().getTable("limelight-intake")
        self.limeB = ntcore.NetworkTableInstance.getDefault().getTable("limelight-shooter")

        self.swerve = Swerve(self.sd, self.navx)

        #Controller assignment
        self.driver = wpilib.XboxController(0)
        self.shotgun = wpilib.XboxController(1)


        #self.beaam = wpilib.DigitalInput(9)

        self.sd.putNumber("Intake Speed:", .1)
        self.sd.putNumber("Pivot Speed:", .1)
        self.sd.putNumber("Shooter Speed:", .1)
        self.sd.putNumber("Feed Speed", .8)

        Climber.zero_encoders()

        #CameraServer stream test
        #CameraServer.enableLogging()
        #CameraServer.startAutomaticCapture()
        #cam = CameraServer.getServer()

        #test
        #self.climber = phoenix5.WPI_TalonFX(54) #Positive winds, Negative extends


    def teleopInit(self):
        self.timer.reset()
        self.timer.start()
        self.navx.zeroYaw()

        # remove for comp
        Climber.zero_encoders()


        II.intake_speed = self.sd.getNumber("Intake Speed:", .1)
        II.feed_speed = self.sd.getNumber("Feed Speed", .8)
        II.index_state = "intake"

        self.sd.putNumber("hold facing kP", 0.1)
        self.swerve.set_speed_limit(self.sd.getNumber("Speed Limit", 0.2))


        Shooter.shooter_speed = self.sd.getNumber("Shooter Speed:", .1)


        self.swerve.facing_PID.kP = self.sd.getNumber("dpad facing kP", 0.01)
        self.swerve.hold_facing_PID.kp = self.sd.getNumber("hold facing kP", .01)
        self.swerve.MAX_AUTO_TURN_SPEED = self.sd.getNumber("Target A",0.5)

        """
        Shooter REV PID setup
        self.sd.putNumber("Target RPM", 0)
        self.sd.putNumber("kP", 0)
        self.sd.putNumber("kI", 0)
        self.sd.putNumber("kD",0)
        self.sd.putNumber("maxOut", 1.0)
        self.sd.putNumber("minOut", -1.0)
        
        Shooter.RPM = self.sd.getNumber("Target RPM", 0)
        Shooter.kP = self.sd.getNumber("kP",0)
        Shooter.kI = self.sd.getNumber("kI", 0)
        Shooter.kD = self.sd.getNumber("kD",0)
        Shooter.maxOut = self.sd.getNumber("maxOut",1.0)
        Shooter.minOut = self.sd.getNumber("minOut",-1.0)
        """



        """
        Pivot PID setup
        Shooter.auto_max_pivot_speed = self.sd.getNumber("Pivot Speed:", .1)
        Shooter.pivot_PID.tolerance = self.sd.getNumber("Pivot Tolerance", 1.0)
        Shooter.pivot_PID.kP = self.sd.getNumber("kP", .005)
        Shooter.pivot_PID.kI = self.sd.getNumber("kI",0.0)
        Shooter.targetA = self.sd.getNumber("Target A", 30.0)
        Shooter.targetB = self.sd.getNumber("Target B", 60.0)
        Shooter.targetX = self.sd.getNumber("Target X", 100.0)
        
        self.sd.putNumber("Pivot Speed:", .1)
        self.sd.putNumber("kP", .005)
        self.sd.putNumber("kI", 0.0)
        self.sd.putNumber("Target A", 30.0)
        self.sd.putNumber("Target B", 60.0)
        self.sd.putNumber("Target X", 100.0)
        self.sd.putNumber("Pivot Tolerance", 1.0)
        """



    def teleopPeriodic(self):

        # Shotgun Controls:
        # UNSAFE MODE WHEN A IS HELD
        if self.shotgun.getAButton():
            Shooter.unsafe_rotate(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.unsafe_climb(self.shotgun.getLeftY(),self.shotgun.getRightY())

        # NORMAL MODE
        else:
            Shooter.manual_aim(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.climb(self.remap_stick(self.shotgun.getLeftY(),0.2), self.remap_stick(self.shotgun.getRightY(), 0.2))

        if self.shotgun.getBButton():
            #Shooter.shooter_speed = 0.25
            Shooter.set_angle(102.3)




        # Driver Controls:

        #Deadzone setup
        x = self.remap_stick(self.driver.getLeftX(), 0.1)
        y = self.remap_stick(self.driver.getLeftY(), 0.1)
        turn = self.remap_stick(self.driver.getRightX(), 0.1)
        snap_heading = self.driver.getPOV()
        self.sd.putNumber("heading", snap_heading)

        #Swerve Driving
        if self.driver.getAButton():
            self.swerve.note_aim(x,y,self.limeF.getNumber("tx", 0))
        elif snap_heading != -1:
            self.swerve.turn_to_face(x,y,snap_heading)
        elif self.driver.getXButton():
            self.swerve.aim_at_target(x, y, self.limeB.getNumber("tx", 0))
        else:
            self.swerve.drive(x, y, turn)


        #Driver II controls
        if self.driver.getAButton():
            II.intake()
        elif self.driver.getBButton():
            II.feed()
        else:
            II.stop()

        #Driver Manual Shooter controls
        if self.driver.getRightBumper():
            Shooter.set_rpm(self.sd.getNumber("Shooter Speed:", .1)) #self.driver.getRightY()
            self.sd.putNumber("bottom out",Shooter.set_rpm(self.sd.getNumber("Shooter Speed:", 1000)))
        else:
            Shooter.stop()



        """
        # Main Drive functions and encoder reporting
        if(self.driver.getLeftBumper()):
            self.swerve.drive(self.driver.getLeftX(), self.driver.getLeftY(), self.note_aim(), field_orientation = False)
        else:
            if not self.driver.getYButton(): #temp
                self.swerve.drive(self.driver.getLeftX(), self.driver.getLeftY(),self.driver.getRightX())

        self.swerve.Report_Encoder_Positions()

        #Pivot Controls

        if self.shotgun.getYButton(): #temp
            if self.driver.getXButton():
                Shooter.set_to(30.0)
            else:
                Shooter.manual_aim(self.shotgun.getRightY())
        else:
            Shooter.manual_aim(0)


        Shooter.manual_aim(self.shotgun.getRightY())

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

    
        # used for pivot PID control
        if self.shotgun.getAButton():
            Shooter.set_to(Shooter.targetA)
        elif self.shotgun.getBButton():
            Shooter.set_to(Shooter.targetB)
        elif self.shotgun.getXButton():
            Shooter.set_to(Shooter.targetX)
        else:
            Shooter.manual_aim()
        """


        # display limelight positions
        if self.timer.hasElapsed(0.5):
            self.sd.putNumber("Pivot position", Shooter.position())
            self.sd.putNumber("Left Climber", Climber.position('L'))
            self.sd.putNumber("Right Climber", Climber.position('R'))
            self.sd.putNumber("Top Shooter Speed", Shooter.current_speed('T'))
            self.sd.putNumber("Bottom Shooter Speed", Shooter.current_speed('B'))
            self.sd.putNumber("current", self.navx.getYaw())
            self.sd.putNumber("Shooter Speed", 1300)
            self.swerve.Report_Encoder_Positions()

            self.sd.putNumber("tx_b", self.limeB.getNumber("tx", 0))

            # self.sd.putNumber("Right Climber", Climber.position('R'))

            # self.sd.putNumber("Left Y Stick", self.shotgun.getLeftY())
            # self.sd.putNumber("Remapped Y", self.remap_stick(self.shotgun.getLeftY(), 0.25))
            # self.sd.putNumber("tx", tx)
            # self.sd.putNumber("ty", ty)
            # self.sd.putNumber("ta", ta)
            # self.sd.putBoolean("Beam Break", self.beaam.get())
            # self.sd.putNumber("Pivot", Shooter.position())
            # self.sd.putNumber("BotAngle",self.navx.getYaw())
            # self.sd.putString("Index Stage", II.index_state)
            # self.sd.putBoolean("Shooter Ready", II.index_state == "loaded")
            # self.sd.putNumber("tx", self.limeF.getNumber("tx", 0))
            # self.sd.putNumber("B_tx", self.limeB.getNumber("tx", 0))
            # self.sd.putBoolean("Limelights", wpilib.PowerDistribution.getSwitchableChannel())

    def note_aim(self) -> float:
        tx = self.limeF.getNumber("tx", 0)
        return 0 if -3 < tx < 3 else tx/abs(tx) * 0.5


    def remap_stick(self, value: float, deadzone: float) -> float:
        return 0.0 if abs(value) < deadzone else value/abs(value) * (abs(value) - deadzone)/(1-deadzone)



