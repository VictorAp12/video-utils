"""
This module contains utility functions for working with tkinter windows.
"""

import tkinter as tk


def center_window(
    window: tk.Tk | tk.Toplevel, master: tk.Tk | tk.Toplevel | None = None
) -> None:
    """
    Center the given window on the screen, or relative to the provided master window.

    :param window: The window to be centered.
    :param master: The master window relative to which the given
        window should be centered. Defaults to None.

    :return: None.
    """

    window.update_idletasks()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - window_width) / 2
    y = (screen_height - window_height) / 2

    if master:
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - window_width) / 2
        y = master.winfo_y() + (master.winfo_height() - window_height) / 2

    window.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")


def print_window_size(event: tk.Event) -> None:
    """
    A method to print the window size based on the event parameters.
    In your tkinter window code, bind this method to the window's event
    Example:
        configure_binding = self.root.bind("<Configure>", print_window_size)

    :param event (tk.Event): The event object containing width and height.

    :return: None.
    """
    print(event.width, event.height)
