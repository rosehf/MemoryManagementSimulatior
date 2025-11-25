"""
Memory Management Simulator with Dynamic Process Creation/Deletion
CIS-302 OS Project - Final Version (Claude)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
from time import sleep
from queue import Queue
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent))

from modules.frame import initialize_frame_table
from modules.process import Process
import modules.frame as frame_module

# Global variables
simulation_running = True
simulation_paused = False
msg_queue = Queue()
process_lock = threading.Lock()
active_processes = {}  # {pid: Process}
next_pid = 1


class MemorySimulatorGUI:
    def __init__(self, root, frame_size=4, total_frames=16):
        self.root = root
        self.frame_size = frame_size
        self.total_frames = total_frames
        
        root.title("Dynamic Memory Management Simulator")
        root.geometry("1200x700")
        
        # Initialize frame table
        initialize_frame_table(total_frames)
        
        # Create main layout
        self.create_layout()
        
        # Start background threads
        self.start_background_threads()
        
        # Start GUI update loop
        self.update_gui()
    
    def create_layout(self):
        # Top Control Panel
        control_frame = tk.Frame(self.root, bg='lightgray', padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(control_frame, text="Process Controls:", font=('Arial', 10, 'bold'), bg='lightgray').pack(side=tk.LEFT, padx=5)
        
        # Create Process Button
        tk.Button(control_frame, text="Create Process", command=self.create_process_dialog, 
                 bg='green', fg='white', padx=10).pack(side=tk.LEFT, padx=5)
        
        # Delete Process Button
        tk.Button(control_frame, text="Delete Process", command=self.delete_process_dialog,
                 bg='red', fg='white', padx=10).pack(side=tk.LEFT, padx=5)
        
        # Pause/Resume Button
        self.pause_button = tk.Button(control_frame, text="Pause Simulation", 
                                      command=self.toggle_pause, bg='orange', fg='white', padx=10)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Clear Logs Button
        tk.Button(control_frame, text="Clear Logs", command=self.clear_logs,
                 bg='gray', fg='white', padx=10).pack(side=tk.LEFT, padx=5)
        
        # Reset Button
        tk.Button(control_frame, text="Reset Simulation", command=self.reset_simulation,
                 bg='darkred', fg='white', padx=10).pack(side=tk.LEFT, padx=5)
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel: Process List and Activity Logs
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Active Processes Section
        tk.Label(left_frame, text="Active Processes", font=('Arial', 10, 'bold')).pack()
        self.process_listbox = tk.Listbox(left_frame, height=8)
        self.process_listbox.pack(fill=tk.X, pady=(0, 10))
        
        # Process Activity Log
        tk.Label(left_frame, text="Process Activity Log", font=('Arial', 10, 'bold')).pack()
        self.log_box = ScrolledText(left_frame, height=20, width=60, state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel: Memory Monitor
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Memory Statistics
        tk.Label(right_frame, text="Memory Monitor", font=('Arial', 10, 'bold')).pack()
        
        stats_frame = tk.Frame(right_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.memory_label = tk.Label(stats_frame, text="Memory Usage: 0%", font=('Arial', 9))
        self.memory_label.pack()
        
        self.memory_progress = ttk.Progressbar(stats_frame, length=300, mode='determinate')
        self.memory_progress.pack(pady=5)
        
        # Frame Table Display
        tk.Label(right_frame, text="Frame Table", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        self.frame_table_box = ScrolledText(right_frame, height=25, width=40, state=tk.DISABLED)
        self.frame_table_box.pack(fill=tk.BOTH, expand=True)
    
    def create_process_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Process")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Number of Pages:", font=('Arial', 10)).pack(pady=10)
        
        page_count = tk.IntVar(value=4)
        spinbox = tk.Spinbox(dialog, from_=1, to=16, textvariable=page_count, width=10)
        spinbox.pack(pady=5)
        
        def create():
            pages = page_count.get()
            self.create_process(pages)
            dialog.destroy()
        
        tk.Button(dialog, text="Create", command=create, bg='green', fg='white', padx=20).pack(pady=20)
    
    def create_process(self, num_pages):
        global next_pid
        
        with process_lock:
            pid = next_pid
            next_pid += 1
            
            # Create new process
            process = Process(pid=pid)
            
            # Add pages to the process
            for vpn in range(num_pages):
                process.page_table.add_page(virtual_page_no=vpn, is_valid=False, frame_no=-1)
            
            active_processes[pid] = process
            msg_queue.put(f"[System] Created Process {pid} with {num_pages} pages")
            
            # Start a thread to simulate this process
            thread = threading.Thread(target=self.simulate_process, args=(process,), daemon=True)
            thread.start()
    
    def delete_process_dialog(self):
        if not active_processes:
            messagebox.showinfo("No Processes", "No active processes to delete")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Process")
        dialog.geometry("300x250")
        
        tk.Label(dialog, text="Select Process to Delete:", font=('Arial', 10)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=6)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        for pid in active_processes.keys():
            listbox.insert(tk.END, f"Process {pid}")
        
        def delete():
            selection = listbox.curselection()
            if selection:
                pid = list(active_processes.keys())[selection[0]]
                self.delete_process(pid)
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a process")
        
        def cancel():
            dialog.destroy()
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Delete Selected", command=delete, 
                 bg='red', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel, 
                 bg='gray', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
    
    def delete_process(self, pid):
        with process_lock:
            if pid in active_processes:
                process = active_processes[pid]
                
                # Free all frames occupied by this process
                for frame_obj in frame_module.FrameTable:
                    if frame_obj.process_id == pid:
                        frame_obj.is_free = True
                        frame_obj.process_id = None
                        msg_queue.put(f"[System] Freed frame {frame_obj.frame_no} from Process {pid}")
                
                # Remove process
                del active_processes[pid]
                msg_queue.put(f"[System] Deleted Process {pid}")
    
    def toggle_pause(self):
        global simulation_paused
        simulation_paused = not simulation_paused
        
        if simulation_paused:
            self.pause_button.config(text="Resume Simulation")
            msg_queue.put("[System] Simulation PAUSED")
        else:
            self.pause_button.config(text="Pause Simulation")
            msg_queue.put("[System] Simulation RESUMED")
    
    def clear_logs(self):
        self.log_box.configure(state=tk.NORMAL)
        self.log_box.delete(1.0, tk.END)
        self.log_box.configure(state=tk.DISABLED)
    
    def reset_simulation(self):
        """Reset the entire simulation to initial state"""
        global next_pid, simulation_paused
        
        # Confirm reset
        if not messagebox.askyesno("Reset Simulation", 
                                   "Are you sure you want to reset? All processes will be deleted."):
            return
        
        # Delete all processes
        with process_lock:
            # Copy the list of PIDs to avoid modification during iteration
            pids_to_delete = list(active_processes.keys())
            
            # Clear the active processes dict first to stop simulation threads
            active_processes.clear()
            
            # Reset frame table
            for frame_obj in frame_module.FrameTable:
                frame_obj.is_free = True
                frame_obj.process_id = -1
                frame_obj.virtual_page_no = -1
                frame_obj.dirty_bit = 0
            
            # Reset PID counter
            next_pid = 1
            
            # Unpause if paused
            if simulation_paused:
                simulation_paused = False
                self.pause_button.config(text="Pause Simulation")
        
        # Clear logs
        self.clear_logs()
        msg_queue.put("[System] Simulation RESET - All processes deleted, memory cleared")
        
        messagebox.showinfo("Reset Complete", "Simulation has been reset to initial state")
    
    def simulate_process(self, process):
        """Simulate process loading and accessing pages"""
        while simulation_running and process.pid in active_processes:
            if simulation_paused:
                sleep(0.5)
                continue
            
            with process_lock:
                if process.pid not in active_processes:
                    break
                
                # Try to load unloaded pages
                for vpn in process.page_table.pages.keys():
                    page = process.page_table.lookup_page(vpn)
                    
                    if not page.is_valid:
                        # Find a free frame
                        free_frame = next((f for f in frame_module.FrameTable if f.is_free), None)
                        
                        if free_frame:
                            process.load_page(virtual_page_no=vpn, frame_no=free_frame.frame_no)
                            free_frame.is_free = False
                            free_frame.process_id = process.pid
                            msg_queue.put(f"[Process {process.pid}] Loaded page {vpn} into frame {free_frame.frame_no}")
                        else:
                            # Page fault - evict a frame (simple FIFO for now)
                            occupied_frames = [f for f in frame_module.FrameTable if not f.is_free]
                            if occupied_frames:
                                victim = occupied_frames[0]
                                msg_queue.put(f"[Process {process.pid}] Page fault! Evicting frame {victim.frame_no} (P{victim.process_id})")
                                victim.process_id = process.pid
                                process.load_page(virtual_page_no=vpn, frame_no=victim.frame_no)
                    else:
                        # Access already loaded page
                        process.access_page(vpn)
            
            sleep(2)  # Delay between operations
    
    def start_background_threads(self):
        # Memory monitor thread
        monitor_thread = threading.Thread(target=self.memory_monitor, daemon=True)
        monitor_thread.start()
    
    def memory_monitor(self):
        while simulation_running:
            if not simulation_paused:
                used_frames = sum(1 for f in frame_module.FrameTable if not f.is_free)
                percent_used = (used_frames / self.total_frames) * 100 if self.total_frames else 0
                msg_queue.put(f"[Monitor] {used_frames * self.frame_size}MB / {self.total_frames * self.frame_size}MB used ({percent_used:.1f}%)")
            sleep(2)
    
    def update_gui(self):
        # Process messages from queue
        while not msg_queue.empty():
            msg = msg_queue.get()
            self.log_box.configure(state=tk.NORMAL)
            self.log_box.insert(tk.END, msg + "\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state=tk.DISABLED)
        
        # Update active processes list
        self.process_listbox.delete(0, tk.END)
        with process_lock:
            for pid, process in active_processes.items():
                loaded_pages = sum(1 for p in process.page_table.pages.values() if p.is_valid)
                total_pages = len(process.page_table.pages)
                self.process_listbox.insert(tk.END, f"Process {pid}: {loaded_pages}/{total_pages} pages loaded")
        
        # Update memory progress bar and label
        used_frames = sum(1 for f in frame_module.FrameTable if not f.is_free)
        percent_used = int((used_frames / self.total_frames) * 100) if self.total_frames > 0 else 0
        self.memory_progress['value'] = percent_used
        self.memory_label.config(text=f"Memory Usage: {used_frames}/{self.total_frames} frames ({percent_used}%)")
        
        # Update frame table display
        self.frame_table_box.configure(state=tk.NORMAL)
        self.frame_table_box.delete(1.0, tk.END)
        for f in frame_module.FrameTable:
            status = f"Frame {f.frame_no:2d}: "
            if f.is_free:
                status += "[ FREE ]"
            else:
                status += f"[P{f.process_id}]"
            self.frame_table_box.insert(tk.END, status + "\n")
        self.frame_table_box.configure(state=tk.DISABLED)
        
        # Schedule next update
        self.root.after(500, self.update_gui)


def main():
    global simulation_running
    
    root = tk.Tk()
    app = MemorySimulatorGUI(root, frame_size=4, total_frames=16)
    
    # Handle window close
    def on_closing():
        global simulation_running
        simulation_running = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()