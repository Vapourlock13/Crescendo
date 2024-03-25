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

        # Basics
        self.timer = wpilib.Timer()
        self.game_timer = wpilib.Timer()
        self.sd = ntcore.NetworkTableInstance.getDefault().getTable('SmartDashboard')
        # self.cameraSelection = NetworkTableInstance.getDefault().getTable("").getEntry("CameraSelection")
        self.navx = navx.AHRS.create_spi()

        # power on limelights
        wpilib.PowerDistribution().setSwitchableChannel(enabled=True)  # USE THIS FOR SWITCHABLE CHANNEL

        # Limelight table instances
        self.limeF = ntcore.NetworkTableInstance.getDefault().getTable("limelight-intake")
        self.limeB = ntcore.NetworkTableInstance.getDefault().getTable("limelight-shooter")

        self.tx_F = self.limeF.getNumber("tx", 0)
        self.tx_B = self.limeB.getNumber("tx", 0)
        self.ty_B = self.limeB.getNumber("ty", 0)
        self.aim_angle = 36.0

        self.swerve = Swerve(self.sd, self.navx)

        # Controller assignment
        self.driver = wpilib.XboxController(0)
        self.shotgun = wpilib.XboxController(1)
        self.tester = wpilib.XboxController(2)
        self.shotgun_is_shooting = False
        self.unsafe_mode = False
        self.moving_to_intake = False
        self.moving_to_speaker = False
        self.is_shooting = False
        self.sucking = False
        self.current_time = 0.0
        self.get_time_auto = True
        self.snipe = True
        self.wait_on_snipe = False

        # self.beaam = wpilib.DigitalInput(9)

        # self.sd.putNumber("Intake Speed:", .45)
        # self.sd.putNumber("Pivot Speed:", .25)
        # self.sd.putNumber("Shooter Speed:", .3)
        # self.sd.putNumber("Feed Speed", .8)

        Climber.zero_encoders()

        # CameraServer stream test
        # CameraServer.enableLogging()
        # CameraServer.startAutomaticCapture()
        # cam = CameraServer.getServer()

        # autonomous variables

        self.auto_selected = ""
        self.auto_delay = 0
        self.auto_step = 0
        #self.sd.putNumber("Autonomous Delay", 0.0)

        self.default_auto = "Cross The Line"

        #Center Autos
        self.center_start = "Center Start"
        self.center_stop = "Center Stop"
        self.center_start_2_notes = "Center Start 2 Notes"

        #Left Autos
        #self.left_start = "Left Start"
        self.left_start_stop = "Left Start then stop"

        #Right Autos
        self.right_start_stop = "Right Start then stop"
        #self.right_start = "Right Start"

        #Blue Autos
        self.blue_2_note = "Left Start 2 Notes"
        self.blue_3_note = "Left Start 3 Notes"

        #Red Autos
        self.red_2_note = "Red 2 Notes"
        self.red_3_note = "Red 3 Notes"

        #ETC
        self.red_note_midline = "3 notes starting right of red speaker"
        self.four_note_left = "Left Start 4 Notes"


        self.chooser = wpilib.SendableChooser()

        self.chooser.setDefaultOption("Cross The Line", self.default_auto)

        #Center Autos
        self.chooser.addOption("Center Start", self.center_start)
        self.chooser.addOption("Center Stop", self.center_stop)
        self.chooser.addOption("Center Start 2", self.center_start_2_notes)

        #Right Autos
        self.chooser.addOption("Right Start Stop", self.right_start_stop)
        # self.chooser.addOption("Right Start", self.right_start)

        #Left Autos
        self.chooser.addOption("Left Start Stop", self.left_start_stop)
        #self.chooser.addOption("Left Start", self.left_start)

        #Blue Autos
        self.chooser.addOption("Blue 3 Note", self.blue_3_note)

        #Red Autos
        self.chooser.addOption("Red 3 Note", self.red_3_note)

        #ETC
        self.chooser.addOption("4 Note Left", self.four_note_left)

        wpilib.SmartDashboard.putData("Autonomous", self.chooser)

    def teleopInit(self):
        self.timer.reset()
        self.timer.start()

        self.game_timer.reset()
        self.game_timer.start()

        # self.navx.zeroYaw()

        # remove for comp
        Climber.zero_encoders()
        self.swerve.reset_odometry()

        # II.intake_speed = self.sd.getNumber("Intake Speed:", .1)
        # II.feed_speed = self.sd.getNumber("Feed Speed", .8)
        II.index_state = "intake"


        # self.sd.putNumber("hold facing kP", 0.1)
        # self.swerve.set_speed_limit(self.sd.getNumber("Speed Limit", 0.2))

        self.swerve.last_facing = 0.0

        self.swerve.set_drive_motors_brake(0)

        # Shooter.shooter_speed = self.sd.getNumber("Shooter Speed:", .1)

        # self.swerve.facing_PID.kP = self.sd.getNumber("dpad facing kP", 0.01)
        # self.swerve.hold_facing_PID.kp = self.sd.getNumber("hold facing kP", .01)
        # self.swerve.MAX_AUTO_TURN_SPEED = self.sd.getNumber("Target A", 0.5)

        # Shooter REV PID setup
        # self.sd.putNumber("Target RPM", 0)
        # self.sd.putNumber("kP", 0)
        # self.sd.putNumber("kI", 0)
        # self.sd.putNumber("kD",0)
        # self.sd.putNumber("maxOut", 1.0)
        # self.sd.putNumber("minOut", -1.0)
        #
        # Shooter.RPM = self.sd.getNumber("Target RPM", 0)
        # Shooter.shooter_kP = self.sd.getNumber("kP", 0)
        # Shooter.shooter_kI = self.sd.getNumber("kI", 0)
        # # Shooter.kI = self.sd.getNumber("kI", 0)
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

        # Shooter.test_RPM = self.sd.getNumber("TEST RPM:", 1000)
        # Shooter.shooter_kP = self.sd.getNumber("TEST kP:", 0.0)
        # Shooter.shooter_kI = self.sd.getNumber("TEST kI", 0.0)
        # Shooter.shooter_kD = self.sd.getNumber("TEST kD:", 0.0)

    def teleopPeriodic(self):
        self.tx_F = self.limeF.getNumber("tx", 0)
        self.tx_B = self.limeB.getNumber("tx", 0)
        self.ty_B = self.limeB.getNumber("ty", 0) + self.sd.getNumber("TESTING", 0)

        self.sd.putNumber("TIME REMAINING:", self.game_timer.getMatchTime())

        # intake_set = 0.0
        # index_set = 0.0
        # pivot_angle_set = -1.0
        # shooter_set = 0.0
        #
        # ALT SHOTGUN
        #
        # # UNSAFE MODE
        # if self.shotgun.getPOV() == 180:
        #     self.unsafe_mode = True
        #     Shooter.unsafe_rotate(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
        #     Climber.unsafe_climb(self.shotgun.getLeftY(), self.shotgun.getRightY())
        # elif self.unsafe_mode:
        #     self.unsafe_mode = False
        #     Shooter.unsafe_rotate(0.0)
        #     Climber.unsafe_climb(0.0, 0.0)
        #
        #
        # # NORMAL MODE
        # else:
        #     Climber.climb(self.remap_stick(self.shotgun.getLeftY(), 0.2),
        #                   self.remap_stick(self.shotgun.getRightY(), 0.2))
        #
        #     if self.shotgun.getBButton():
        #         pivot_angle_set = 98.8
        #         shooter_set = 1000
        #         if self.shotgun.getLeftBumper():
        #             II.feed()
        #
        #     elif self.shotgun.getXButton():
        #         pivot_angle_set = 36.0
        #
        #     elif self.shotgun.getAButton():
        #         pivot_angle_set = 10
        #
        # Shooter.set_rpm(shooter_set) if shooter_set > 0 else Shooter.stop_shooter()
        # Shooter.set_angle(pivot_angle_set) if pivot_angle_set > 0.0 else Shooter.stop_pivot()
        #


        # if self.tester.getAButton():
        #     Shooter.set_rpm(self.sd.getNumber("TEST RPM:",1000))
        # else:
        #     Shooter.stop_shooter()
        #
        # if self.tester.getBButton():
        #     Shooter.set_angle(98)
        # elif self.tester.getXButton():
        #     Shooter.set_angle(36)
        # else:
        #     Shooter.stop_pivot()

        #Shotgun Controls:
        #UNSAFE MODE WHEN D-PAD IS DOWN


        if self.shotgun.getPOV() == 180:
            self.unsafe_mode = True
            Shooter.unsafe_rotate(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.unsafe_climb(self.shotgun.getLeftY(), self.shotgun.getRightY())
        elif self.unsafe_mode:
            self.unsafe_mode = False
            Shooter.unsafe_rotate(0.0)
            Climber.unsafe_climb(0.0, 0.0)


        # NORMAL MODE
        else:
            # Shooter.manual_aim(self.shotgun.getLeftTriggerAxis() - self.shotgun.getRightTriggerAxis())
            Climber.climb(self.remap_stick(self.shotgun.getLeftY(), 0.2),
                          self.remap_stick(self.shotgun.getRightY(), 0.2))


            if self.shotgun.getBButton():
                self.shotgun_is_shooting = True
                Shooter.set_angle(98.8)
                Shooter.set_rpm(1000)  # 800
                if self.shotgun.getLeftBumper():
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

            elif self.shotgun.getAButton():
                self.moving_to_speaker = True
                Shooter.set_angle(14.5)

            elif self.moving_to_speaker:
                Shooter.stop_pivot()
                self.moving_to_speaker = False

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

        # Deadzone setup
        x = self.remap_stick(self.driver.getLeftX(), 0.1)
        y = self.remap_stick(self.driver.getLeftY(), 0.1)
        turn = self.remap_stick(self.driver.getRightX(), 0.1)
        snap_heading = self.driver.getPOV()
        # self.sd.putNumber("heading", snap_heading)

        # Swerve Driving
        if self.driver.getAButton():  # Intaking
            self.swerve.note_aim(x, y, self.tx_F)

        elif self.shotgun.getYButton(): #SNIPING CODE
            self.snipe = True
            self.aim_angle = 0.85 * self.ty_B + 13.2 #12.8 #other formula: .703 * self.tx_B + 11.6
            self.swerve.aim_at_target_tele(x, y, self.tx_B, 2)
            Shooter.set_angle(self.aim_angle)
            Shooter.set_rpm(5250)
            self.sd.putBoolean("Sniper Pivot Angle", (self.aim_angle - 1) < Shooter.position() < (self.aim_angle + 1))
            self.sd.putBoolean("Sniper Speed", 5000 < Shooter.current_speed('B'))
            self.sd.putBoolean("Sniper Bot Angle", -1 < self.tx_B < 4)
            if (self.aim_angle - 1) < Shooter.position() < (self.aim_angle + 1) and 5000 < Shooter.current_speed('B') and -1 < self.tx_B < 4:
                II.feed()


        elif self.snipe:
            Shooter.stop_pivot()
            Shooter.stop_shooter()
            II.stop_index()
            self.snipe = False


        elif snap_heading != -1:  # Face specific direction
            self.swerve.turn_to_face(x, y, snap_heading)

        # elif self.driver.getRightBumper(): # Aiming at speaker LIMELIGHT :C
        # self.swerve.aim_at_target(x, y, self.limeB.getNumber("tx", 0))

        elif self.driver.getLeftBumper():  # Swerve w/ Field Orientation off
            self.swerve.drive(x, y, turn, field_orientation=False)

        else:  # Normal Swerve
            self.swerve.drive(x, y, turn)
            self.sd.putNumber("y-stick", y)

        # Driver II controls
        if self.driver.getAButton():
            II.intake()
            self.sucking = True

        elif self.sucking:
            II.stop()
            self.sucking = False

        elif self.driver.getYButton():
            II.index_state = "intake"


        elif self.driver.getRightBumper():
            self.is_shooting = True
            Shooter.set_rpm(3500)

        elif self.driver.getRightTriggerAxis() > .1:
            Shooter.set_rpm(4500)
            self.is_shooting = True

        elif self.driver.getLeftTriggerAxis() > .1:
            Shooter.set_rpm(2000 * self.driver.getLeftTriggerAxis())
            self.is_shooting = True

        elif self.is_shooting:
            Shooter.stop_shooter()
            II.stop_index()
            self.is_shooting = False

        if self.driver.getXButton() and self.is_shooting:
            II.feed()

        if self.timer.hasElapsed(0.5):
            self.sd.putNumber("Pivot position", Shooter.position())
            self.sd.putNumber("Left Climber", Climber.position('L'))
            self.sd.putNumber("Right Climber", Climber.position('R'))
            self.sd.putString("Shooter RPM", f"{Shooter.current_speed('T'):.0f}")
            #self.sd.putString("Bottom Shooter Speed", f"{Shooter.current_speed('B'):.0f}")
            self.sd.putNumber("BoomBot Facing", self.navx.getYaw() )
            # self.sd.putNumber("Shooter Speed", 1300)
            self.swerve.Report_Encoder_Positions()

            self.sd.putNumber("tx_F", self.limeF.getNumber("tx", 0))
            self.sd.putNumber("tx_B", self.limeB.getNumber("tx", 0))
            self.sd.putNumber("ty_B", self.limeB.getNumber("ty", 0))
            self.sd.putNumber("X traveled", self.swerve.x_travel)
            self.sd.putNumber("Y traveled", self.swerve.y_travel)

            self.sd.putString("Index State", II.index_state)

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

    # def note_aim(self) -> float:
    #     tx = self.limeF.getNumber("tx", 0)
    #     return 0 if -3 < tx < 3 else tx / abs(tx) * 0.5

    def remap_stick(self, value: float, deadzone: float) -> float:
        return 0.0 if abs(value) < deadzone else value / abs(value) * (abs(value) - deadzone) / (1 - deadzone)

    def sniper(self, x = 0, y = 0):
        self.aim_angle = 0.85 * (self.ty_B - 0.5) + 13.2  # other formula: .703 * self.tx_B + 11.6
        self.swerve.aim_at_target_tele(x, y, self.tx_B, 2)
        Shooter.set_angle(self.aim_angle)
        Shooter.set_rpm(4750)
        if (self.aim_angle - 1) < Shooter.position() < (self.aim_angle + 1) and 4250 < Shooter.current_speed('B') and -2 < self.tx_B < 4:
            II.feed()
            return True
        return False

    def stop_sniper(self):
        Shooter.stop_pivot()
        Shooter.stop_shooter()
        II.stop_index()

    def autonomousInit(self):
        self.timer.reset()
        self.timer.start()
        self.navx.zeroYaw()
        self.tx_F = self.limeF.getNumber("tx", 0)
        self.tx_B = self.limeB.getNumber("tx", 0)

        Climber.zero_encoders()
        self.swerve.reset_odometry()
        self.swerve.set_drive_motors_brake(1)


        self.autoSelected = self.chooser.getSelected()
        self.auto_step = 0
        # self.auto_selected = "CrossTheLine"
        print("Auto selected: " + self.autoSelected)
        self.auto_delay = self.sd.getNumber("Autonomous Delay", 0.0)
        self.sd.putNumber("Autonomous Delay", self.auto_delay)

        self.get_time_auto = True

    def autonomousPeriodic(self):
        if wpilib.DigitalInput(0).get():
            Shooter.left_pivot_motor.set(0.0)
            Shooter.right_pivot_motor.set(0.0)
            return

        self.sd.putNumber("Y traveled", self.swerve.y_travel)
        self.tx_F = self.limeF.getNumber("tx", 0)
        self.tx_B = self.limeB.getNumber("tx", 0)
        self.ty_B = self.limeB.getNumber("ty", 0)
        self.sd.putNumber("Nav X Yaw", self.navx.getYaw())

        self.sd.putBoolean("Sniper Pivot Angle", (self.aim_angle - 1) < Shooter.position() < (self.aim_angle + 1))
        self.sd.putBoolean("Sniper Speed", 4250 < Shooter.current_speed('B'))
        self.sd.putBoolean("Sniper Bot Angle", -1 < self.tx_B < 4)


        if (self.timer.get() > self.auto_delay):

            match self.autoSelected:

                #CENTER POS AUTOS

                case self.default_auto: #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.default_auto)
                    self.sd.putString("Autonomous Step:", " 0: Drive Forward ")
                    if self.swerve.y_travel > -52:
                        self.swerve.drive(0, -.25 / 2.0, 0)
                    else:
                        self.swerve.drive(0, 0, 0, field_orientation=True)


                case self.center_start: #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.center_start)
                    match self.auto_step:
                        case 0:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Shoot from Subwoofer")

                            Shooter.set_rpm(3500)
                            if self.auto_delay + 2.0 < self.timer.get():
                                II.feed()
                            if self.auto_delay + 3.0 < self.timer.get():
                                II.stop_index()
                                Shooter.stop_shooter()
                                Shooter.stop_pivot()
                                self.auto_step += 1

                        case 1:
                            self.autoSelected = self.default_auto

                            ...

                case self.center_stop: #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.center_start)
                    match self.auto_step:
                        case 0:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Shoot from Subwoofer")

                            Shooter.set_rpm(3500)
                            if self.auto_delay + 2.0 < self.timer.get():
                                II.feed()
                            if self.auto_delay + 3.0 < self.timer.get():
                                II.stop_index()
                                Shooter.stop_shooter()

                case self.center_start_2_notes: #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.center_start_2_notes)
                    match self.auto_step:
                        case 0:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Shoot from Subwoofer")
                            Shooter.set_rpm(3500) #3500
                            if self.auto_delay + 2.0 < self.timer.get():
                                II.feed()
                            if self.auto_delay + 3.0 < self.timer.get():
                                II.stop_index()
                                Shooter.stop_shooter()
                                Shooter.stop_pivot()
                                self.auto_step += 1
                        case 1:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Drive Forward and Intake")

                            II.intake()

                            if self.swerve.y_travel > -200:
                                if II.index_state != "loaded":
                                    self.swerve.note_aim(0, -0.25 / 2.0, self.tx_F)
                                else:
                                    self.swerve.drive(0, 0, 0, field_orientation=True)
                                    Shooter.stop_pivot()
                                    self.auto_step += 1
                            else:
                                self.swerve.drive(0, 0, 0, field_orientation=True)
                        case 2:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")

                            self.swerve.aim_at_target(0, 0, self.tx_B)
                            Shooter.set_angle(14)
                            #if 40 < Shooter.position() < 55:
                                #Shooter.stop_pivot()
                            Shooter.set_rpm(3500) #3500
                            if self.get_time_auto:
                                II.stop()
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.timer.get() > self.current_time + 2.0 and self.timer.get() < self.current_time + 3.0:
                                II.feed()
                            if self.timer.get() > self.current_time + 3.0:
                                II.stop()
                                Shooter.stop_shooter()
                                Shooter.stop_pivot()
                                # self.auto_step += 1

                #LEFT START AUTOS



                case self.left_start_stop:  #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.left_start_stop)
                    match self.auto_step:
                        case 0:  # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if self.timer.get() < self.auto_delay + 1.0:
                                    self.swerve.turn_to_face(0, -0.1, -30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1

                        case 1:  # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 2:  # Turn back to 0
                            self.stop_sniper()
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.swerve.drive(0, 0, 0)
                                Shooter.stop_pivot()
                                Shooter.stop_shooter()

                #RIGHT START AUTOS

                case self.right_start_stop:  #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.right_start_stop)
                    match self.auto_step:
                        case 0:  # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if self.timer.get() < self.auto_delay + 1.0:
                                    self.swerve.turn_to_face(0, -0.1, 30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1

                        case 1:  # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 2:  # Turn back to 0
                            self.stop_sniper()
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.swerve.drive(0, 0, 0)
                                Shooter.stop_pivot()
                                Shooter.stop_shooter()

                #BLUE START AUTOS

                case self.blue_2_note:  # START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.blue_2_note)
                    match self.auto_step:
                        case 0:  # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                            self.get_time_auto = False

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if not -35 < self.navx.getYaw() < -25:
                                    self.swerve.turn_to_face(0, -0.1, -30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1

                        case 1:  # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.current_time = self.timer.get()
                                    self.wait_on_snipe = True

                            if self.wait_on_snipe and self.current_time + 0.5 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 2:  # Turn back to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.wait_on_snipe = False  # Check
                                self.auto_step += 1

                        case 3:  # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.12, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 4:  # Angle back to 0 (precautionary)
                            if not -30 < self.navx.getYaw() < -20:
                                self.swerve.turn_to_face(0.1, 0, -25)
                            else:
                                self.auto_step += 1

                        case 5:  # SECOND SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Second Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 6:
                            self.stop_sniper()
                            self.swerve.drive(0, 0, 0)


                case self.blue_3_note:  #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.blue_3_note)
                    match self.auto_step:
                        case 0:  # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                            self.get_time_auto = False

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if not -35 < self.navx.getYaw() < -25:
                                    self.swerve.turn_to_face(0, -0.1, -30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1

                        case 1:  # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.current_time = self.timer.get()
                                    self.wait_on_snipe = True

                            if self.wait_on_snipe and self.current_time + 0.5 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 2:  # Turn back to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.wait_on_snipe = False  # Check
                                self.auto_step += 1

                        case 3:  # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.12, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 4:  # Angle back to 0 (precautionary)
                            if not -30 < self.navx.getYaw() < -20:
                                self.swerve.turn_to_face(0.1, 0, -25)
                            else:
                                self.auto_step += 1

                        case 5:  # SECOND SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Second Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.current_time = self.timer.get()
                                    self.wait_on_snipe = True

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 6:  # Angle right
                            if not 85 < self.navx.getYaw() < 95:
                                self.swerve.turn_to_face(0.1, 0, 90)
                            else:
                                self.auto_step += 1

                        case 7:  # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.1, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 8:  # Angle to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.wait_on_snipe = False
                                self.auto_step += 1

                        case 9:  # THIRD SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Third Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 10:
                            self.stop_sniper()
                            self.swerve.drive(0, 0, 0)

                #RED START AUTOS

                case self.red_2_note:  # START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.red_2_note)
                    match self.auto_step:
                        case 0:  # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                            self.get_time_auto = False

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if self.timer.get() < self.auto_delay + 1.0:
                                    self.swerve.turn_to_face(0, -0.1, 30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1

                        case 1:  # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 0.5 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 2:  # Turn back to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.wait_on_snipe = False  # Check
                                self.auto_step += 1

                        case 3:  # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.15, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 4:  # Angle back to 0 (precautionary)
                            if not 20 < self.navx.getYaw() < 30:
                                self.swerve.turn_to_face(-0.1, 0, 25)
                            else:
                                self.auto_step += 1

                        case 5:  # SECOND SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Second Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 6:
                            self.stop_sniper()
                            self.swerve.drive(0, 0, 0)

                case self.red_3_note:  #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.red_3_note)
                    match self.auto_step:
                        case 0: # Turn and move before firing
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                            self.get_time_auto = False

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if self.timer.get() < self.auto_delay + 1.0:
                                    self.swerve.turn_to_face(0, -0.1, 30)

                                else:
                                    self.wait_on_snipe = False
                                    self.auto_step += 1


                        case 1: # FIRST SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: First Snipe")

                            if self.sniper(0, 0): #Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 0.5 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 2: # Turn back to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.wait_on_snipe = False # Check
                                self.auto_step += 1

                        case 3: # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.15, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 4: # Angle back to 0 (precautionary)
                            if not 20 < self.navx.getYaw() < 30:
                                self.swerve.turn_to_face(-0.1, 0, 25)
                            else:
                                self.auto_step += 1

                        case 5: # SECOND SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Second Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.stop_sniper()
                                self.auto_step += 1

                        case 6: # Angle left
                            if not -95 < self.navx.getYaw() < -85:
                                self.swerve.turn_to_face(-0.1, 0, -90)
                            else:
                                self.auto_step += 1

                        case 7: # Drive with note aim
                            if II.index_state != "loaded":
                                II.intake()
                                self.swerve.note_aim(0, -0.1, self.tx_F)
                            else:
                                II.stop()
                                self.auto_step += 1

                        case 8: # Angle to 0
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(-0.1, 0, 0)
                            else:
                                self.wait_on_snipe = False
                                self.auto_step += 1

                        case 9: # THIRD SHOT
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Third Snipe")

                            if self.sniper(0, 0):  # Possibly add movement whilst firing
                                if not self.wait_on_snipe:
                                    self.wait_on_snipe = True
                                    self.current_time = self.timer.get()

                            if self.wait_on_snipe and self.current_time + 1.0 < self.timer.get():
                                self.auto_step += 1

                        case 10: #Stop everything
                            self.stop_sniper()
                            self.swerve.drive(0, 0, 0)

                #RISKY AUTOS


                case self.four_note_left: #START OF AN AUTO
                    self.sd.putString("Selected Autonomous:", self.four_note_left)
                    match self.auto_step:
                        case 0:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                            Shooter.set_angle(24)

                            if self.auto_delay < self.timer.get():  # Wait until delay is over
                                if not -35 < self.navx.getYaw() < -25:
                                    self.swerve.turn_to_face(0, -0.15 / 2.0, -30)
                                else:
                                    Shooter.stop_pivot()
                                    self.swerve.drive(0, 0, 0)
                                    self.auto_step += 1

                        case 1:
                            self.swerve.aim_at_target(0, -0.15 / 2.0, self.tx_B)

                            Shooter.set_rpm(3500)

                            if self.get_time_auto:
                                self.current_time = self.timer.get()
                                self.get_time_auto = False

                            if self.timer.get() > self.current_time + .75 and self.timer.get() < self.current_time + 1.0:
                                II.feed()

                            if self.timer.get() > self.current_time + 1.0:
                                II.stop()
                                Shooter.stop_shooter()
                                self.auto_step += 1

                        case 2:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")

                            if not -3 < self.navx.getYaw() < 3:
                                self.swerve.turn_to_face(0, -0.15 / 2.0, 0)

                            else:
                                self.auto_step += 1

                        case 3:
                            self.get_time_auto = True

                            if self.swerve.y_travel > -150:
                                if II.index_state != "loaded":
                                    self.swerve.note_aim(0, -0.2 / 2.0, self.tx_F)
                                    II.intake()
                                else:
                                    self.swerve.drive(0, 0, 0, field_orientation=True)
                                    self.auto_step += 1
                            else:
                                II.stop()
                                self.swerve.drive(0, 0, 0, field_orientation=True)
                        case 4:
                            II.stop()
                            if not -35 < self.navx.getYaw() < 35:
                                self.swerve.turn_to_face(0.15 / 2.0, 0, -30)

                            else:
                                self.auto_step += 1

                        case 5:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")

                            self.swerve.aim_at_target(0.15 / 2.0, 0, self.tx_B)
                            Shooter.set_angle(13)
                            # if 40 < Shooter.position() < 55:
                            # Shooter.stop_pivot()
                            if self.get_time_auto:
                                II.stop()
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 1.0:
                                Shooter.set_rpm(4500)  # 3500
                            if self.timer.get() > self.current_time + 0.75 and self.timer.get() < self.current_time + 1.0:
                                II.feed()
                            if self.timer.get() > self.current_time + 1.0:
                                II.stop()
                                Shooter.stop_shooter()
                                self.auto_step += 1
                        case 6:
                            self.get_time_auto = True
                            if not 85 < self.navx.getYaw() < 95:
                                self.swerve.turn_to_face(0.25 / 2.0, 0, 90)
                            else:
                                self.auto_step +=1
                        case 7:
                            if self.get_time_auto:
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.current_time + 4.0 > self.timer.get():
                                II.intake()
                                if II.index_state != "loaded":
                                    self.swerve.note_aim(0, -0.3 / 2.0, self.tx_F)
                                else:
                                    self.auto_step +=1
                            else:
                                II.stop()
                                self.swerve.drive(0, 0, 0)
                        case 8:
                            II.stop()
                            self.get_time_auto = True
                            if not -5 < self.navx.getYaw() < 5:
                                self.swerve.turn_to_face(0, 0, 0)
                            else:
                                self.auto_step += 1
                        case 9:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")

                            self.swerve.aim_at_target(0, 0, self.limeB.getNumber("tx", 0))
                            Shooter.set_angle(16)
                            # if 40 < Shooter.position() < 55:
                            # Shooter.stop_pivot()
                            if self.get_time_auto:
                                II.stop()
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 1.0:
                                Shooter.set_rpm(4500)  # 3500
                            if self.timer.get() > self.current_time + 0.75 and self.timer.get() < self.current_time + 1.0:
                                II.feed()
                            if self.timer.get() > self.current_time + 1.0:
                                II.stop()
                                Shooter.stop_shooter()
                                self.auto_step += 1
                        case 10:
                            self.get_time_auto = True
                            if not 85 < self.navx.getYaw() < 95:
                                self.swerve.turn_to_face(0.4 / 2.0, 0, 90)
                            else:
                                self.auto_step += 1
                        case 11:
                            if self.get_time_auto:
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.current_time + 4.0 > self.timer.get():
                                II.intake()
                                if II.index_state != "loaded":
                                    self.swerve.note_aim(0, -0.3 / 2.0, self.tx_F)
                                else:
                                    self.auto_step += 1
                            else:
                                II.stop()
                                self.swerve.drive(0, 0, 0)
                        case 12:
                            II.stop()
                            self.get_time_auto = True
                            if not 25 < self.navx.getYaw() < 35:
                                self.swerve.turn_to_face(0, 0, 30)
                            else:
                                self.auto_step += 1
                        case 13:
                            self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")

                            self.swerve.aim_at_target(0, 0, self.tx_B)
                            Shooter.set_angle(11)
                            if self.get_time_auto:
                                II.stop()
                                self.current_time = self.timer.get()
                                self.get_time_auto = False
                            if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 2.0:
                                Shooter.set_rpm(4500)  # 3500
                            if self.timer.get() > self.current_time + 1.0 and self.timer.get() < self.current_time + 2.0:
                                II.feed()
                            if self.timer.get() > self.current_time + 2.0:
                                II.stop()
                                Shooter.stop_shooter()


                # COMMENTED OUT AUTOS


                # case self.red_note_midline:
                #     self.sd.putString("Selected Autonomous", self.red_note_midline)
                #     match self.auto_step:
                #         case 0:
                #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                #             Shooter.set_angle(22)
                #
                #             if self.auto_delay < self.timer.get():  # Wait until delay is over
                #                 if self.timer.get() < self.auto_delay + 1.0:
                #                     self.swerve.turn_to_face(0, -.25 / 2.0, 30)
                #
                #                 else:
                #                     Shooter.stop_pivot()
                #                     self.auto_step += 1
                #
                #         case 1:
                #             self.swerve.aim_at_target(0, 0, self.tx_B)
                #
                #             Shooter.set_rpm(3500)
                #
                #             if self.get_time_auto:
                #                 self.current_time = self.timer.get()
                #                 self.get_time_auto = False
                #
                #             if self.timer.get() > self.current_time + 0.5 and self.timer.get() < self.current_time + 1:
                #                 II.feed()
                #
                #             if self.timer.get() > self.current_time + 1.0:
                #                 II.stop()
                #                 Shooter.stop_shooter()
                #                 Shooter.stop_pivot()
                #                 self.auto_step += 1
                #
                #         case 2:
                #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")
                #
                #             if not -3 < self.navx.getYaw() < 3:
                #                 self.swerve.turn_to_face(0, 0, 0)
                #
                #             else:
                #                 Shooter.stop_pivot()
                #                 self.auto_step += 1
                #
                #         case 3:
                #             self.get_time_auto = True
                #
                #             if II.index_state != "loaded":
                #                 self.swerve.note_aim(0, -0.25 / 2.0, self.limeF.getNumber("tx", 0))
                #                 II.intake()
                #             else:
                #                 self.swerve.drive(0, 0, 0, field_orientation=True)
                #                 self.auto_step += 1
                #         case 4:
                #             II.stop()
                #             if not 25 < self.navx.getYaw() < 35:
                #                 self.swerve.turn_to_face(0, 0, 30)
                #
                #             else:
                #                 Shooter.stop_pivot()
                #                 self.auto_step += 1
                #
                #         case 5:
                #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")
                #
                #             self.swerve.aim_at_target(0, 0, self.limeB.getNumber("tx", 0))
                #             Shooter.set_angle(12)
                #             # if 40 < Shooter.position() < 55:
                #             # Shooter.stop_pivot()
                #
                #             if self.get_time_auto:
                #                 II.stop()
                #                 self.current_time = self.timer.get()
                #                 self.get_time_auto = False
                #             if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 0.5:
                #                 Shooter.set_rpm(4500)  # 3500
                #             if self.timer.get() > self.current_time + .5 and self.timer.get() < self.current_time + 1.0:
                #                 II.feed()
                #             if self.timer.get() > self.current_time + 1.0:
                #                 II.stop()
                #                 Shooter.stop_shooter()
                #                 self.auto_step += 1
                #
                #         case 7:
                #             self.get_time_auto = True
                #             self.auto_step += 1
                #
                #         case 8:
                #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")
                #
                #             if self.get_time_auto:
                #                 self.current_time = self.timer.get()
                #                 self.get_time_auto = False
                #
                #             if not -3 < self.navx.getYaw() < 3:
                #                 self.swerve.turn_to_face(0, 0, 0)
                #
                #             else:
                #                 Shooter.stop_pivot()
                #                 self.auto_step += 1




                    # case self.left_start:
                    #     self.sd.putString("Selected Autonomous:", self.left_start)
                    #     match self.auto_step:
                    #         case 0:
                    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
                    #             Shooter.set_angle(24)
                    #
                    #             if self.auto_delay < self.timer.get(): # Wait until delay is over
                    #                 if self.timer.get() < self.auto_delay + 1.0:
                    #                     self.swerve.turn_to_face(0,0, -30)
                    #
                    #                 else:
                    #                     Shooter.stop_pivot()
                    #                     self.auto_step += 1
                    #
                    #         case 1:
                    #             self.swerve.aim_at_target(0, 0, self.tx_B)
                    #
                    #             Shooter.set_rpm(3500)
                    #
                    #             if self.get_time_auto:
                    #                 self.current_time = self.timer.get()
                    #                 self.get_time_auto = False
                    #
                    #             if self.timer.get() > self.current_time + .5 and self.timer.get() < self.current_time + 1.0:
                    #                 II.feed()
                    #
                    #             if self.timer.get() > self.current_time + 1.0:
                    #                 II.stop()
                    #                 Shooter.stop_shooter()
                    #                 Shooter.stop_pivot()
                    #                 self.auto_step += 1
                    #
                    #         case 2:
                    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")
                    #
                    #             if not -3 < self.navx.getYaw() < 3:
                    #                 self.swerve.turn_to_face(0, 0, 0)
                    #
                    #             else:
                    #                 Shooter.stop_pivot()
                    #                 self.auto_step += 1
                    #
                    #         case 3:
                    #             self.get_time_auto = True
                    #
                    #             if self.swerve.y_travel > -150:
                    #                 if II.index_state != "loaded":
                    #                     self.swerve.note_aim(0, -0.25 / 2.0, self.limeF.getNumber("tx", 0))
                    #                     II.intake()
                    #                 else:
                    #                     self.swerve.drive(0, 0, 0, field_orientation=True)
                    #                     Shooter.stop_pivot()
                    #                     self.auto_step += 1
                    #             else:
                    #                 II.stop()
                    #                 self.swerve.drive(0, 0, 0, field_orientation=True)
                    #         case 4:
                    #             II.stop()
                    #             if not -35 < self.navx.getYaw() < 35:
                    #                 self.swerve.turn_to_face(0, 0, -30)
                    #
                    #             else:
                    #                 Shooter.stop_pivot()
                    #                 self.auto_step += 1
                    #
                    #         case 5:
                    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")
                    #
                    #             self.swerve.aim_at_target(0, 0, self.limeB.getNumber("tx", 0))
                    #             Shooter.set_angle(12)
                    #             # if 40 < Shooter.position() < 55:
                    #             # Shooter.stop_pivot()
                    #             if self.get_time_auto:
                    #                 II.stop()
                    #                 self.current_time = self.timer.get()
                    #                 self.get_time_auto = False
                    #             if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 1.0:
                    #                 Shooter.set_rpm(3500)  # 3500
                    #             if self.timer.get() > self.current_time + 0.5 and self.timer.get() < self.current_time + 1.0:
                    #                 II.feed()
                    #             if self.timer.get() > self.current_time + 1.0:
                    #                 II.stop()
                    #                 Shooter.stop_shooter()
                    #                 Shooter.stop_pivot()
                    #                 self.swerve.drive(0, 0, 0)
                    #                 # self.auto_step += 1

            # case self.left_start:
            #     self.sd.putString("Selected Autonomous:", self.left_start)
            #     match self.auto_step:
            #         case 0:
            #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
            #             Shooter.set_angle(22)
            #
            #             if self.auto_delay < self.timer.get():  # Wait until delay is over
            #                 if self.timer.get() < self.auto_delay + 1.0:
            #                     self.swerve.turn_to_face(0, -.25 / 2.0, 30)
            #
            #                 else:
            #                     Shooter.stop_pivot()
            #                     self.auto_step += 1
            #
            #         case 1:
            #             self.swerve.aim_at_target(0, 0, self.tx_B)
            #
            #             Shooter.set_rpm(3500)
            #
            #             if self.get_time_auto:
            #                 self.current_time = self.timer.get()
            #                 self.get_time_auto = False
            #
            #             if self.timer.get() > self.current_time + 0.5 and self.timer.get() < self.current_time + 1:
            #                 II.feed()
            #
            #             if self.timer.get() > self.current_time + 1.0:
            #                 II.stop()
            #                 Shooter.stop_shooter()
            #                 Shooter.stop_pivot()
            #                 self.auto_step += 1
            #
            #         case 2:
            #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")
            #
            #             if not -3 < self.navx.getYaw() < 3:
            #                 self.swerve.turn_to_face(0, 0, 0)
            #
            #             else:
            #                 Shooter.stop_pivot()
            #                 self.auto_step += 1
            #
            #         case 3:
            #             self.get_time_auto = True
            #
            #             if II.index_state != "loaded":
            #                 self.swerve.note_aim(0, -0.25 / 2.0, self.limeF.getNumber("tx", 0))
            #                 II.intake()
            #             else:
            #                 self.swerve.drive(0, 0, 0, field_orientation=True)
            #                 self.auto_step += 1
            #         case 4:
            #             II.stop()
            #             if not 25 < self.navx.getYaw() < 35:
            #                 self.swerve.turn_to_face(0, 0, 30)
            #
            #             else:
            #                 Shooter.stop_pivot()
            #                 self.auto_step += 1
            #
            #         case 5:
            #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")
            #
            #             self.swerve.aim_at_target(0, 0, self.limeB.getNumber("tx", 0))
            #             Shooter.set_angle(12)
            #             # if 40 < Shooter.position() < 55:
            #             # Shooter.stop_pivot()
            #
            #             if self.get_time_auto:
            #                 II.stop()
            #                 self.current_time = self.timer.get()
            #                 self.get_time_auto = False
            #             if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 0.5:
            #                 Shooter.set_rpm(4500)  # 3500
            #             if self.timer.get() > self.current_time + .5 and self.timer.get() < self.current_time + 1.0:
            #                 II.feed()
            #             if self.timer.get() > self.current_time + 1.0:
            #                 II.stop()
            #                 Shooter.stop_shooter()
            #                 # self.auto_step += 1

    # case self.left_start:
    #     self.sd.putString("Selected Autonomous:", self.left_start)
    #     match self.auto_step:
    #         case 0:
    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Angle to Shoot from Subwoofer")
    #             Shooter.set_angle(22)
    #
    #             if self.auto_delay < self.timer.get():  # Wait until delay is over
    #                 if self.timer.get() < self.auto_delay + 1.0:
    #                     self.swerve.turn_to_face(0, -.25 / 2.0, -30)
    #
    #                 else:
    #                     Shooter.stop_pivot()
    #                     self.auto_step += 1
    #
    #         case 1:
    #             self.swerve.aim_at_target(0, 0, self.tx_B)
    #
    #             Shooter.set_rpm(4000)
    #
    #             if self.get_time_auto:
    #                 self.current_time = self.timer.get()
    #                 self.get_time_auto = False
    #
    #             if self.timer.get() > self.current_time + 0.5 and self.timer.get() < self.current_time + 1:
    #                 II.feed()
    #
    #             if self.timer.get() > self.current_time + 1.0:
    #                 II.stop()
    #                 Shooter.stop_shooter()
    #                 Shooter.stop_pivot()
    #                 if self.timer.get() > self.current_time + 2.0:
    #                     self.auto_step += 1
    #
    #         case 2:
    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: re-angle")
    #
    #             if not -3 < self.navx.getYaw() < 3:
    #                 self.swerve.turn_to_face(0, 0, 0)
    #
    #             else:
    #                 Shooter.stop_pivot()
    #                 self.auto_step += 1
    #
    #         case 3:
    #             self.get_time_auto = True
    #
    #             if II.index_state != "loaded":
    #                 self.swerve.note_aim(-0.08, -0.25 / 2.0, self.tx_F)  # subject to change?
    #                 II.intake()
    #             else:
    #                 self.swerve.drive(0, 0, 0, field_orientation=True)
    #                 self.auto_step += 1
    #
    #         case 4:
    #             II.stop()
    #             if not 25 < self.navx.getYaw() < 35:
    #                 self.swerve.turn_to_face(0, 0, -30)
    #
    #             else:
    #                 Shooter.stop_pivot()
    #                 self.auto_step += 1
    #
    #         case 5:
    #             self.sd.putString("Autonomous Step:", f" {self.auto_step}: Aim at Speaker")
    #
    #             self.swerve.aim_at_target(0, 0, self.limeB.getNumber("tx", 0))
    #             Shooter.set_angle(12)
    #             # if 40 < Shooter.position() < 55:
    #             # Shooter.stop_pivot()
    #
    #             if self.get_time_auto:
    #                 II.stop()
    #                 self.current_time = self.timer.get()
    #                 self.get_time_auto = False
    #             if self.timer.get() > self.current_time and self.timer.get() < self.current_time + 0.5:
    #                 Shooter.set_rpm(4500)  # 3500
    #             if self.timer.get() > self.current_time + .5 and self.timer.get() < self.current_time + 1.0:
    #                 II.feed()
    #             if self.timer.get() > self.current_time + 1.0:
    #                 II.stop()
    #                 Shooter.stop_shooter()
    #                 # self.auto_step += 1


