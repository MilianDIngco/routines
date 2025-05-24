import os
import sys
import termios
import tty

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
            print("Press any key to continue... yurt")
            get_key()

if __name__ == "__main__":
    main()
