import socket
import pyotp
import time

# get the hostname
host = socket.gethostname()
port = 5010  # initiate port no above 1024

def start_Contract_Server():

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
    
        print ("Requesting the corresponding MNO to the user's SIM : " + str(mobile_no))
        break


    # close the connection with wifiAP
    conn.close()
    server_socket.close()


    # make connection with MNO and send mobile number
    MNO_port= 5020
    contract_MNO_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate

    try:
        contract_MNO_socket.connect((host, MNO_port))  # connect to the server
    except IOError:
        print('couldnt connect. Retrying')
        time.sleep(3)
        try:
            contract_MNO_socket.connect((host, MNO_port))
        except IOError:
            print('Could not connect. Retry later.')
            contract_MNO_socket.close()
            exit()

    # send Phone Number to MNO
    while True:
        contract_MNO_socket.send(mobile_no.encode())
        
        # receiev OTP from MNO
        b = b''
        while 1:
            hotp_tmp = contract_MNO_socket.recv(1024)  # receive response
            b += hotp_tmp

        decoded_hotp = json.loads (b.decode('utf-8'))

        print('Received OTP(mno) from MNO: ' + str(decoded_hotp))  # show in terminal
        break

    # close the connection with smart contract
    contract_MNO_socket.close()



if __name__ == '__main__':
    start_Contract_Server()