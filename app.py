import os
import sys
import termios
import tty
import threading
import time
from typing import List
import pyfiglet
import queue

'''
MOVEMENT
\033[<row>;<col>H  // move cursor to absolute position
\033[<n>A          // move cursor up n rows
\033[<n>B          // move cursor down n rows
\033[<n>C          // move cursor right n cols
\033[<n>D          // move cursor left n cols
SCREEN AND LINE CONTROL
\033[2J            // clear screen
\033[K             // clear to end of line
\033[1K            // clear from start of line to cursor
\033[2K            // clear entire line
\033[s             // save cursor position
\033[u             // restore saved cursor position
TEXT COLOR
\033[0m            // reset all formatting
\033[31m           // set red
\033[32m           // set green
\033[33m           // set yellow
\033[34m           // set blue
\033[1m            // set bold

█
'''
block = '█'
size = os.get_terminal_size()

class Routine:

    def __init__(self, name):
        self.name = name
        self.tasks = []

    def add_task(self, name, duration):
        self.tasks.append((name, duration))

    def edit_task(self, orig_name, new_name = "", new_duration = -1):
        index = -1
        for i, task in enumerate(self.tasks):
            if task[0] == orig_name:
                index = i
                break

        if (new_name != ""):
            self.tasks[index] = (new_name, self.tasks[index][1])
        if (new_duration != -1):
            self.tasks[index] = (self.tasks[index][0], new_duration)

    def edit_name(self, new_name):
        self.name = new_name

    #def start_routine(self):

class Screen:
    v_padding = 2
    h_padding = 5
    
    def __init__(self):
        self.screen = ""
        self.menus = []
        self.current_menu = 0

    @staticmethod
    def cursor_to(row, col):
        return f"\033[{row};{col}H"

    @staticmethod
    def get_center_row(height):
        return (int) (size.lines / 2 - height / 2)

    @staticmethod
    def get_center_col(width):
        return (int) (2 + size.columns / 2 - width / 2)


    def draw_block(self, row, col):
        self.screen += self.cursor_to(row, col) + block
        
    def draw_char(self, row, col, char):
        self.screen += self.cursor_to(row, col) + char

    def draw_rect(self, row, col, width, height):
        str = self.cursor_to(row, col)
        for _ in range(width):
            str += block

        for i in range(height):
            current_row = row + 1 + i
            str += self.cursor_to(current_row, col)
            str += block
            str += self.cursor_to(current_row, col + width - 1)
            str += block

        str += self.cursor_to(row + height + 1, col)
        for _ in range(width):
            str += block

        self.screen += str

    def set_fg_col(self, r, g, b):
        self.screen += f"\033[38;2;{r};{g};{b}m"

    def set_bg_col(self, r, g, b):
        self.screen += f"\033[48;2;{r};{g};{b}m"

    def add_screen(self, value):
        self.screen += value 

    def clear_screen(self):
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    """
    ███████████
    █         █
    █  title  █
    █         █
    █  1      █
    █  2      █
    █  3      █
    █         █
    ███████████
    """
    def display_menu(self):
        menu = self.menus[self.current_menu]
        options = menu.options

        max_width = len(menu.title)
        for option in options:
            max_width = len(option[0]) if len(option[0]) > max_width else max_width
        
        max_width += self.h_padding * 2
        max_height = len(menu.options) + 1 + 1 + self.v_padding * 2

        row = self.get_center_row(max_height)
        col = self.get_center_col(max_width)

        # Print box around menu
        self.draw_rect(row, col, max_width, max_height)

        # Print title
        title_row = row + self.v_padding + 1
        title_col = self.get_center_col(len(menu.title))
        title = self.cursor_to(title_row, title_col) + menu.title
        self.add_screen(title)
        
        # Print marker then options
        option_col = col + self.h_padding - 1
        option_row = title_row + 2
        self.add_screen(self.cursor_to(option_row, option_col))
        for i, option in enumerate(options):
            if i == menu.selected:
                marker = "# "
            else:
                marker = option[1] + " "
            words = option[0]
            self.add_screen(marker + words) 
            
            # move to next
            option_row += 1
            self.add_screen(self.cursor_to(option_row, option_col))
            
        num = self.cursor_to(1, 1) + " " + str(menu.selected)
        self.add_screen(num)

    def add_menu(self, menu):
        self.menus.append(menu)

    def set_menu(self, index):
        self.current_menu = index 

    def get_menu(self):
        return self.menus[self.current_menu]

    def update_screen(self):
        self.clear_screen()
        sys.stdout.write(self.screen)
        sys.stdout.flush()
        self.screen = ""

