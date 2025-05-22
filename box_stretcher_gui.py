import os
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import * # type: ignore


from box_stretcher_ui  import ColorLED, SetupFrame, ManualMove, Protocol, ProtocolFrame, ControlsFrame, StatusFrame
from box_stretcher_motor import Motor, Status


class GUI:
    def __init__(self, master: ttk.Window):
        self.master = master

        self.tabControl = ttk.Notebook(self.master)

        self.tabs = []
        self.tab_idx = 0

        self.motor_list = []
        self.protocol_list = []
        self.status_list = []

        self.init_tab()

        self.add_tab_button = ttk.Button(self.master, text="Add Motor", command=self.add_new_tab)
        self.add_tab_button.pack(pady=10)

    def init_tab(self):
        self.tabs.append(ttk.Frame(self.tabControl))

        self.motor_list.append(Motor())
        self.protocol_list.append(Protocol())
        self.status_list.append(Status())

        SetupFrame(self.tabs[self.tab_idx], self.motor_list[self.tab_idx]).grid(row=0, column=0, sticky=NSEW, padx=5, pady=2)
        ManualMove(self.tabs[self.tab_idx], self.motor_list[self.tab_idx], self.protocol_list[self.tab_idx]).grid(row=0, column=1, sticky=NSEW, padx=5, pady=2)
        ProtocolFrame(self.tabs[self.tab_idx], self.protocol_list[self.tab_idx]).grid(row=1, column=0, rowspan=2, sticky=NSEW, padx=5, pady=2)
        ControlsFrame(self.tabs[self.tab_idx], self.motor_list[self.tab_idx], self.protocol_list[self.tab_idx], self.status_list[self.tab_idx]).grid(row=1, column=1, sticky=NSEW, padx=5, pady=2)
        StatusFrame(self.tabs[self.tab_idx], self.motor_list[self.tab_idx], self.protocol_list[self.tab_idx], self.status_list[self.tab_idx]).grid(row=2, column=1, sticky=NSEW, padx=5, pady=2)

        self.tabControl.add(self.tabs[self.tab_idx], text=f"Motor {self.tab_idx+1}")
        self.tabControl.pack(expand=1, fill="both")

        self.tab_idx += 1

    def add_new_tab(self):
        self.init_tab()

if __name__ == "__main__":
    root = ttk.Window("box go brrrrr", "darkly", resizable=(False, False), iconphoto="icons/banana2.png")
    app = GUI(root)
    root.mainloop()