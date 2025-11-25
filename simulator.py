# Cadet Hayden Rose CIS-302 OS Project
# Main Simulator Module
# This module simulates process memory management using page tables and frame tables.

# Import notes:
#  - each frame has an arbirary value of 4MB for the purpose of this simulation

# TODO: implement random process creation and page accesses. (USE AI??)

import threading
from time import sleep
from modules.frame import initialize_frame_table, display_frame_table
from modules.process import Process
from modules import frame
   


def main():
    global simulation_running
    simulation_running = True

    # Initialize Frame Table with 'total_frames'  of 'frame_size' size frames
    frame_size = 4  # in MB
    total_frames = 16
    initialize_frame_table(total_frames)

    # Display initial Frame Table
    display_frame_table()

    monitor_thread = threading.Thread(target=memory_monitor, args=(frame_size, total_frames))
    monitor_thread.start()

    # Process Creation
    process1 = Process(pid=1)
    process2 = Process(pid=2)

    # Add pages to Process 1's Page Table
    for vpn in range(4):
        process1.page_table.add_page(virtual_page_no=vpn, is_valid=False, frame_no=-1)

    # Add pages to Process 2's Page Table
    for vpn in range(4):
        process2.page_table.add_page(virtual_page_no=vpn, is_valid=False, frame_no=-1)

    # Simulate Process 1 loading pages
    print("\nSimulating Process 1:")
    process1.load_page(virtual_page_no=0, frame_no=0)
    process1.load_page(virtual_page_no=1, frame_no=1)
    process1.access_page(virtual_page_no=0)
    process1.access_page(virtual_page_no=2)  
    process1.mark_page_dirty(virtual_page_no=1) 
    process1.load_page(virtual_page_no=2, frame_no=2)

    # Simulate Process 2 loading pages
    print("\nSimulating Process 2:")
    process2.load_page(virtual_page_no=0, frame_no=3)
    process2.access_page(virtual_page_no=0)
    process2.access_page(virtual_page_no=1)  
    process2.load_page(virtual_page_no=1, frame_no=4)

    print("\nFinal State of Frame Table:")
    display_frame_table()



def memory_monitor(frame_size, total_frames):
    while simulation_running:
        used_frames = sum(1 for f in frame.FrameTable if not f.is_free)
        free_frames = total_frames - used_frames
        percent_used = (used_frames / total_frames) * 100 if total_frames else 0
        print(f"Memory: {used_frames * frame_size}MB / {total_frames * frame_size}MB used ({percent_used}%)")
        sleep(1)  # wait 1 second before updating

if __name__ == "__main__":
    main()
