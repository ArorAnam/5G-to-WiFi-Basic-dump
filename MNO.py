import socket
import pyotp
import time
import json

# get the hostname
host = socket.gethostname()
port = 5020  # initiate port no above 1024

def start_MNO_Server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(5)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    
    
    while 1:
        try:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            mobile_no = conn.recv(1024).decode()
        except ConnectionReseteError:
            print("Issue in reading data.")
            continue
    
        print ("Generating& sending OTP(mno) to the user's SIM : " + str(mobile_no))

        # Generate OTP(mno) for 30 secs
        hotp = pyotp.HOTP('base32secret3232')
        
        # OTP Byte
        hotpByte = hotp.at(4096).encode()

        # Send OTP back to smart contract
        # Also set AuthMNO = 1
        MNO_message = {
                        'OTP': hotp.at(4096), 
                        'Auth_Flag': True
                      }
        b = json.dumps(MNO_message).encode('utf-8')
        conn.sendall(b)

        break


    # close the connection with wifiAP
    conn.close()
    server_socket.close()


    # make connection with user device and send OTP(mno)
    UE_port= 5030
    MNO_UE_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate

    try:
        MNO_UE_socket.connect((host, UE_port))  # connect to the server
    except IOError:
        print('couldnt connect. Retrying')
        time.sleep(3)
        try:
            MNO_UE_socket.connect((host, UE_port))
        except IOError:
            print('Could not connect. Retry later.')
            MNO_UE_socket.close()
            exit()

    # send 
    while True:
        MNO_UE_socket.send(hotpByte)
        
        break

    # close the connection with smart contract
    MNO_UE_socket.close()



if __name__ == '__main__':
    start_MNO_Server()