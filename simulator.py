# Cadet Hayden Rose CIS-302 OS Project
# Main Simulator Module
# This module simulates process memory management using page tables and frame tables.

from modules.frame import initialize_frame_table, display_frame_table
from modules.process import Process
   


def main():
    # Initialize Frame Table with 16 frames
    initialize_frame_table(16)

    # Display initial Frame Table
    display_frame_table()

    
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

if __name__ == "__main__":
    main()
