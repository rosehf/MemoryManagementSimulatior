# IMPORTANT THIS FILE IS AI GENERATED SOLELY FOR THE PURPOSE OF BETTER VISUALIZING THE SIMULATION.
# ALL LOGIC AND FUNCTIONALITY IN CLI VERSION WAS WRITTEN BY CADETS AND PROVIDED TO THE AI FOR GUI IMPLEMENTATION.

 
import threading
from time import sleep
from queue import Queue
from modules.frame import initialize_frame_table, display_frame_table
from modules import frame
from modules.process import Process
from gui import SimulatorGUI  # Import the GUI class

# Global variables
simulation_running = True
msg_queue = Queue()  # Thread-safe message queue

def main():
    global simulation_running

    simulation_running = True

    # Initialize Frame Table
    frame_size = 4  # MB per frame
    total_frames = 16
    initialize_frame_table(total_frames)

    # Display initial Frame Table
    display_frame_table()

    # --- Process Creation ---
    process1 = Process(pid=1)
    process2 = Process(pid=2)

    # Add pages to Process 1
    for vpn in range(4):
        process1.page_table.add_page(virtual_page_no=vpn, is_valid=False, frame_no=-1)

    # Add pages to Process 2
    for vpn in range(4):
        process2.page_table.add_page(virtual_page_no=vpn, is_valid=False, frame_no=-1)

    # --- Start GUI ---
    import tkinter as tk
    root = tk.Tk()
    gui = SimulatorGUI(root, frame_table=frame.FrameTable, msg_queue=msg_queue)

    # --- Start Memory Monitor Thread ---
    monitor_thread = threading.Thread(target=memory_monitor, args=(frame_size, total_frames), daemon=True)
    monitor_thread.start()

    # --- Start Process Simulation Threads ---
    t1 = threading.Thread(target=simulate_process, args=(process1,), daemon=True)
    t2 = threading.Thread(target=simulate_process, args=(process2,), daemon=True)
    t1.start()
    t2.start()

    # --- Launch GUI Main Loop ---
    root.mainloop()
    simulation_running = False


def memory_monitor(frame_size, total_frames):
    while simulation_running:
        used_frames = sum(1 for f in frame.FrameTable if not f.is_free)
        free_frames = total_frames - used_frames
        percent_used = (used_frames / total_frames) * 100 if total_frames else 0
        msg_queue.put(f"[Memory Monitor] {used_frames * frame_size}MB / {total_frames * frame_size}MB used ({percent_used:.1f}%)")
        sleep(1)


def simulate_process(process):
    """Simulate process loading pages and accessing memory."""
    # Example sequence (can expand or randomize later)
    for vpn in process.page_table.pages.keys():
        page = process.page_table.lookup_page(vpn)
        if not page.is_valid:
            # Find a free frame
            free_frame = next((f for f in frame.FrameTable if f.is_free), None)
            if free_frame:
                process.load_page(virtual_page_no=vpn, frame_no=free_frame.frame_no)
                free_frame.is_free = False
                free_frame.process_id = process.pid
                msg_queue.put(f"[Process {process.pid}] Loaded virtual page {vpn} into frame {free_frame.frame_no}")
            else:
                # Page fault handling: evict first frame
                victim = frame.FrameTable[0]
                msg_queue.put(f"[Process {process.pid}] Page fault! Evicting frame {victim.frame_no} (P{victim.process_id})")
                victim.process_id = process.pid
                process.load_page(virtual_page_no=vpn, frame_no=victim.frame_no)

        # Access the page
        process.access_page(vpn)
        sleep(1)  # Delay for visualization


if __name__ == "__main__":
    main()
