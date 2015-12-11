"""
File containing some helpful utility functions that can be used anywhere.
"""
__author__ = 'kevin'

def get_button_xy(button):
    row = int(button / 16)
    column = button - (16 * row)
    return column, row

def get_button_id(x, y):
    return x + (16 * y)
