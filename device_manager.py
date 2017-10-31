# Echo server program
import socket
import sys

# Symbolic name meaning all available interfaces
HOST = ''
PORT = 2800

ADDRESS = 0x1234
NAMES = {'parameter_a': 0x1ff03, 'parameter_b':0x0}

initialised = None
connections = None
handles = None

def reset():
    global initialised
    global connections
    global handles
    
    initialised = False
    connections = []
    handles = []
    
def str2int(string):
    if string[:2] == "0x":
        return int(string, 16)
    else:
        return int(string, 10)
    
def main(port_nr):
    global initialised
    global connections
    global handles
    
    reset()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, port_nr))
    while 1:
        s.listen(1)
        conn, addr = s.accept()
        print 'Connected by', addr
        data = ""
        while 1:
            cmd = None
            for i in range(len(data)):
                if data[i] == "\n":
                    cmd = data[:i]
                    data = data[i+1:]
                    break
            if cmd:
                cmd = cmd.lower()
                if cmd == "reset":
                    reset()
                elif cmd == "init":
                    if not initialised:
                        initialised = True
                        conn.sendall("OK\n")
                    else:
                        conn.sendall("ERROR\n")
                elif cmd[:len("connect")] == "connect":
                    params = cmd.split()[1:]
                    if len(params) != 1:
                        conn.sendall("ERROR\n")
                    else:
                        if (str2int(params[0]) == ADDRESS) and (ADDRESS not in connections):
                            connections.append(str2int(params[0]))
                            handle = (str2int(params[0]) * 2) - 3
                            handles.append(handle)
                            conn.sendall("0x%x\n"%handle)
                        else:
                            conn.sendall("ERROR\n")
                elif cmd[:len("disconnect")] == "disconnect":
                    params = cmd.split()[1:]
                    if len(params) != 1:
                        conn.sendall("ERROR\n")
                    else:
                        if str2int(params[0]) in handles:
                            idx = handles.index(str2int(params[0]))
                            handles.pop(idx)
                            connections.pop(idx)
                            conn.sendall("OK\n")
                        else:
                            conn.sendall("ERROR\n")
                elif cmd[:len("get")] == "get":
                    params = cmd.split()[1:]
                    if len(params) != 2:
                        conn.sendall("ERROR\n")
                    else:
                        handle = str2int(params[0])
                        name = params[1]
                        if (handle in handles) and (name in NAMES.keys()):
                            conn.sendall("0x%x\n"%NAMES[name])
                        else:
                            conn.sendall("ERROR\n")
                else:
                    conn.sendall("ERROR\n")
            else:
                try:
                    rcv = conn.recv(1024)
                except:
                    break
                if not rcv: 
                    print "connection closed"
                    break
                data += rcv
                
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        if sys.argv[1] != "-p" or len(sys.argv) != 3:
            print "Usage %s -p <optional port nr>"%str(sys.argv[0])
            exit(1)
        else:
            try:
                port_nr = str2int(sys.argv[2])
            except:
                print "Usage %s -p <optional port nr>"%str(sys.argv[0])
                exit(1)
    else:
        port_nr = PORT
    try:
        main(port_nr)
    except:
        exit(1)
    exit(0)
    