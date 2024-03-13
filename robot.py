import phoenix5
import wpilib
# from wpilib import SmartDashboard
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
        self.tester = wpilib.XboxController(2)
        self.shotgun_is_shooting = False
        self.unsafe_mode = False
        self.moving_to_intake = False
        self.moving_to_speaker = False
        self.is_shooting = False


        #self.beaam = wpilib.DigitalInput(9)

        self.sd.putNumber("Intake Speed:", .45)
        self.sd.putNumber("Pivot Speed:", .25)
        self.sd.putNumber("Shooter Speed:", .3)
        self.sd.putNumber("Feed Speed", .8)

        Climber.zero_encoders()

        #CameraServer stream test
        #CameraServer.enableLogging()
        #CameraServer.startAutomaticCapture()
        #cam = CameraServer.getServer()

        # autonomous variables


        self.auto_selected = ""
        self.auto_delay = 0
        self.auto_step = 0
        self.sd.putNumber("Autonomous Delay",0.0)


        self.default_auto = "Cross The Line"
        self.center_start = "Center Start"
        self.chooser = wpilib.SendableChooser()
        self.chooser.setDefaultOption("Cross The LIne", self.default_auto)
        self.chooser.addOption("Center Start", self.center_start)
        wpilib.SmartDashboard.putData("Autonomous",self.chooser)



    def teleopInit(self):
        self.timer.reset()
        self.timer.start()

        self.navx.zeroYaw()

        # remove for comp
        Climber.zero_encoders()
        self.swerve.reset_odometry()

        II.intake_speed = self.sd.getNumber("Intake Speed:", .1)
        #II.feed_speed = self.sd.getNumber("Feed Speed", .8)
        II.index_state = "intake"

        # self.sd.putNumber("hold facing kP", 0.1)
        self.swerve.set_speed_limit(self.sd.getNumber("Speed Limit", 0.2))

        self.swerve.last_facing = 0.0


        Shooter.shooter_speed = self.sd.getNumber("Shooter Speed:", .1)


        self.swerve.facing_PID.kP = self.sd.getNumber("dpad facing kP", 0.01)
        self.swerve.hold_facing_PID.kp = self.sd.getNumber("hold facing kP", .01)
        self.swerve.MAX_AUTO_TURN_SPEED = self.sd.getNumber("Target A",0.5)


        #Shooter REV PID setup
        # self.sd.putNumber("Target RPM", 0)
        # self.sd.putNumber("kP", 0)
        # self.sd.putNumber("kI", 0)
        # self.sd.putNumber("kD",0)
        # self.sd.putNumber("maxOut", 1.0)
        # self.sd.putNumber("minOut", -1.0)
        #
        Shooter.RPM = self.sd.getNumber("Target RPM", 0)
        Shooter.shooter_kP = self.sd.getNumber("kP",0)
        Shooter.shooter_kI = self.sd.getNumber("kI", 0)
        # Shooter.kI = self.sd.getNumber("kI", 0)
        # Shooter.kD = self.sd.getNumber("kD",0)
        # Shooter.maxOut = self.sd.getNumber("maxOut",1.0)
        # Shooter.minOut = self.sd.getNumber("minOut",-1.0)
        #



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

        # if self.tester.getAButton():
        #     Shooter.set_rpm(self.sd.getNumber("Target B",1000))
        # else:
        #     Shooter.run(0.0)

        # Shotgun Controls:
        # UNSAFE MODE WHEN D-PAD IS DOWN


        if self.shotgun.getPOV() == 180:
            self.unsafe_mode = True
            Shooter.unsafe_rotate(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.unsafe_climb(self.shotgun.getLeftY(),self.shotgun.getRightY())
        elif self.unsafe_mode:
            self.unsafe_mode = False
            Shooter.unsafe_rotate(0.0)
            Climber.unsafe_climb(0.0,0.0)


        # NORMAL MODE
        else:
            #Shooter.manual_aim(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.climb(self.remap_stick(self.shotgun.getLeftY(),0.2), self.remap_stick(self.shotgun.getRightY(), 0.2))

            if self.shotgun.getBButton():
                self.shotgun_is_shooting = True
                Shooter.set_angle(98.0)
                Shooter.set_rpm(1300) #800
                if self.shotgun.getYButton():
                    II.feed()
            elif self.shotgun_is_shooting:
                Shooter.stop_shooter()
                Shooter.stop_pivot()
                II.stop_index()
                self.shotgun_is_shooting = False
            elif self.shotgun.getXButton():
                Shooter.set_angle(36.0)
                self.moving_to_intake = True
            elif not self.shotgun.getXButton() and self.moving_to_intake:
                Shooter.stop_pivot()
                self.moving_to_intake = False
            #
            # elif self.shotgun.getAButton():
            #     self.moving_to_speaker = True
            #     Shooter.set_angle(30)
            #
            # elif self.moving_to_speaker:
            #     Shooter.stop_pivot()
            #     self.moving_to_speaker = False



        #     if self.shotgun.getXButton():
        #         Shooter.set_rpm(2000)
        #     else:
        #         Shooter.set_rpm(0)
        #
        # if self.shotgun.getBButton():
        #     Shooter.shooter_speed = 0.25
        #     Shooter.set_angle(102.3)
        #     ...



        # Driver Controls:

        #Deadzone setup
        x = self.remap_stick(self.driver.getLeftX(), 0.1)
        y = self.remap_stick(self.driver.getLeftY(), 0.1)
        turn = self.remap_stick(self.driver.getRightX(), 0.1)
        snap_heading = self.driver.getPOV()
        self.sd.putNumber("heading", snap_heading)

        # Swerve Driving
        if self.driver.getAButton(): #Intaking
            self.swerve.note_aim(x,y,self.limeF.getNumber("tx", 0))

        elif snap_heading != -1: #Face specific direction
            self.swerve.turn_to_face(x,y,snap_heading)

        #elif self.driver.getRightBumper(): # Aiming at speaker LIMELIGHT :C
            #self.swerve.aim_at_target(x, y, self.limeB.getNumber("tx", 0))

        elif self.driver.getLeftBumper(): # Swerve w/ Field Orientation off
            self.swerve.drive(x, y, turn, field_orientation= False)

        else: #Normal Swerve
            self.swerve.drive(x, y, turn)


        #Driver II controls
        if self.driver.getAButton():
            II.intake()
        #elif self.driver.getRightBumper(): Auto Aim should remove need for this :C
            #II.feed()

        elif self.driver.getRightBumper():
            self.is_shooting = True
            Shooter.set_rpm(3500)
            if self.driver.getXButton():
                II.feed()

        elif self.is_shooting:
            Shooter.stop_shooter()
            II.stop_index()
            self.is_shooting = False

        elif not self.shotgun_is_shooting:
            II.stop()





        # display limelight positions
        if self.timer.hasElapsed(0.5):
            self.sd.putNumber("Pivot position", Shooter.position())
            self.sd.putNumber("Left Climber", Climber.position('L'))
            self.sd.putNumber("Right Climber", Climber.position('R'))
            self.sd.putNumber("Top Shooter Speed", Shooter.current_speed('T'))
            self.sd.putNumber("Bottom Shooter Speed", Shooter.current_speed('B'))
            self.sd.putNumber("current", self.navx.getYaw())
            #self.sd.putNumber("Shooter Speed", 1300)
            self.swerve.Report_Encoder_Positions()

            self.sd.putNumber("tx_b", self.limeB.getNumber("tx", 0))
            self.sd.putNumber("X traveled", self.swerve.x_travel)
            self.sd.putNumber("Y traveled",self.swerve.y_travel)


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

    def autonomousInit(self):
        self.timer.reset()
        self.timer.start()
        self.navx.zeroYaw()

        Climber.zero_encoders()
        self.swerve.reset_odometry()

        self.autoSelected = self.chooser.getSelected()
        #self.auto_selected = "CrossTheLine"
        print("Auto selected: " + self.autoSelected)
        self.auto_delay = self.sd.getNumber("Autonomous Delay",0.0)

    def autonomousPeriodic(self):
        self.sd.putNumber("Y traveled", self.swerve.y_travel)

        if(self.timer.get() > self.auto_delay):

            match self.autoSelected:
                case self.default_auto:
                    if self.swerve.y_travel > -48:
                        self.swerve.drive( 0, -.3, 0)
                    else:
                        self.swerve.drive(0,0,0)


                case self.center_start:
                    match self.auto_step:
                        case 0:
                            Shooter.set_rpm(3500)
                            if self.auto_delay + 2.0 < self.timer.get():
                                II.feed()
                            if self.auto_delay + 3.0 < self.timer.get():
                                self.auto_step += 1
                                II.stop_index()
                                Shooter.stop_shooter()
                        case 1:
                            self.autoSelected = self.default_auto


                            ...

                    #         set shooter rpm
                    #         rpm good then feed
                    #         wait 1 sec after feeding
                    #         turn off index and shooter
                    #         set autoSelected to CrossTheLine
                    # ...
                case "LeftStart":
                    match self.auto_step:
                        case 0:
                            ...
                        #     drive forward a few feet
                        # case 1:
                        #     self.swerve.turn_to_face(0,0, 225)
                        # case 2:
                        #     limelight aim
                        # case 3:
                        #     set shooter rpm
                        #     feed and fire
                        # case 4:
                        #     turn off motors
                        #

                    ...
                case "RightStart":
                    ...



