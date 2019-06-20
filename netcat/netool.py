
import sys
import socket
import argparse
import threading
import subprocess

"""
setparser()
   Inicializa o parser usado para a coleta de argumentos
"""

def setparser():
        parser = argparse.ArgumentParser(description='Netool')

        parser.add_argument('-l', '--listen', action='store_true',
                            help='listen on [host]:[port] for incoming connections')
        parser.add_argument('-e', '--execute',
                            help='execute the given file upon connection')
        parser.add_argument('-c', '--command', action='store_true',
                            help='initialize a command shell')
        parser.add_argument('-u', '--upload_dest',
                            help='upon receiving connection, upload a file and write to [destination]')
        parser.add_argument('-t', '--target',
                            default='0.0.0.0', # todas as interfaces
                            help='target host to be affected')
        parser.add_argument('-p', '--port',
                            required=True, type=int, choices=range(0,65536),
                            help='port to be affected')

        return parser

# ---------------------------------------------------------------------------

"""
client_sender(str buffer)
   Envia os dados coletados do stdin pela rede
"""

def client_sender(buffer):

    global state

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((state.target, state.port))

        if buffer:
            client_socket.send(buffer)

        while True:
            recv_len = 1
            resp = ''

            while recv_len:
                data = client_socket.recv(4096).decode('utf-8')
                recv_len = len(data)

                resp += data

                if recv_len < 4096:
                    break
                
            print(resp)

            buffer = input('>')+'\n'
            client_socket.send(buffer.encode('utf-8'))

    except Exception as e:
        print("[!] Exception! Exiting...")
        print("[!] Error details: {}".format(e))

        client_socket.close()

# ---------------------------------------------------------------------------

"""
server_loop()
   Cria um server pra receber requisicoes
"""

def server_loop():

    global state

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((state.target, state.port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket,))
        client_thread.start()

    
# ---------------------------------------------------------------------------
  
"""
run_command(str comm)
   Roda o comando recebido no os local
"""

def run_command(comm):

    global state

    try:
        output = subprocess.check_output(comm.rstrip(),
                                         stderr=subprocess.STDOUT,
                                         shell=True)
    except:
        output = 'Failed to execute command.\r\n'.encode('utf-8')

    return output
    
# ---------------------------------------------------------------------------

  
"""
client_handler(socket client_socket)
   Lida com as acoes escolhidas pelo usuario - upload, execute e command
"""

def client_handler(client_socket):

    global state

    if state.upload_dest:
            
        file_buf = ''

        while True:
            data = client_socket.recv(1024).decode('utf-8')

            if not data:
                break
            else:
                file_buf += data

        try:
            with open(state.upload_dest, 'wb') as file_descriptor:
                file_descriptor.write(file_buf)

            client_socket.send('Successfully saved file to {}\r\n'.format(state.upload_dest))
        except:
            client_socket.send('Failed to save file to {}\r\n'.format(state.upload_dest))

    if state.execute:
        output = run_command(state.execute)
        client_socket.send(output)

    if state.command:    
        
        while True:
            client_socket.send('Netool:$ '.encode('utf-8'))
            cmd_buf = ''

            while '\n' not in cmd_buf:
                cmd_buf += client_socket.recv(1024).decode('utf-8')

            resp = run_command(cmd_buf)
            client_socket.send(resp)
# ---------------------------------------------------------------------------


# Inicializando o parser
parser = setparser()
state = parser.parse_args()

def main():
    global state

    buffer = sys.stdin.read()
    client_sender(buffer.encode('utf-8'))

    if state.listen:
        server_loop()

if __name__ == '__main__':
    main()
