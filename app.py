import os
import sys
import termios
import tty
import threading
import time
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
screen = ""

def cursor_to(row, col):
    return f"\033[{row};{col}H"

def draw_block(row, col):
    str = cursor_to(row, col) + block
    return str

def draw_char(row, col, char):
    str = cursor_to(row, col) + char
    return str

def draw_rect(row, col, width, height):
    str = cursor_to(row, col)
    for _ in range(width):
        str += block

    for i in range(height):
        current_row = row + 1 + i
        str += cursor_to(current_row, col)
        str += block
        str += cursor_to(current_row, col + width - 1)
        str += block

    str += cursor_to(row + height + 1, col)
    for _ in range(width):
        str += block

    return str

def get_center_row(height):
    return (int) (size.lines / 2 - height / 2)

def get_center_col(width):
    return (int) (2 + size.columns / 2 - width / 2)

def set_fg_col(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def set_bg_col(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

def add_screen(value):
    global screen
    screen += value 

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
def clear_screen():
    print("\033[2J\033[H", end='')

# Draw menu with selection highlighting
def draw_menu(selected_index):
    clear_screen()
    options = ["Option 1", "Option 2", "Quit"]
    print("=== Basic Python TUI ===\n")
    for i, option in enumerate(options):
        prefix = "=> " if i == selected_index else "   "
        print(f"{prefix}{option}")

def main():
    selected = 0
    options = 3
    while True:
        draw_menu(selected)
        key = get_key()
        
        if key == 'q' or (key == '\n' and selected == options-1):
            break
        elif key == 'w':  # Move up
            selected = (selected - 1) % options
        elif key == 's':  # Move down
            selected = (selected + 1) % options
        elif key in ('\n', '\r'):  # Enter key
            if selected == 0:
                print("\nYou selected Option 1")
            elif selected == 1:
                print("\nYou selected Option 2")
            print("Press any key to continue... yurt█")
            get_key()
            draw_block(10, 10)

if __name__ == "__main__":
    #main()
    clear_screen()
    width = size.columns - 10
    height = size.lines - 10
    screen = ""
    
    add_screen(set_fg_col(55, 100, 50))
    add_screen("hello")
    add_screen(draw_rect(get_center_row(height), get_center_col(width), width, height))
    print(screen)

    ascii_banner = pyfiglet.figlet_format("Title Bann")
    print(ascii_banner)
