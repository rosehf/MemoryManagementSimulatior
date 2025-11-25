# Cadet Hayden Rose CIS-302 OS Project
# Process Module
# This module defines the Process class which manages its own Page Table.

from modules.page import PageTable
from modules import frame

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.page_table = PageTable(process_id=self.pid)

    def access_page(self, virtual_page_no):
        page = self.page_table.lookup_page(virtual_page_no)
        if page and page.is_valid:
            print(f'Process {self.pid} accessed virtual page {virtual_page_no} in frame {page.frame_no}.')
        else:
            print(f'Process {self.pid} page fault on virtual page {virtual_page_no}.')

    def load_page(self, virtual_page_no, frame_no):
        self.page_table.mark_valid(virtual_page_no, frame_no)
        # Update the frame table
        frame_obj = frame.FrameTable[frame_no]
        frame_obj.is_free = False
        frame_obj.process_id = self.pid
        frame_obj.virtual_page_no = virtual_page_no
        print(f'Process {self.pid} loaded virtual page {virtual_page_no} into frame {frame_no}.')

    def mark_page_dirty(self, virtual_page_no):
        self.page_table.mark_dirty(virtual_page_no)
        page = self.page_table.lookup_page(virtual_page_no)
        if page and page.is_valid:
            # Update the frame table's dirty bit
            frame_obj = frame.FrameTable[page.frame_no]
            frame_obj.dirty_bit = 1
        print(f'Process {self.pid} marked virtual page {virtual_page_no} as dirty.')