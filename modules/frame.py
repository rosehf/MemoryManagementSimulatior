# Cadet Hayden Rose CIS-302 OS Project
# Frame Module
# This module defines the Frame class and manages the Frame Table.


# Create Frame class to represent a memory frame
class Frame:
    def __init__(self, frame_no, is_free, process_id, virtual_page_no):
        self.frame_no = frame_no
        self.is_free = is_free
        self.process_id = process_id
        self.virtual_page_no = virtual_page_no
        self.dirty_bit = 0  # Initialize dirty bit to 0 (not modified from disk)

    def display(self):
        print(f'Frame No: {self.frame_no}, Is Free: {self.is_free}, Process ID: {self.process_id}, Virtual Page No: {self.virtual_page_no}, Dirty Bit: {self.dirty_bit}')


# Global Frame Table
def initialize_frame_table(num_frames):
    global FrameTable
    FrameTable = []
    for i in range(num_frames):
        frame = Frame(frame_no=i, is_free=True, process_id=-1, virtual_page_no=-1)
        FrameTable.append(frame)


# Function to display the current state of the Frame Table
def display_frame_table():
    print("Frame Table:")
    for frame in FrameTable:
        frame.display()

