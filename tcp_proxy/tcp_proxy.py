#!/usr/bin/python

# Simple TCP Proxy
# Author: Franco Barpp Gomes (https://github.com/Hyodar)

# -*- coding: utf-8 -*-

# Imported modules
# -----------------------------------------------------------------------------

import argparse
import socket
import sys
import threading

# Functions
# -----------------------------------------------------------------------------

"""
server_loop()
    Creates a socket and creates threads to deal with connections
"""

def server_loop(local_host, local_port, remote_host, remote_port, receive_first, timeout):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("[!] Failed to listen to {}:{}".format(local_host, local_port))
        print("[!] Error details: {}".format(e))
        sys.exit(0)
    
    print("[*] Listening on {}:{}...".format(local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print("[->] Received incoming connection from {}:{}".format(addr[0],
                                                                    addr[1]))

        # creates a thread to talk with the remote host
        proxy_thread = threading.Thread(target=proxy_handler, args=(
            client_socket, remote_host, remote_port, receive_first, timeout
        ))
        proxy_thread.start()

# -----------------------------------------------------------------------------

"""
proxy_handler(client_socket: socket, remote_host: str, remote_port: int,
              receive_first: bool, timeout: int)
    Main proxy logic
"""

def proxy_handler(client_socket, remote_host, remote_port, receive_first, timeout):

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buff = receive_from(remote_socket, timeout)
        hexdump(remote_buff)

        remote_buff = response_handler(remote_buff)

        if remote_buff:
            print("[<-] Sending {} bytes to localhost...".format(len(remote_buff)))
            client_socket.send(remote_buff)

    # loop: reads from local -> sends to remote -> sends to local
    while True:
        
        # Reading from localhost
        local_buff = receive_from(client_socket, timeout)

        if local_buff:
            print("[->] Received {} bytes from localhost.".format(len(local_buff)))
            hexdump(local_buff)

            # Sending local buffer to request handler
            local_buff = request_handler(local_buff)

            # Sending off the data to the remote host
            remote_socket.send(local_buff)
            print("[->] Sent to remote.")

        # Receiving back the response
        remote_buff = receive_from(remote_socket, timeout)

        if remote_buff:

            print("[<-] Received {} bytes from remote.".format(len(remote_buff)))
            hexdump(remote_buff)

            remote_buff = response_handler(remote_buff)

            client_socket.send(remote_buff)
            print("[<-] Sent to localhost.")

        if not local_buff or not remote_buff:
            print("[*] No more data. Closing connections...")

            client_socket.close()
            remote_socket.close()

            break

# -----------------------------------------------------------------------------

"""
hexdump(src: bytes, length: int)
    Dumps the src as hex in a pretty way
    source: http://code.activestate.com/recipes/142812-hex-dumper/ (comments)
"""

def hexdump(src, length=10):

    src = src.decode('utf-8')

    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = ''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
       result.append( "%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return '\n'.join(result)

# -----------------------------------------------------------------------------

"""
receive_from(connection: socket, timeout: int)
    Reads the buffer until empty and returns it
"""

def receive_from(connection, timeout):

    buff = b''

    connection.settimeout(timeout)

    # beautiful way of reading it until there's no more data
    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break
            
            buff += data
    except:
        pass
    
    return buff

# -----------------------------------------------------------------------------

"""
request_handler(buff: bytes):
    Modifies and returns the request packets destined to remote host
"""

def request_handler(buff):

    # packet modifications

    return buff

# -----------------------------------------------------------------------------

"""
response_handler(buff: bytes):
    Modifies and returns the response packets destined to local host
"""

def response_handler(buff):

    # packet modifications

    return buff

# -----------------------------------------------------------------------------

"""
setparser()
   Sets an argparser to receive argument data
"""

def setparser():

        parser = argparse.ArgumentParser(description='Simple TCP Proxy')

        parser.add_argument('-rf', '--receivefirst', action='store_true',
                            help='first receive data before sending')
        parser.add_argument('-lh', '--localhost', default='127.0.0.1',
                            help='localhost address')
        parser.add_argument('-lp', '--localport',
                            default=9000, type=int, choices=range(0,65536),
                            help='local port number')
        parser.add_argument('-rh', '--remotehost',
                            help='remote host address')
        parser.add_argument('-rp', '--remoteport', 
                            type=int, choices=range(0,65536),
                            help='remote port number')
        parser.add_argument('-t', '--timeout', 
                            type=int, default=2,
                            help='connection timeout (default 2s)')

        return parser

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():

    parser = setparser()
    args = parser.parse_args()

    server_loop(args.localhost, args.localport, args.remotehost,
                args.remoteport, args.receivefirst, args.timeout)

if __name__ == '__main__':
    main()