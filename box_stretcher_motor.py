import os
from pathlib import Path
from zaber_motion import Units, Library
from zaber_motion.ascii import Connection

class Status:
    def __init__(self):
        self.state = "idle"
        self.N_CYCLES = 0
        self.T_REMAINING_SEC = 0

    def reset_status(self):
        self.state = "idle"
        self.N_CYCLES = 0
        self.T_REMAINING_SEC = 0

    def set_running(self):
        self.state = "running"

    def set_idle(self):
        self.state = "idle"
        


class Motor:
    DEFAULT_SPEED = 10  # [mm/s] actuator_default: 18.6
    DEFAULT_LENGTH_UNIT = Units.LENGTH_MILLIMETRES
    DEFAULT_SPEED_UNIT = Units.VELOCITY_MILLIMETRES_PER_SECOND

    def __init__(self):
        db_path = Path(os.path.dirname(__file__)).joinpath("zaber_device_db")
        Library.enable_device_db_store(str(db_path))
        self.connected = False

    def connect(self, port):
        self.connection = Connection.open_serial_port(port)
        try:
            self.device_list = self.connection.detect_devices()
            self.device = self.device_list[0]
            self.axis = self.device.get_axis(1)
            self.connected = True
        except Exception as e:
            self.connection.close()
            raise e

    def disconnect(self):
        self.connected = False
        self.connection.close()

    def stop(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        # self.device.all_axes.stop(wait_until_idle=False)
        self.axis.stop(wait_until_idle=False)

    def home(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.axis.settings.set("maxspeed", self.DEFAULT_SPEED, self.DEFAULT_SPEED_UNIT)
        self.axis.home()

    def move_absolute_distance(self, length, speed):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.axis.settings.set("maxspeed", speed, self.DEFAULT_SPEED_UNIT)

        self.axis.move_absolute(length, self.DEFAULT_LENGTH_UNIT)

    def move_relative_distance(self, length, speed):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        self.axis.settings.set("maxspeed", speed, self.DEFAULT_SPEED_UNIT)

        self.axis.move_relative(length, self.DEFAULT_LENGTH_UNIT)

    # def move_absolute_distance(self, pos, speed):
    #     if not self.connected:
    #         raise ConnectionError("Motors must be connected first.")
    #     self.device1.settings.set(BinarySettings.TARGET_SPEED, speed / 2, Units.VELOCITY_MILLIMETRES_PER_SECOND)

    #     position = self.ZERO_POSITION - self.mm_to_data((pos - 12) / 2)
    #     self.device1.generic_command_no_response(CommandCode.MOVE_ABSOLUTE, position)

    def get_position(self):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
        return self.axis.get_position(self.DEFAULT_LENGTH_UNIT)

    def move_cyclical(self, L0, strain, strain_rate, cycles, status: Status):
        if not self.connected:
            raise ConnectionError("Motors must be connected first.")
            
        self.absolute_distance = abs(L0 - L0 * (100 + strain)/100)
        self.speed = self.absolute_distance/(strain/strain_rate)
        self.axis.settings.set("maxspeed", self.speed, self.DEFAULT_SPEED_UNIT)
        
        self.starting_length = self.axis.get_position(self.DEFAULT_LENGTH_UNIT)
        self.final_length = self.starting_length - self.absolute_distance
        
        for n in range(cycles):
            self.axis.move_absolute(self.final_length, self.DEFAULT_LENGTH_UNIT)
            self.axis.move_absolute(self.starting_length, self.DEFAULT_LENGTH_UNIT)
            status.N_CYCLES += 1
