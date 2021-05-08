import socket
import pyotp
import time
import pickle

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
        # b = b''
        # while 1:
        #     hotp_tmp = contract_MNO_socket.recv(1024)  # receive response
        #     b += hotp_tmp

        # decoded_hotp = json.loads (b.decode('utf-8'))

        hotp = contract_MNO_socket.recv(1024)
        decoded_hotp = pickle.loads (hotp) 

        # print('Received OTP(mno) from MNO: ' + str(decoded_hotp))  # show in terminal
        break

    # close the connection with smart contract
    contract_MNO_socket.close()


    # Receive OTP(mno) & Auth from Wifi
    otp_dict = conn.recv(1024)
    decoded_otp_dict = pickle.loads (otp_dict)

    # check if OTP_Check_1 = OTP_Check_2
    if decoded_hotp['OTP'] == decoded_otp_dict['OTP'] and decoded_otp_dict['Auth_Flag'] and decoded_hotp['Auth_Flag']:
       print ("Smart Contract Executed !!")

       # send confirmation to WifiAP
       result_json = {'result': 'Smart Contract Execution Successful. Internet Access Granted.',
                    'Access': True}
       conn.send(pickle.dumps (result_json))

    else:
        print ("OTP do not match ! Try Again.")
        result_json = {'result': 'Smart Contract Execution Successful. Internet Access Denied.',
                    'Access': False}
        conn.send(pickle.dumps (result_json))


    # close the connection with wifiAP
    conn.close()
    server_socket.close()


if __name__ == '__main__':
    start_Contract_Server()