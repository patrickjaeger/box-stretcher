import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from box_stretcher_motor import Motor, Status


class ColorLED(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.diameter = 15
        
        self.led = ttk.Canvas(self, height=self.diameter, width=self.diameter)
        self.led.pack()
        self.set_color()

    def set_color(self, color="red"): 
        self.led.create_oval(0, 0, self.diameter, self.diameter, fill=color)


class Protocol:
    def __init__(self):
        self.L0 = None
        self.STRAIN = None
        self.STRAIN_RATE = None
        self.CYCLES = None


class SetupFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motor):
        super().__init__(master, text="Setup", padding=(5, 5))

        self.port_var = ttk.StringVar(value="COM7")
        self.port_ent = ttk.Entry(self, textvariable=self.port_var, width=6)
        # self.port_ent.configure(validate="key", validatecommand=(self.register(self.validator), "%P",))
        self.port_ent.grid(row=0, column=0, padx=5, pady=2)

        self.connect_btn = ttk.Button(self, text="Connect", command=self.on_connect_click)
        self.connect_btn.grid(row=0, column=1, padx=5, pady=2, sticky=EW)

        self.connect_led = ColorLED(self)
        self.connect_led.grid(row=0, column=2, padx=5, pady=2)

        self.home_btn = ttk.Button(self, text="Home motor", state="disabled", command=self.on_home_click)
        self.home_btn.grid(row=1, column=1, padx=5, pady=2, sticky=EW)

        self.home_led = ColorLED(self)
        self.home_led.grid(row=1, column=2, padx=5, pady=2)

        self.top_button = ttk.Button(self, text="Pin", state="enabled", command=self.on_top_click)
        self.top_button.grid(row=2, column=1, padx=5, pady=2, sticky=EW)

        self.connection_state = "naive"
        self.connection = None
        self.home_state = "naive"
        self.device1 = None
        self.device2 = None

        self.master = master
        self.on_top = False

        self.motors = motors

    def on_connect_click(self):
        if self.connection_state == "naive":
            try:
                self.motors.connect(self.port_var.get())
            except Exception as e:
                print(e)
            else:
                self.connection_state = "connected"
                self.connect_btn.configure(bootstyle="danger", text="Disconnect")
                self.connect_led.set_color("green")
                self.home_btn.configure(state="enabled")
        elif self.connection_state == "connected":
            try:
                self.motors.disconnect()
            except:
                return
            else:
                self.connection_state = "naive"
                self.connect_btn.configure(bootstyle="default", text="Connect")
                self.connect_led.set_color("red")
                self.home_led.set_color("red")

    def on_home_click(self):
        try:
            self.motors.home()
            self.home_led.set_color("yellow")
        except Exception as e:
            print(e)
        else:
            self.home_btn.configure(state="disabled")
            self.home_state = "homed"
            self.home_led.set_color("green")

    def on_top_click(self):
        if self.on_top:
            self.on_top = False
            self.master.wm_attributes("-topmost", False)
            self.master.update()
            self.top_button.configure(text="Pin")
        else:
            self.on_top = True
            self.master.wm_attributes("-topmost", True)
            self.master.update()
            self.top_button.configure(text="Unpin")

    def callback(self):
        print(self.port_var.get())


class ManualMove(ttk.Labelframe):
    def __init__(self, master, motors: Motor, protocol: Protocol):
        super().__init__(master, text="Manual move", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1, minsize=120)
        self.columnconfigure(1, weight=1)

        self.length_var = ttk.StringVar()
        self.length_var.set("10")
        self.speed_var = ttk.StringVar()
        self.speed_var.set("10")

        self.length_lbl = ttk.Label(self, text="Length [mm]")
        self.length_lbl.grid(row=0, column=0, sticky=E)
        self.length_ent = ttk.Entry(self, textvariable=self.length_var, width=6, justify="right")
        self.length_ent.grid(row=0, column=1, padx=5, pady=2, sticky=EW)

        self.speed_lbl = ttk.Label(self, text="Speed [mm/s]")
        self.speed_lbl.grid(row=1, column=0, sticky=E)
        self.speed_ent = ttk.Entry(self, textvariable=self.speed_var, width=6, justify="right")
        self.speed_ent.grid(row=1, column=1, padx=5, pady=2, sticky=EW)

        self.move_btn = ttk.Button(self, text="Move", command=self.on_move_click)
        self.move_btn.grid(row=3, column=1, padx=5, pady=5, sticky=EW)

        self.motors = motors
        self.protocol = protocol

    def on_move_click(self):
        try:
            self.motors.move_absolute_distance(float(self.length_var.get()), float(self.speed_var.get()))
            # self.protocol.L0 = self.length_var
        except Exception as e:
            print(e)

    

