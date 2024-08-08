import tkinter as tk
import ttkbootstrap as ttk
import customtkinter as ctk
import itertools
import time
import threading
import os
import sys

from PIL import Image, ImageTk
from tkinter import messagebox

#TODO:  add a backround color, finish all color choices, compile into app

class ScheduleBuilderApp:

    class SpinboxWidget():
        def __init__(self, master, fg_color, text_color, font, hours, time_index, text, button_color, max, min, time_validation_callback=None):
            self.fg_color = fg_color
            self.text_color = text_color
            self.FONT = font
            self.hours = hours
            self.time_index = time_index
            self.button_color = button_color
            self.text = text
            self.time_validation_callback = time_validation_callback
            self.max = max
            self.min = min
    
            self.spinbox = ctk.CTkFrame(master=master, 
                                        fg_color=self.fg_color, 
                                        border_color=self.text_color, 
                                        border_width=2)
            
            self.time_label = ctk.CTkLabel(
                master=self.spinbox, 
                text=f'{self.text} {self.hours[self.time_index]}', 
                font=(self.FONT, 14), 
                fg_color=self.fg_color, 
                text_color=self.text_color,
            )
            self.increment_button = ctk.CTkButton(
                master=self.spinbox, 
                text="▲", 
                width=20, 
                height=4, 
                font=('impact', 5),
                command=self.increment, 
                fg_color=self.button_color, 
                text_color=self.text_color
            )
            self.decrement_button = ctk.CTkButton(
                master=self.spinbox, 
                text="▼", 
                width=20, 
                height=4, 
                font=('impact', 5),
                command=self.decrement, 
                fg_color=self.button_color, 
                text_color=self.text_color
            )

            self.layout_widgets()

        def layout_widgets(self):
            self.time_label.grid(row=0, 
                                 column=0, 
                                 rowspan=2, 
                                 padx=5, 
                                 pady=2)
            self.increment_button.grid(row=0, 
                                       column=1, 
                                       padx=(0, 5), 
                                       sticky='s')
            self.decrement_button.grid(row=1, 
                                       column=1, 
                                       padx=(0, 5), 
                                       sticky='n')

        def increment(self):
            self.time_index += 1
            if self.time_index >= self.max:
                self.time_index = self.min
            self.update_time()

        def decrement(self):
            self.time_index -= 1
            if self.time_index < self.min:
                self.time_index = self.max
            self.update_time()

        def update_time(self):
            self.time_label.configure(text=f'{self.text} {self.hours[self.time_index]}')

            if self.time_validation_callback:
                self.time_validation_callback(self)

    def __init__(self, root):
        self.window = root
        self.window.state('zoomed')
        self.window.overrideredirect(True)

        self.FONT = 'MS Reference Sans Serif'
        self.MAIN_COLOR = '#3E60C1'

        self.SECONDARY_COLOR = '#2E4583'
        self.TERTIARY_COLOR = '#98c1d9'

        self.ACCENT_COLOR1 = '#001550'
        self.ACCENT_COLOR2 = '#001550'

        self.BACKROUND_COLOR = '#C4DDFF'

        self.TOOLBAR_TEXTCOLOR = '#000C26'
        self.SEPARATOR_COLOR = '#293556'
        self.CALENDAR_COLOR = '#C4DDFF'

        self.window_width = self.window.winfo_screenwidth()
        self.window_height = self.window.winfo_screenheight()

        self.class_counter = 0
        self.section_counter = 0
        self.possibility = 0

        self.sections = []
        self.classes = []
        self.schedules = []
        self.class_components = {}

        self.menu_shown = False
        self.schedule_generated = tk.BooleanVar()
        self.schedule_generated.set(False)
        self.schedule_generated.trace_add("write", self.renew_schedule)

        self.colors = ('red', 'light blue', 'light green', 'pink', 'orange', 'grey', 'yellow', 'cyan', 'coral', 'magenta')
        self.weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
        self.hours = ('08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00')

        self.style = ttk.Style()
        self.style.configure('blue.TSeparator', 
                        background=self.SECONDARY_COLOR)
        
        self.style.configure('sect.TMenubutton', background=self.MAIN_COLOR)
        
        self.style.configure('TMenubutton', 
                             background=self.TERTIARY_COLOR, 
                             borderwidth=0, 
                             foreground=self.TOOLBAR_TEXTCOLOR, 
                             arrowcolor=self.TOOLBAR_TEXTCOLOR,
                             font=(self.FONT, 11))

        self.setup_ui()

    def renew_schedule(self, *args):
        time.sleep(0.1)
        new_text = f'Schedule Mockup #{self.possibility+1}' if self.schedule_generated.get() else f'Schedule Mockup #{self.possibility+1} (OLD)'
        new_color = self.TOOLBAR_TEXTCOLOR if self.schedule_generated.get() else self.ACCENT_COLOR1
        # Check if the new text is different from the current text
        if self.tabs.cget("text") != new_text:
            self.tabs.configure(text=new_text, text_color=new_color)
        
    def setup_ui(self):
        self.setup_banner()
        self.setup_main_frame()
        self.setup_toolbar()
        self.setup_class_selector()
        self.setup_calendar_banner()
        self.setup_schedule_ui()

    def get_possibilities(self):

        entries = {}
        item_label = []

        # Get all child widgets
        child_widgets = self.class_list.winfo_children()

        # Sort child widgets by their current row to ensure proper ordering
        child_widgets.sort(key=lambda widget: widget.grid_info().get('row', 0))

        menu_index = 0

        for widget in child_widgets:

            if isinstance(widget, ttk.Menubutton):
                item_label = []  # Initialize item_label for each Menubutton

                accessed_menu_name = widget["menu"]
                accessed_menu = widget.nametowidget(accessed_menu_name)

                # Print all options in the menu
                for i in range(accessed_menu.index("end") + 1):
                    item_label.append(accessed_menu.entrycget(i, "label"))

                entries[self.classes[menu_index]] = item_label
                menu_index += 1

        # Helper function to convert time ranges to indices
        def time_range_to_indices(time_range_str, times_list):
            # Extract multiple time ranges
            ranges = time_range_str.split(', ')
            indices = []
            
            for time_range in ranges:
                parts = time_range.split(': ')
                if len(parts) != 2:
                    raise ValueError(f"Time range format error: '{time_range}'")
                
                day = parts[0]
                times = parts[1].split(' - ')
                if len(times) != 2:
                    raise ValueError(f"Start and end times are not properly formatted: '{time_range}'")
                
                start_time = times[0]
                end_time = times[1]
                
                if start_time not in times_list or end_time not in times_list:
                    raise ValueError(f"Time '{start_time}' or '{end_time}' not in list")
                
                start_index = times_list.index(start_time)
                end_index = times_list.index(end_time)
                indices.append((day, start_index, end_index))
            
            return indices

        # Function to check if any two time ranges on the same day overlap
        def times_overlap(indices1, indices2):
            day_time_dict1 = {}
            day_time_dict2 = {}

            # Organize time ranges by day
            for day, start, end in indices1:
                if day not in day_time_dict1:
                    day_time_dict1[day] = []
                day_time_dict1[day].append((start, end))

            for day, start, end in indices2:
                if day not in day_time_dict2:
                    day_time_dict2[day] = []
                day_time_dict2[day].append((start, end))

            # Check overlaps for each day
            for day in day_time_dict1:
                if day in day_time_dict2:
                    for start1, end1 in day_time_dict1[day]:
                        for start2, end2 in day_time_dict2[day]:
                            if start1 < end2 and start2 < end1:
                                return True
            return False

        # Function to check if a combination has overlapping times
        def combination_has_no_overlaps(combination, times_list):
            indices_list = [time_range_to_indices(sec.split(' > ')[1], times_list) for sec in combination]
            for i in range(len(indices_list)):
                for j in range(i + 1, len(indices_list)):
                    if times_overlap(indices_list[i], indices_list[j]):
                        return False
            return True

        # Main function to generate all possible valid schedules
        def generate_schedules(classes, times_list):
            section_lists = list(classes.values())
            all_combinations = itertools.product(*section_lists)
            self.schedules = []
            
            for combination in all_combinations:
                if combination_has_no_overlaps(combination, times_list):
                    formatted_schedule = []
                    for sec in combination:
                        parts = sec.split(' | ')
                        section_info = parts[0]
                        teacher = parts[1].split(' > ')[0]
                        time_indices = time_range_to_indices(parts[1].split(' > ')[1], times_list)
                        formatted_schedule.append((section_info, teacher, time_indices))
                    self.schedules.append(formatted_schedule)
            
            return self.schedules
        
        if self.class_counter > 0:
            self.possibility = 0
            self.schedules = generate_schedules(entries, self.hours)      
            self.show_schedule()
        else:
            self.show_notification("Notification", "No classes were given")

    def show_schedule(self):

        if len(self.schedules) > 0:

            for time_slot in self.frames.values():
                time_slot.configure(fg_color=self.MAIN_COLOR, text='')

            self.schedule_generated.set(True)

            current_schedule = self.schedules[self.possibility]

            for class_num, class_sections in enumerate(current_schedule):

                for day, start, end in class_sections[2]:
            
                    event_title = self.frames[(start, day)]
                    event_title.configure(text=f'{class_sections[0]}')

                    for hour in range(start, end):
                        self.frames[(hour, day)].configure(fg_color=self.colors[class_num])
        else:
            self.show_notification('Notification', 'No possible schedules match these parameters')

    def increment_possibility(self):
        if self.schedule_generated.get():
            if self.possibility < len(self.schedules)-1:
                self.possibility += 1
            else:
                self.possibility = 0
            self.tabs.configure(text = f'Mockup Schedule {self.possibility+1}')
            self.show_schedule()    

    def decrement_possibility(self):
        if self.schedule_generated.get():
            if self.possibility > 0:
                self.possibility -= 1
            else:
                self.possibility = len(self.schedules)-1
            self.tabs.configure(text = f'Schedule Mockup #{self.possibility+1}')
            self.show_schedule() 

    def setup_banner(self):
        banner = ctk.CTkFrame(master=self.window, 
                              corner_radius=0, 
                              fg_color=self.BACKROUND_COLOR)
        banner.pack(side=tk.TOP, fill=tk.X)

        banner_canvas_size = 35
        banner_canvas = ctk.CTkCanvas(master=banner, 
                                      width=banner_canvas_size, 
                                      height=banner_canvas_size)
        banner_canvas.configure(background=self.BACKROUND_COLOR)

        banner_canvas.create_oval(0, 0, 30, 30, 
                                  outline=self.ACCENT_COLOR2, 
                                  fill=self.ACCENT_COLOR2)
        banner_canvas.grid(row=0, 
                           column=0, 
                           padx=(15, 0), 
                           pady=5, 
                           sticky='w')

        banner_text = ctk.CTkLabel(master=banner, 
                                   text='Schedule Builder Application | tristandermody8@gmail.com', 
                                   font=(self.FONT, 16), 
                                   fg_color=self.BACKROUND_COLOR, 
                                   text_color=self.ACCENT_COLOR1)
        banner_text.grid(row=0, 
                         column=1, 
                         padx=(0, banner_canvas_size), 
                         pady=10, 
                         sticky='n')

        banner.grid_columnconfigure(0, weight=0)
        banner.grid_columnconfigure(1, weight=1)

    def setup_main_frame(self):
        self.main_frame = ctk.CTkFrame(master=self.window, 
                                  corner_radius=0, 
                                  fg_color=self.BACKROUND_COLOR)
        self.main_frame.pack(fill=tk.BOTH, 
                        expand=True)
        
    def setup_calendar_banner(self):

        self.calendar_frame = ctk.CTkFrame(master=self.main_frame, 
                                     corner_radius=0, 
                                     fg_color=self.CALENDAR_COLOR, border_width=1, border_color=self.CALENDAR_COLOR)
        
        self.calendar_frame.pack(
                           fill=tk.BOTH, 
                           expand=True,
                           padx=(0,8))
        
        self.calendar_banner = ctk.CTkFrame(master=self.calendar_frame, 
                                            fg_color=self.SECONDARY_COLOR, 
                                            corner_radius=0)
        self.calendar_banner.pack(side=tk.TOP, fill=tk.X) 

        self.tabs = ctk.CTkLabel(master=self.calendar_banner, 
                                 text='Schedule Mockup #1', 
                                 font=(self.FONT, 18), 
                                 text_color=self.TOOLBAR_TEXTCOLOR)
        self.tabs.grid(row=0, column=0, sticky='ens', padx=25, pady=18)

        self.left_button = ctk.CTkButton(master=self.calendar_banner, 
                                         text='◄', 
                                         font=('impact', 20), 
                                         width=30, 
                                         text_color=self.TOOLBAR_TEXTCOLOR, 
                                         fg_color=self.SECONDARY_COLOR, 
                                         anchor='center',
                                         command=self.decrement_possibility)
        
        self.left_button.grid(row=0, 
                              column=1, 
                              sticky='e', 
                              padx=0, 
                              pady=18)

        self.right_button = ctk.CTkButton(master=self.calendar_banner, 
                                          text='►', 
                                          font=('impact', 20), 
                                          width=30, 
                                          text_color=self.TOOLBAR_TEXTCOLOR, 
                                          fg_color=self.SECONDARY_COLOR, 
                                          anchor='center',
                                          command=self.increment_possibility)
        
        self.right_button.grid(row=0, 
                               column=2, 
                               sticky='e', 
                               padx=(0,25), 
                               pady=18)
        
        self.separator = ctk.CTkCanvas(master=self.calendar_banner, width=720, height=1)
        self.separator.configure(background=self.SEPARATOR_COLOR)
        self.separator.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(3,0))

        self.calendar_banner.grid_columnconfigure(0, weight=0)
        self.calendar_banner.grid_columnconfigure(1, weight=1)
        self.calendar_banner.grid_columnconfigure(2, weight=0)

    def setup_schedule_ui(self):

        self.frames = {}  # Dictionary to store frame references

        # Create the main frame for the calendar
        calendar = ctk.CTkFrame(master=self.main_frame, fg_color=self.CALENDAR_COLOR, corner_radius=0)
        calendar.pack(pady=(0,9), padx=(0,8), expand=True, fill=tk.BOTH, anchor = 'n')

        # Create the header row with days of the week
        for i, day in enumerate(self.weekdays):
            day_label = ctk.CTkLabel(master=calendar, text=day, width=155, anchor="center", text_color=self.TOOLBAR_TEXTCOLOR, fg_color=self.SECONDARY_COLOR)
            day_label.grid(row=0, column=i+1, padx=0, pady=(0,5), sticky='ew')

        # Create the time column and grid slots
        for index, hour in enumerate(self.hours):
            # Create a time label or a blank label
            if index % 2 == 0:
                time_label = ctk.CTkLabel(master=calendar, text=hour, text_color=self.TOOLBAR_TEXTCOLOR)
            else:
                time_label = ctk.CTkLabel(master=calendar, text="")
            time_label.grid(row=index+1, column=0, padx=7, sticky='nsew')

            for j, day in enumerate(self.weekdays):
                self.slot_frame = ctk.CTkLabel(master=calendar, 
                                               height=10, 
                                               width=155, 
                                               text = '', 
                                               fg_color=self.MAIN_COLOR, 
                                               corner_radius=0, 
                                               text_color=self.TOOLBAR_TEXTCOLOR)
                self.slot_frame.grid(row=index + 1, 
                                     column=j+1, 
                                     sticky='nsew', 
                                     padx=(1,0), 
                                     pady=(1,0))
                # Store reference to the frame with a unique key
                self.frames[(index, day[:3])] = self.slot_frame

        # Configure grid weights
        for i in range(len(self.weekdays) + 1):
            calendar.columnconfigure(i, weight=1)
        for i in range(len(self.hours) + 2):
            calendar.rowconfigure(i, weight=1)

    def setup_toolbar(self):
        toolbar_width = self.window_width / 6
        toolbar_frame = ctk.CTkFrame(master=self.main_frame, 
                                     corner_radius=10, 
                                     fg_color=self.MAIN_COLOR, 
                                     width=toolbar_width,
                                     background_corner_colors=(self.BACKROUND_COLOR, self.MAIN_COLOR, self.MAIN_COLOR, self.BACKROUND_COLOR))
        toolbar_frame.pack(side=tk.LEFT, 
                           fill=tk.Y, 
                           padx=(10,0), 
                           pady=(0, 10))
        self.toolbar_frame = toolbar_frame

        toolbar_title = ctk.CTkLabel(master=toolbar_frame, 
                                     text='SCHEDULER', 
                                     font=(self.FONT, 18), 
                                     fg_color=self.MAIN_COLOR, 
                                     text_color=self.TOOLBAR_TEXTCOLOR, 
                                     width=toolbar_width, 
                                     anchor='w')
        toolbar_title.grid(row=0, 
                           column=0, 
                           padx=25, 
                           pady=20, 
                           sticky='ew')

        toolbar_canvas = ctk.CTkCanvas(master=toolbar_frame, 
                                       width=30, 
                                       height=30)
        toolbar_canvas.configure(background=self.MAIN_COLOR)
        toolbar_canvas.create_oval(0, 0, 20, 20, 
                                   outline=self.SECONDARY_COLOR, 
                                   fill=self.SECONDARY_COLOR)
        toolbar_canvas.grid(row=0, 
                            column=1, 
                            padx=15, 
                            pady=5, 
                            sticky='e')

        separator1 = ctk.CTkCanvas(master=toolbar_frame, width=toolbar_width, height=1)
        separator1.configure(background=self.SEPARATOR_COLOR)

        separator1.grid(row=1, 
                        column=0, 
                        columnspan=2, 
                        sticky='ew')

        button1_image = self.load_image("calendar.png", 20, 20)
        button1 = ctk.CTkButton(master=toolbar_frame, 
                                text='    GENERATE SCHEDULES', 
                                font=(self.FONT, 15),
                                anchor='w', 
                                image=button1_image, 
                                compound='right', 
                                width=toolbar_width, 
                                height=40, 
                                corner_radius=0, 
                                fg_color=self.MAIN_COLOR, 
                                text_color=self.TOOLBAR_TEXTCOLOR, 
                                hover_color=self.TERTIARY_COLOR,
                                command=self.get_possibilities)
        button1.grid(row=2, 
                     column=0, 
                     columnspan=2, 
                     sticky='ew', 
                     pady=(20, 0))

        button2_image = self.load_image('exit.png', 25, 25)
        button2 = ctk.CTkButton(master=toolbar_frame, 
                                text='    EXIT TO DESKTOP', 
                                font=(self.FONT, 15), 
                                anchor='w', 
                                image=button2_image, 
                                compound='right', 
                                width=toolbar_width, 
                                height=40, 
                                corner_radius=0, 
                                fg_color=self.MAIN_COLOR, 
                                text_color=self.TOOLBAR_TEXTCOLOR, 
                                hover_color=self.TERTIARY_COLOR,
                                command=lambda: self.window.destroy())
        button2.grid(row=3, 
                     column=0, 
                     columnspan=2, 
                     sticky='ew', 
                     pady=20)

        separator2 = ctk.CTkCanvas(master=toolbar_frame, width=toolbar_width, height=1)
        separator2.configure(background=self.SEPARATOR_COLOR)
        separator2.grid(row=4, 
                        column=0, 
                        columnspan=2, 
                        sticky='ew')

        classes_label = ctk.CTkLabel(master=toolbar_frame, 
                                     text='     CLASSES', 
                                     font=(self.FONT, 13), 
                                     anchor='w', 
                                     height=40, 
                                     fg_color=self.MAIN_COLOR, 
                                     text_color=self.ACCENT_COLOR1)
        classes_label.grid(row=5, 
                           column=0, 
                           columnspan=2, 
                           sticky='ew', 
                           pady=(10,0))

        self.class_list = ctk.CTkScrollableFrame(master=toolbar_frame, 
                                                 width=toolbar_width, 
                                                 height=300, 
                                                 fg_color=self.MAIN_COLOR, 
                                                 scrollbar_button_color=self.MAIN_COLOR, scrollbar_button_hover_color=self.MAIN_COLOR)
        
        self.class_list.grid(row=6, column=0, columnspan=2, sticky='nsew', pady=(0, 10))

        self.add_class_button = ctk.CTkButton(master=toolbar_frame, 
                                         text='+ Add Classes', 
                                         font=(self.FONT, 13), 
                                         fg_color=self.TERTIARY_COLOR, 
                                         text_color=self.TOOLBAR_TEXTCOLOR,
                                         command=self.class_menu_animate)
        self.add_class_button.grid(row=7, 
                              column=0, 
                              columnspan=2, 
                              sticky='s', 
                              pady=10)

        toolbar_frame.grid_rowconfigure(6, weight=1)

    def setup_class_selector(self):

        toolbar_width = self.window_width / 6

        self.class_selector = ctk.CTkFrame(master=self.window, 
                                           fg_color=self.SECONDARY_COLOR, 
                                           bg_color=self.MAIN_COLOR, height=2, 
                                           width=toolbar_width + 89, 
                                           corner_radius=10,
                                           background_corner_colors=(self.SECONDARY_COLOR, self.SECONDARY_COLOR, self.MAIN_COLOR, self.MAIN_COLOR))
        
        self.course_info_label = ctk.CTkLabel(master=self.class_selector, 
                                              fg_color=self.SECONDARY_COLOR, 
                                              bg_color=self.TERTIARY_COLOR, 
                                              text='Course Info',
                                              font=(self.FONT, 14),
                                              text_color=self.TOOLBAR_TEXTCOLOR)
        
        self.class_input = ctk.CTkEntry(master=self.class_selector, 
                                        placeholder_text='Course Name (ex: Math)', 
                                        width=260,
                                        fg_color=self.TERTIARY_COLOR, 
                                        bg_color=self.SECONDARY_COLOR, 
                                        border_color=self.TOOLBAR_TEXTCOLOR, 
                                        text_color=self.TOOLBAR_TEXTCOLOR, 
                                        placeholder_text_color=self.ACCENT_COLOR1, 
                                        font=(self.FONT, 14))
        
        self.course_code_input = ctk.CTkEntry(master=self.class_selector, 
                                              placeholder_text='Course Code (ex: 101-NYA-05)', 
                                              width=260,
                                              fg_color=self.TERTIARY_COLOR,
                                              bg_color=self.SECONDARY_COLOR, 
                                              border_color=self.TOOLBAR_TEXTCOLOR, 
                                              text_color=self.TOOLBAR_TEXTCOLOR, 
                                              placeholder_text_color=self.ACCENT_COLOR1, 
                                              font = (self.FONT, 14))
        
        self.separator_canvas = ctk.CTkCanvas(master=self.class_selector, width=720, height=1)
        self.separator_canvas.configure(background=self.TOOLBAR_TEXTCOLOR)

        self.section_info_title = ctk.CTkLabel(master=self.class_selector, 
                                              fg_color=self.SECONDARY_COLOR, 
                                              bg_color=self.SECONDARY_COLOR, 
                                              text='Section Info',
                                              font=(self.FONT, 14),
                                              text_color=self.TOOLBAR_TEXTCOLOR)

        self.time_frame = ctk.CTkFrame(master=self.class_selector, fg_color=self.SECONDARY_COLOR)

        self.spinbox_start = self.SpinboxWidget(
            master=self.time_frame, 
            fg_color=self.TERTIARY_COLOR, 
            text_color=self.TOOLBAR_TEXTCOLOR, 
            font=self.FONT, 
            hours=self.hours, 
            time_index=0,
            text='From: ',
            max=0,
            min=0,
            button_color=self.TERTIARY_COLOR,
            time_validation_callback=self.validate_times
        )

        self.spinbox_end = self.SpinboxWidget(
            master=self.time_frame, 
            fg_color=self.TERTIARY_COLOR, 
            text_color=self.TOOLBAR_TEXTCOLOR, 
            font=self.FONT, 
            hours=self.hours, 
            time_index=self.spinbox_start.time_index+1,
            text='To: ',
            max=len(self.hours)-1,
            min=0,
            button_color=self.TERTIARY_COLOR,
            time_validation_callback=self.validate_times
        )

        self.teacher_input = ctk.CTkEntry(master=self.class_selector, 
                                              placeholder_text="Teacher's name (ex: Jane Smith)", 
                                              width=260,
                                              fg_color=self.TERTIARY_COLOR,
                                              bg_color=self.SECONDARY_COLOR, 
                                              border_color=self.TOOLBAR_TEXTCOLOR, 
                                              text_color=self.TOOLBAR_TEXTCOLOR, 
                                              placeholder_text_color=self.ACCENT_COLOR1, 
                                              font = (self.FONT, 14))

        self.menu_frame=ctk.CTkFrame(master=self.time_frame, 
                                      fg_color=self.TERTIARY_COLOR, 
                                      border_color=self.TOOLBAR_TEXTCOLOR, 
                                      border_width=2)
                                      
        self.days = ttk.Menubutton(master=self.menu_frame, text='on:', style='blue.TMenuButton')
        self.menu = tk.Menu(master=self.days, tearoff=False)
        self.days.config(menu=self.menu)

        self.selected_day_var = tk.StringVar()
        self.menu_item_ids = {}

        for day_name in self.weekdays:

            self.menu.add_radiobutton(
                label=day_name,
                variable=self.selected_day_var,
                value=day_name,  # Each radiobutton should have a unique value
                command=lambda day=day_name: confirm_day(day),
                font=(self.FONT, 8),
                foreground=self.TOOLBAR_TEXTCOLOR,
                background=self.TERTIARY_COLOR,
                indicatoron=False,
                activebackground=self.MAIN_COLOR
            )
            self.menu_item_ids[day_name] = day_name

        self.menu.add_radiobutton(label='Clear Times', 
                                  font=(self.FONT, 8),
                                  command=lambda text='Clear Times': confirm_day(text),
                                  foreground=self.TOOLBAR_TEXTCOLOR,
                                  background=self.SECONDARY_COLOR,
                                  selectcolor=self.MAIN_COLOR,
                                  activebackground=self.SECONDARY_COLOR,
                                  indicatoron=False)

        self.section_times = {day: '' for day in self.weekdays}

        self.confirmation = ctk.CTkFrame(master=self.class_selector, fg_color=self.SECONDARY_COLOR)

        self.section_data_confirm = ctk.CTkButton(master=self.confirmation, 
                                                  text='Add Section', 
                                                  text_color=self.TOOLBAR_TEXTCOLOR, 
                                                  bg_color=self.SECONDARY_COLOR, 
                                                  fg_color=self.MAIN_COLOR, 
                                                  width=50, 
                                                  corner_radius=10,
                                                  command=lambda:self.add_section())
        
        self.section_data_confirm_label = ctk.CTkLabel(master=self.confirmation, 
                                                      fg_color=self.SECONDARY_COLOR, 
                                                      bg_color=self.SECONDARY_COLOR, 
                                                      text='',
                                                      compound='right',
                                                      font=(self.FONT, 12),
                                                      text_color=self.TOOLBAR_TEXTCOLOR)

        def confirm_day(day):

            if day == 'Clear Times':

                for day in self.weekdays:
                    self.section_times = {day: ''}
                    self.menu.entryconfigure(self.menu_item_ids[day], label = day)
                    self.menu_item_ids[day] = day

            else:
                self.section_times[day] = self.hours[self.spinbox_start.time_index] + ' - ' + self.hours[self.spinbox_end.time_index]
                self.menu.entryconfigure(self.menu_item_ids[day], label = day + ' | ' + self.section_times[day])
                self.menu_item_ids[day] = day + ' | ' + self.section_times[day]
            
    def class_menu_animate(self):

        max_height = 400
        min_height = 2
        deceleration = 5

        self.add_class_button.configure(state='disabled')

        self.spinbox_start.spinbox.pack(side=tk.LEFT, padx=5)
        self.spinbox_end.spinbox.pack(side=tk.LEFT, padx=5)
        self.menu_frame.pack(side=tk.LEFT, padx=5)
        self.days.pack(padx=5, pady=(5,7))

        self.section_data_confirm.pack(side=tk.LEFT)
        self.section_data_confirm_label.pack(side=tk.LEFT, padx=10)

        def increase_height():
            nonlocal dropdown_height

            if dropdown_height > 0:
                self.class_input.place(x=20, y=int(dropdown_height * 0.15))
                self.course_info_label.place(x=20, y=15)

            if dropdown_height > 50:
                self.course_code_input.place(x=20, y=dropdown_height * 0.30)

            if dropdown_height > 100:
                self.separator_canvas.place(x=0, y=dropdown_height * 0.62)
                self.section_info_title.place(x=20, y=dropdown_height * 0.45)

            if dropdown_height > 150:
                self.teacher_input.place(x=21, y=dropdown_height * 0.55)
                self.time_frame.place(x=15, y=dropdown_height * 0.70)

            if dropdown_height > 200:
                self.confirmation.place(x=21, y=dropdown_height * 0.85 + 5)

            if dropdown_height < max_height - 1:
                increment = (max_height - dropdown_height) / deceleration
                dropdown_height += increment
                self.class_selector.configure(height=dropdown_height)
                self.class_selector.after(30, increase_height)
            else:
                self.add_class_button.configure(state='enabled')

        def decrease_height():
            nonlocal dropdown_height

            if dropdown_height > min_height + 1:
                increment = (min_height - dropdown_height) / deceleration
                dropdown_height += increment
                self.class_selector.configure(height=int(dropdown_height))
                self.class_selector.after(30, decrease_height)

            else:
                self.class_selector.configure(height=min_height)
                self.add_class_button.configure(state='enabled')
                self.class_selector.place_forget()
                self.clear_selections()

        if not self.menu_shown:
            
            if self.class_counter < 10:
                dropdown_height = min_height
                self.class_selector.place(x=self.toolbar_frame.winfo_rootx() - 5, y=257)
                self.add_class_button.configure(text='CANCEL')
                self.menu_shown = True
                increase_height()
            else:
                self.add_class_button.configure(state='enabled', text='Class Limit Reached', fg_color = 'red', text_color=self.TOOLBAR_TEXTCOLOR)

        elif self.menu_shown:
            dropdown_height = max_height
            self.add_class_button.configure(text='+ Add Classes')
            self.menu_shown = False
            decrease_height()

    def load_image(self, relative_path, resize_x, resize_y):

        if hasattr(sys, '_MEIPASS'):
            # Running as a bundled executable
            base_path = sys._MEIPASS
        else:
            # Running in a normal Python environment
            base_path = os.path.abspath(".")

        image_path = os.path.join(base_path, relative_path)

        try:
            image = ctk.CTkImage(light_image=Image.open(image_path), size=(resize_x, resize_y))
            return image
        except FileNotFoundError:
            pass

    def add_section(self):
        teacher_name = self.teacher_input.get().strip()
        course = self.course_code_input.get().strip()
        class_name = self.class_input.get().strip()

        if self.section_counter >= 10:
            self.section_data_confirm_label.configure(text='❌ Maximum 10 sections')

        elif len(teacher_name) == 0 or len(course) == 0 or len(class_name) == 0 or all(value == '' for value in self.section_times.values()):
            self.section_data_confirm_label.configure(text='❌ Entries cannot be empty')

        elif teacher_name.isspace() or course.isspace() or class_name.isspace():
            self.section_data_confirm_label.configure(text='❌ Entries must contain a non-blank character')

        elif len(course) > 10:
            self.section_data_confirm_label.configure(text='❌ Maximum 10 characters for course code')

        elif len(teacher_name.split(' ')) < 2 or any(char.isdigit() for char in teacher_name):
            self.section_data_confirm_label.configure(text="❌ Provide valid first and last name")

        else:
            days_with_times = {day: time for day, time in self.section_times.items() if time}

            # Convert the filtered dictionary to a string
            formatted_days = ', '.join(f'{day[:3]}: {time}' for day, time in days_with_times.items())

            section_info = f"{teacher_name} > {formatted_days}"

            # Check for duplicate info
            if section_info in self.sections:
                self.section_data_confirm_label.configure(text='❌ Section Already Exists')
            else:
                self.sections.append(section_info)
                self.section_counter += 1
                self.section_data_confirm_label.configure(text=f'✔️ Section #{self.section_counter} added!')
                self.add_class_button.configure(text='Confirm', command=lambda: self.add_class())
        
    def add_class(self):
        
        name = self.class_input.get()
        current_class = f'{name if len(name) < 15 else name[:15] + "…"} ({self.course_code_input.get()})'

        if current_class in self.classes:

            self.add_class_button.configure(text='Class Already Exists', fg_color='red', text_color = self.TOOLBAR_TEXTCOLOR)

        else:
            self.classes.append(current_class)
            class_label_text = f'# Class {self.class_counter + 1} | {current_class}'

            self.class_label = ctk.CTkLabel(
                master=self.class_list,
                text = class_label_text,
                font=(self.FONT, 14),
                anchor='w',
                fg_color=self.MAIN_COLOR,
                text_color=self.TOOLBAR_TEXTCOLOR,
            )

            self.section_button = ttk.Menubutton(master=self.class_list, text='❌', style='sect.TMenubutton')
            
            self.class_section_menu = tk.Menu(master=self.section_button, tearoff=False)
            self.section_button.config(menu=self.class_section_menu)
            self.class_color = ctk.CTkFrame(master=self.class_list, corner_radius=10, fg_color='red', width=10, height=10)

            self.selected_sect = tk.StringVar()

            for sect_num, sect_info in enumerate(self.sections):
                
                label_text = f'Sect. {sect_num + 1} | {sect_info}'

                self.class_section_menu.add_radiobutton(
                    label=label_text,
                    value=sect_num,
                    variable=self.selected_sect,
                    command=lambda menu=self.class_section_menu, label=self.class_label, button=self.section_button, color=self.class_color: self.delete_section(menu, label, button, color),
                    font=(self.FONT, 8),
                    foreground=self.TOOLBAR_TEXTCOLOR,
                    background=self.MAIN_COLOR,
                    selectcolor=self.MAIN_COLOR,
                    activebackground=self.TERTIARY_COLOR,         
                )
            
            self.class_label.grid(row=self.classes.index(current_class), column=0, padx=(18, 0), pady=5, sticky='nsw')
            self.section_button.grid(row=self.classes.index(current_class), column=1, stick='w')

            self.class_color.grid(row=self.classes.index(current_class), column=2, sticky='e')
            self.class_color.configure(fg_color = self.colors[self.classes.index(current_class)])

            self.class_list.grid_columnconfigure(0, weight=0)
            self.class_list.grid_columnconfigure(1, weight=0)
            self.class_list.grid_columnconfigure(2, weight=1)

            self.class_counter += 1

            if self.class_counter > 8:
                self.class_list.configure(scrollbar_button_color=self.ACCENT_COLOR1, scrollbar_button_hover_color=self.ACCENT_COLOR2)

            self.class_menu_animate()
            self.add_class_button.configure(text='+ Add Classes', command=self.class_menu_animate, fg_color=self.TERTIARY_COLOR)
            self.schedule_generated.set(False)
            
    def delete_section(self, menu, label, button, color):
        self.schedule_generated.set(False)
        
        if menu.index('end') == 0:
            # Destroy the given widgets
            label.destroy()
            button.destroy()
            color.destroy()

            # Update the classes list and class counter
            self.classes.remove(label.cget('text').split('|')[1].strip())
            self.class_counter -= 1
            
            # Get all child widgets and sort by their current row to maintain order
            child_widgets = self.class_list.winfo_children()
            child_widgets.sort(key=lambda widget: widget.grid_info().get('row', 0))

            # Separate widgets by type
            labels = []
            buttons = []
            colors = []

            for widget in child_widgets:
                if isinstance(widget, ctk.CTkLabel):
                    labels.append(widget)
                elif isinstance(widget, ttk.Menubutton):
                    buttons.append(widget)
                else:
                    colors.append(widget)

            # Update labels
            for index, label in enumerate(labels):
                if index < len(self.classes):  # Ensure index is within bounds
                    new_label = f'# Class {index + 1} | {self.classes[index]}'
                    label.configure(text=new_label)
                    label.grid(row=index, column=0, padx=(18, 0), pady=5)

            # Update Menubuttons
            for index, button in enumerate(buttons):
                button.grid(row=index, column=1, sticky='w')

            # Update color widgets
            for index, color_widget in enumerate(colors):
                if index < len(self.colors):  # Ensure index is within bounds
                    color_widget.configure(fg_color=self.colors[index])
                    color_widget.grid(row=index, column=2, sticky='e')

            if self.class_counter <= 8:
                self.class_list.configure(scrollbar_button_color=self.MAIN_COLOR, scrollbar_button_hover_color=self.MAIN_COLOR)

        else:
            section = self.selected_sect.get()
            menu.delete(section)
            last_index = menu.index("end")
            for i in range(0, last_index + 1):
                # Update labels and values
                label_text = f'Sect. {i + 1} | {menu.entrycget(i, "label").split("|")[1]}'
                menu.entryconfig(i, label=label_text, value=i)
    
    def validate_times(self, widget):
        start_index = self.spinbox_start.time_index
        end_index = self.spinbox_end.time_index

        if widget == self.spinbox_start:
            # Ensure start time is always less than end time
            self.spinbox_end.min = start_index+1

        elif widget == self.spinbox_end:
            # Ensure end time is always greater than start time
            self.spinbox_start.max = end_index-1

    def clear_selections(self):
        self.section_counter = 0
        self.sections.clear()
        self.section_data_confirm_label.configure(text='')

        if len(self.teacher_input.get()) != 0 or len(self.course_code_input.get()) != 0 or len(self.class_input.get()) != 0:
            self.class_input.delete(0, tk.END)
            self.course_code_input.delete(0, tk.END)
            self.teacher_input.delete(0, tk.END)

        for day in self.weekdays:
            self.section_times = {day: ''}
            self.menu.entryconfigure(self.menu_item_ids[day], label = day)
            self.menu_item_ids[day] = day

    def show_notification(self, message, body):

        messagebox.showerror(message, body)

def main_application(root, splash):
    # Simulate loading of assets or other initialization tasks
    time.sleep(1.5)
    
    root.deiconify()  # Show the main application window
    splash.destroy()  # Destroy the splash screen

def create_splash_screen():
    splash = tk.Toplevel()
    splash.state('zoomed')
    splash.overrideredirect(True)
    splash.attributes('-topmost', True)
    
    relative_path = 'icon1.png'

    if hasattr(sys, '_MEIPASS'):
            # Running as a bundled executable
            base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")

    image_path = os.path.join(base_path, relative_path)


    pil_image = Image.open(image_path)
    image = ImageTk.PhotoImage(pil_image)
    
    # Create a label to display the image
    image_label = tk.Label(splash, image=image)
    image_label.image = image  # Keep a reference to avoid garbage collection
    image_label.pack(expand=True)
    
    # Optional: Add an image or progress bar here
    return splash

def main():
    root = ttk.Window()
    root.withdraw()  # Hide the root window initially
    splash = create_splash_screen()

    app = ScheduleBuilderApp(root)
    
    
    # Start the main application in a new thread
    threading.Thread(target=main_application, args=(root, splash)).start()
    
    root.mainloop()

if __name__ == '__main__':
    main()


