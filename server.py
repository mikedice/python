import threading
import queue
import socket
import select
import queue
import serial
import sys

# Global connectedClient list shared between Network
# listener thread and the Serial Port thread
connectedClients = []

# line is a comma seperated string with two integer fields
def readValues(serialPort):
    line = serialPort.readline()
    try:
        dec = line.decode('utf-8')
    except:
        return('',0,0)

    stringvals =  dec.replace('\n','').split(',')
    
    # We may sometimes get a partial line, like when the program first
    # opens the serial port. If this happens we can just return and
    # ignore that line
    if len(stringvals) != 3:
        return('',0,0)

    # Return a tuple that contains our fields
    return (stringvals[0], int(stringvals[1]), int(stringvals[2]))

# Open the serial port. You can specify the port's
# operating system path using the first arguemnt to the script.
# or a default will be used.
def openSerialPort():
    portPath = '/dev/ttyACM1'
    if len(sys.argv) > 1:
        portPath = sys.argv[1]
    serialPort = serial.Serial(portPath)
    return serialPort

class ConnectedClient:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.work_queue = queue.Queue()

def client_thread_procedure(connectedClient):
    while True:
        data = connectedClient.work_queue.get()
        connectedClient.client_socket.send(data.encode('utf-8'))
    
    print('client thread is closing client socket')
    connectedClient.client_socket.close()
    return

def serial_port_thread_procedure():
    count = 0    
    serialPort = openSerialPort()
    while True:
        vals = readValues(serialPort)
        data = '{},{:d},{:d}'.format(vals[0], vals[1], vals[2])
        print(count, data)
        count = count+1
        for client in connectedClients:
            client.work_queue.put('{},{}\n'.format(count,data))
        if count > 10000:
            count = 0
                    


# Main Program
# Start a listening socket to listen on the network. Then create a 
# program loop which uses socket polling to check the listening 
# socket for new incoming connections. For new connections
# create game client instances so we can send data to them. The
# main program loop will also poll the serial port for information
# coming in from the Arduino. Any information received over the 
# serial port will be put in the client queues of any previously
# connected clients so they can transfer the data over the network
#
if __name__ == "__main__":
    PORT = 7654
    HOST = ''
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.setblocking(0)
    serversocket.bind((HOST, PORT))
    serversocket.listen(5)
    serialThread = threading.Thread(target=serial_port_thread_procedure,
                                    daemon=True)
    serialThread.start()

    try:
        print('socket is listening')
        while True:
            potential_readers=[serversocket]
            potential_writers=[]
            potential_errs=[]
            timeout=0.100
            ready_to_read,ready_to_write,in_error = \
                    select.select(potential_readers,
                            potential_writers,
                            potential_errs,
                            timeout)
            if serversocket in ready_to_read:
                print('accept ready')
                (new_client,new_client_address)=serversocket.accept()
                print('accepted connection from',new_client_address)
                client = ConnectedClient(new_client, new_client_address)
                thread = threading.Thread(target=client_thread_procedure,
                        args=(client,),
                        daemon=True)
                connectedClients.append(client)
                thread.start()
                    
    except KeyboardInterrupt:
        print('\nclosing server socket')
        serversocket.close()
        print('bye')
