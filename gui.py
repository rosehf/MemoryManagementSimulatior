# IMPORTANT: THIS FILE IS AI GENERATED SOLELY FOR THE PURPOSE OF BETTER VISUALIZING THE SIMULATION.

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class SimulatorGUI:
    def __init__(self, root, frame_table, msg_queue, update_interval=500):
        self.root = root
        self.frame_table = frame_table
        self.msg_queue = msg_queue
        self.update_interval = update_interval  # milliseconds

        root.title("OS Simulator GUI")

        # --- Left Panel: Process Logs ---
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(self.left_frame, text="Process Activity").pack()
        self.log_box = ScrolledText(self.left_frame, height=20, width=50, state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=True)

        # --- Right Panel: Memory Monitor ---
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(self.right_frame, text="Memory Monitor").pack()
        self.memory_progress = ttk.Progressbar(self.right_frame, length=200, mode='determinate')
        self.memory_progress.pack(pady=5)
        self.frame_table_box = ScrolledText(self.right_frame, height=20, width=30, state=tk.DISABLED)
        self.frame_table_box.pack(fill=tk.BOTH, expand=True)

        # Start GUI update loop
        self.update_gui()

    def update_gui(self):
        # Process messages from queue
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            self.log_box.configure(state=tk.NORMAL)
            self.log_box.insert(tk.END, msg + "\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state=tk.DISABLED)

        # Update memory progress
        total_frames = len(self.frame_table)
        used_frames = sum(1 for f in self.frame_table if not f.is_free)
        percent_used = int((used_frames / total_frames) * 100) if total_frames > 0 else 0
        self.memory_progress['value'] = percent_used

        # Update frame table display
        self.frame_table_box.configure(state=tk.NORMAL)
        self.frame_table_box.delete(1.0, tk.END)
        for f in self.frame_table:
            status = f"Frame {f.frame_no}: "
            status += "Free" if f.is_free else f"Occupied by P{f.process_id}"
            self.frame_table_box.insert(tk.END, status + "\n")
        self.frame_table_box.configure(state=tk.DISABLED)

        # Schedule next update
        self.root.after(self.update_interval, self.update_gui)