import os
import sys
import termios
import tty
import threading
import time
from typing import List
import pyfiglet

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
        print("\033[2J\033[H", end='')

    def display_menu(self, menu):
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


    
#def progress_bar(row, col, width, percent):
    


# Function to get a single keypress (raw input)
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)  # Read one char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Clear the screen

# Draw menu with selection highlighting

def main():
    screen = Screen()
    
    main_menu = Menu("Main Menu")
    main_menu.add_option([
        ("Morning routine", "*", lambda x: x*x),
        ("Morning routine", "*", lambda x: x*x),
        ("Morning routine", "*", lambda x: x*x),
        ("Morning routine", "*", lambda x: x*x),
        ("Morning routine", "*", lambda x: x*x),
        ("Morning routine", "*", lambda x: x*x),
        ("Add new routine", "*", lambda x: x * x),
        ("Quit", "~", lambda x: x * x)
    ])

    while True:
        screen.display_menu(main_menu)
        screen.update_screen()

        key = get_key()
        
        if key == 'q':
            break
        elif key == 'w':  # Move up
            main_menu.up()
        elif key == 's':  # Move down
            main_menu.down()
        '''elif key in ('\n', '\r'):  # Enter key
            if selected == 0:
        '''

if __name__ == "__main__":
    main()