class ProtocolFrame(ttk.Labelframe):
    def __init__(self, master: Motor, protocol: Protocol):
        super().__init__(master, text="Protocol", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1, minsize=120)
        self.columnconfigure(1, weight=1)

        self.len_zero_var = ttk.StringVar()
        self.len_zero_var.set("28.5")
        self.strain_var = ttk.StringVar()
        self.strain_var.set("18")
        self.strain_rate_var = ttk.StringVar()
        self.strain_rate_var.set("5")
        self.cycles_var = ttk.StringVar()
        self.cycles_var.set("1000")

        self.len_zero_lab = ttk.Label(self, text="L0 [mm]")
        self.len_zero_lab.grid(row=0, column=0, sticky=E)
        self.len_zero_ent = ttk.Entry(self, textvariable=self.len_zero_var, width=6, justify="right")
        self.len_zero_ent.grid(row=0, column=1, padx=5, pady=2, sticky=E)

        self.strain_lab = ttk.Label(self, text="Strain [%]")
        self.strain_lab.grid(row=1, column=0, sticky=E)
        self.strain_ent = ttk.Entry(self, textvariable=self.strain_var, width=6, justify="right")
        self.strain_ent.grid(row=1, column=1, padx=5, pady=2, sticky=E)

        self.strain_rate_lab = ttk.Label(self, text="Strain rate [%/s]")
        self.strain_rate_lab.grid(row=2, column=0, sticky=E)
        self.strain_rate_ent = ttk.Entry(self, textvariable=self.strain_rate_var, width=6, justify="right")
        self.strain_rate_ent.grid(row=2, column=1, padx=5, pady=2, sticky=E)

        self.cycles_lab = ttk.Label(self, text="Cycles [n]")
        self.cycles_lab.grid(row=3, column=0, sticky=E)
        self.cycles_ent = ttk.Entry(self, textvariable=self.cycles_var, width=6, justify="right")
        self.cycles_ent.grid(row=3, column=1, padx=5, pady=2, sticky=E)

        protocol.L0 = self.len_zero_var
        protocol.STRAIN = self.strain_var
        protocol.STRAIN_RATE = self.strain_rate_var
        protocol.CYCLES = self.cycles_var


class ControlsFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motor, protocol: Protocol, status: Status):
        super().__init__(master, text="Controls", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1)
        # self.columnconfigure(0, weight=1)

        self.run_btn = ttk.Button(self, text="Run protocol", bootstyle="warning", state="enabled",  command=self.on_run_click)
        self.run_btn.grid(row=0, column=0, padx=5, pady=5, sticky=EW)

        #self.goto_zero_btn = ttk.Button(self, text="Go to L0", bootstyle="default", command=self.on_goto_zero_click)
        #self.goto_zero_btn.grid(row=0, column=1, padx=5, pady=5, sticky=EW)

        # self.trigger_btn = ttk.Button(self, text="Run ", bootstyle="warning", command=self.on_trigger_click)
        # self.trigger_btn.grid(row=1, column=0, padx=5, pady=5, sticky=EW)

        self.stop_btn = ttk.Button(self, text="STOP", bootstyle="danger", command=self.on_stop_click)
        self.stop_btn.grid(row=1, column=0, padx=5, pady=5, sticky=EW)

        self.motors = motors
        self.protocol = protocol
        self.status = status
        self.check_status_loop()

        self.cycle_thread = None

    # def on_goto_zero_click(self):
    #     try:
    #         self.motors.move_absolute_distance(float(self.protocol.L0.get()), 5)
    #     except Exception as e:
    #         print(e)

    def on_run_click(self):
        self.cycle_thread = threading.Thread(target=self.run_click_thread)
        self.cycle_thread.start()

    def run_click_thread(self):
        try:
            self.status.set_running()
            self.motors.move_cyclical(float(self.protocol.L0.get()), 
                                      float(self.protocol.STRAIN.get()),
                                      float(self.protocol.STRAIN_RATE.get()),
                                      int(self.protocol.CYCLES.get()),
                                      self.status)
        except Exception as e:
            print(e)
        
        self.status.reset_status()
        

    def on_stop_click(self):
        try:
            self.motors.stop()
            self.status.reset_status()
        except Exception as e:
            print(e)

        # self.run_btn.configure(state="enabled")

    def check_status_loop(self):
        # Update the button state based on motor status
        if self.status.state == "idle":
            self.run_btn.configure(state="enabled")
        else:
            self.run_btn.configure(state="disabled")

        # Schedule the next check in 500 ms
        self.after(500, self.check_status_loop)




class StatusFrame(ttk.Labelframe):
    def __init__(self, master, motors: Motor, protocol: Protocol, status: Status):
        super().__init__(master, text="Status", padding=(5, 5))
        # self.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.status_lbl = ttk.Label(self, text="Status:")
        self.status_lbl.grid(row=0, column=0, padx=5, pady=2, sticky=E)
        self.status_out = ttk.Label(self, text="idle")
        self.status_out.grid(row=0, column=1, padx=5, pady=2, sticky=W)

        self.clen_lbl = ttk.Label(self, text="Cycle:")
        self.clen_lbl.grid(row=1, column=0, padx=5, pady=2, sticky=E)
        self.clen_out = ttk.Label(self, text="-")
        self.clen_out.grid(row=1, column=1, padx=5, pady=2, sticky=W)

        self.rem_lbl = ttk.Label(self, text="Time remaining:")
        self.rem_lbl.grid(row=2, column=0, padx=5, pady=2, sticky=E)
        self.rem_out = ttk.Label(self, text="-", width=10)
        self.rem_out.grid(row=2, column=1, padx=5, pady=2, sticky=W)

        self.motors = motors
        self.status = status
        self.protocol = protocol

        self.display_values()
    
    # TODO write function here that is called in motors to update the status;
    # or restructure to MVC architecture
    def show_cycle(self):
        self.clen_out["text"] = self.status.N_CYCLES
        

    def display_values(self):
        if self.motors.connected:
            self.motor_status = self.motors.axis.is_busy()
            if self.motor_status:
                self.status_out["text"] = "running"
                self.status.T_REMAINING_SEC = (float(self.protocol.STRAIN.get()) / float(self.protocol.STRAIN_RATE.get())) * (int(self.protocol.CYCLES.get()) - int(self.status.N_CYCLES)) * 2
                self.rem_out["text"] = f"{round(self.status.T_REMAINING_SEC / 60, 1)} min"
            else:
                self.status_out["text"] = "idle"
                self.rem_out["text"] = f"{round(self.status.T_REMAINING_SEC / 60, 1)} min"
            self.show_cycle()
        self.after(100, self.display_values)