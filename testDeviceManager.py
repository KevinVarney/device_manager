#! python2
# testDeviceManager.py - Test the device_manager

import socket, sys

DEFAULT_PORT = 2800

# Send and display message to the device manager and receive and display the response
def sendMessage(message):
    global sock
    print >> sys.stdout, 'TX: ' + message
    message += '\n'
    sock.sendall(message)
    reply = sock.recv(16).rstrip('\n')
    print >> sys.stdout, 'RX: ' + reply
    return reply 

# Check and display whether the response is as expected
def checkReply(reply, expectedReply):
    if reply != expectedReply:
        print >> sys.stderr, 'FAIL\n'
    else:
        print >> sys.stdout, 'PASS\n'
    

def sendValidCommand(message):
    checkReply(sendMessage(message),'OK')

def sendInvalidCommand(message):
    checkReply(sendMessage(message),'ERROR')

# Check response to a valid data request is a hexadecimal number
def sendValidRequest(message):
    reply = sendMessage(message)
    try:
        int(reply,16)
        print >> sys.stdout, 'PASS\n'
    except:
        print >> sys.stderr, 'FAIL\n'
    return reply

# Check response to an invalid data request is ERROR
def sendInvalidRequest(message):
    sendInvalidCommand(message)
    return ''

def performTests():
    # Causes the device_manager to crash later on
    #print >> sys.stdout, 'Attempt to connect to remote device before initialising the device manager'  
    #sendInvalidCommand('CONNECT 0x1234')

    print >> sys.stdout, 'Initialise device manager'
    sendValidCommand('INIT')

    print >> sys.stdout, 'Send an extra initialise command'
    sendInvalidCommand('INIT')

    print >> sys.stdout, 'Attempt to connect to a non-existant remote device'
    sendInvalidCommand('CONNECT 0x1233')

    print >> sys.stdout, 'Connect to an existing remote device'
    handle = sendValidRequest('CONNECT 0x1234')

    print >> sys.stdout, 'Get parameter A'
    parameter = sendValidRequest('GET ' + handle + ' parameter_a')

    print >> sys.stdout, 'Get parameter B'
    parameter = sendValidRequest('GET ' + handle + ' parameter_b')

    print >> sys.stdout, 'Attempt to get non-existant parameter C'
    parameter = sendInvalidRequest('GET ' + handle + ' parameter_c')

    print >> sys.stdout, 'Attempt to get parameter A using an invalid handle'
    invalidHandle = hex(int(handle,16)+1)
    parameter = sendInvalidRequest('GET ' + invalidHandle + ' parameter_a')

    print >> sys.stdout, 'Get parameter A - swap uppercase and lowercase'
    parameter = sendValidRequest('get ' + handle.upper() + ' PARAMETER_A')

    print >> sys.stdout, 'Attempt to disconnect from a non-existant remote device'
    sendInvalidCommand('DISCONNECT ' + invalidHandle)

    print >> sys.stdout, 'Disconnect from the remote device'
    sendValidCommand('DISCONNECT ' + handle)

# Set port number to command line argument if there is one, otherwise use default
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    port = DEFAULT_PORT

# Connect to the device manager
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost',port)
print >> sys.stdout, 'connecting to %s port %s\n' % server_address
sock.connect(server_address)

performTests()

print >> sys.stdout, 'Reset the remote device to the initial state'
sock.sendall('RESET\n')

# Close the socket
print >> sys.stdout, 'closing the socket'    
sock.close()