class Menu:

    """
    Options 
    [ ("name", "marker", lambda) ]
    """
    def __init__(self, title):
        self.title = title
        self.options = []
        self.selected = 0

    def set_title(self, title):
        self.title = title 

    def add_option(self, options, index = -1):
        if (index == -1):
            index = len(self.options)

        if (type(options) is list):
            for opt in options:
                self.options.insert(index, opt)
                index += 1
        else:
            self.options.insert(index, options)

    def up(self): 
        self.selected = (self.selected - 1) % len(self.options)

    def down(self):
        self.selected = (self.selected + 1) % len(self.options)

    def select(self):
        self.options[self.selected][2]()

    def remove_option(self, name = "", index = -1):
        if name != "":
            for i, option in enumerate(self.options):
                if option[0] == name:
                    self.options.remove(i)
                    return
        if index != -1 and index < len(self.options):
            self.options.remove(index)
            return
    
    def clear_options(self):
        self.options.clear()

def end_program():
    global running
    running = False

def update_main_menu():
    global routines
    global main_menu
    global screen

    # Clear options
    main_menu.clear_options()

    # Add routines
    for i, routine in enumerate(routines):
        main_menu.add_option((routine.name, "*", lambda: screen.set_menu(i)))

    # Add option to add routine
    main_menu.add_option(("Add new routine", "=", lambda: screen.draw_char(1, 5, "adding")))

    # Add option to quit
    main_menu.add_option(("Quit", "-", lambda: end_program()))

def update_routine_menu(menu, routine):
    global screen 

    # Change name
    menu.set_title(routine.name)

    # Add tasks
    for task in routine.tasks:
        menu.add_option((task[0] + " " + str(task[1]), "-", lambda: screen.draw_char(1, 5, task[0])))

    # Add new task
    menu.add_option(("Add new task", "+", lambda: screen.draw_char(1, 5, "Adding task")))
    # Add run routine
    menu.add_option(("Run routine", "=", lambda: screen.draw_char(1, 5, "Running")))
    # Add back to main menu
    menu.add_option(("Main menu", "~", lambda: screen.set_menu(0)))

def input_handler():
    global running 
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while running:
            key = sys.stdin.read(1)
            input_queue.put(key)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def graphics_handler():
    global size
    global running
    while running:
        size = os.get_terminal_size()
        screen.display_menu()
        screen.update_screen()

        while not input_queue.empty():
            key = input_queue.get()
        
            if key == 'q':
                running = False
            elif key == 'w':  # Move up
                screen.get_menu().up()
            elif key == 's':  # Move down
                screen.get_menu().down()
            elif key in ('\n', '\r'):  # Enter key
                screen.get_menu().select()
        
        time.sleep(1/30)

    screen.clear_screen()

input_queue = queue.Queue()
screen = Screen()
main_menu = Menu("Main Menu")
screen.add_menu(main_menu)

running = True

morning_routine_menu = Menu("Routine")
morning_routine = Routine("Morning routine")
morning_routine.add_task("Drink water", 60)
morning_routine.add_task("Make bed", 120)
morning_routine.add_task("Something else", 120)

night_routine_menu = Menu("Routine")
night_routine = Routine("Nighttime routine")
night_routine.add_task("Drink water", 60)
night_routine.add_task("Make bed", 120)
night_routine.add_task("Something else", 120)

school_routine_menu = Menu("Routine")
school_routine = Routine("School day")
school_routine.add_task("Drink water", 60)
school_routine.add_task("Make bed", 120)
school_routine.add_task("Something else", 120)


routines = [morning_routine, night_routine, school_routine]

update_main_menu()
update_routine_menu(morning_routine_menu, morning_routine)
update_routine_menu(night_routine_menu, night_routine)
update_routine_menu(school_routine_menu, school_routine)

screen.add_menu(morning_routine_menu)
screen.add_menu(night_routine_menu)
screen.add_menu(school_routine_menu)

screen.set_menu(1)

if __name__ == "__main__":
    input_thread = threading.Thread(target=input_handler, daemon=True)
    render_thread = threading.Thread(target=graphics_handler)

    input_thread.start()
    render_thread.start()

    render_thread.join()
    input_thread.join()

