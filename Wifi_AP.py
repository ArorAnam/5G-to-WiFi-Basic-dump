import socket
import pyotp
import time

# get the hostname
host = socket.gethostname()
port = 5006  # initiate port no above 1024

def start_Wifi_Server():

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
            data = conn.recv(1024).decode()
        except ConnectionReseteError:
            print("Issue in reading data.")
            continue
    
        print ("Mobile number of connected user: " + str(data))

        # generate a OTP for 30 secs
        totp = pyotp.TOTP('base32secret3232')
        
        # OTP Byte
        totpByte = totp.now().encode()
        # Send the OTP to User device
        conn.send(totpByte)
        break

    while 1:
        try:
            otp = conn.recv(1024).decode()
        except ConnectionReseteError:
            print("Issue in reading data.")
            continue

        if totp.verify(otp):
            conn.send('Authenticaiton Successfull !!'.encode())
        else:
            conn.send('Authentication failed !!'.encode())
        break

    conn.close()  # close the connection
    server_socket.close()


if __name__ == '__main__':
    start_Wifi_Server()
