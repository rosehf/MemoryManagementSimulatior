# Cadet Hayden Rose CIS-302 OS Project
# Page Module
# This module defines the Page and PageTable classes for process memory management.

class Page:
    def __init__(self, virtual_page_no, is_valid, frame_no):
        self.virtual_page_no = virtual_page_no
        self.is_valid = is_valid
        self.frame_no = frame_no
        self.dirty_bit = 0  # Initialize dirty bit to 0 (not modified from disk)

class PageTable:
    def __init__(self, process_id):
        self.pages = {}
        self.process_id = process_id

    def add_page(self, virtual_page_no, is_valid, frame_no):
        page = Page(virtual_page_no, is_valid, frame_no)
        self.pages[virtual_page_no] = page

    def lookup_page(self, virtual_page_no):
        return self.pages.get(virtual_page_no, None)
    
    def mark_dirty(self, virtual_page_no):
        page = self.lookup_page(virtual_page_no)
        if page:
            page.dirty_bit = 1

    def mark_valid(self, virtual_page_no, frame_no):
        page = self.lookup_page(virtual_page_no)
        if page:
            page.is_valid = True
            page.frame_no = frame_no
    
    def mark_invalid(self, virtual_page_no):
        page = self.lookup_page(virtual_page_no)
        if page:
            page.is_valid = False
            page.frame_no = -1

    
