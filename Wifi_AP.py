import socket
import pyotp
import time
import pickle

# get the hostname
host = socket.gethostname()
port = 5009  # initiate port no above 1024

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


    # make connection with the smart contract and send it the user's mobile number
    contract_port= 5010
    AP_contract_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate

    try:
        AP_contract_socket.connect((host, contract_port))  # connect to the server
    except IOError:
        print('couldnt connect. Retrying')
        time.sleep(3)
        try:
            AP_contract_socket.connect((host, contract_port))
        except IOError:
            print('Could not connect. Retry later.')
            AP_contract_socket.close()
            exit()

    # send Phone Number to smart contract
    while True:
        AP_contract_socket.send(data.encode())
        
        break


    # Retreive OTP(mno) fomr user deveice
    OTP_MNO = conn.recv(1024).decode()

    # Send this OTP to smart contract along with the AUth Flag
    contract_message = {
                        'OTP': OTP_MNO, 
                        'Auth_Flag': True
                       }
    AP_contract_socket.send(pickle.dumps(contract_message))


    # Receive OTP verificatin result from smart contract
    otp_verify = AP_contract_socket.recv(1024)
    decoded_otp_verify = pickle.loads (otp_verify)


    # Send result to user ddeive - UE
    # And grant gateway access
    conn.send(decoded_otp_verify['result'].encode())


    # close the connection with the user device
    conn.close() 
    server_socket.close()

    # close the connection with smart contract
    AP_contract_socket.close()


if __name__ == '__main__':
    start_Wifi_Server()
