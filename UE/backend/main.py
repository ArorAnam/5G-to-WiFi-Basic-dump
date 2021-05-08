import uvicorn

import socket
import time
import json

host = socket.gethostname()  # as both code is running on same pc
port = 5009  # socket server port number

def client_program():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    
    try:
        client_socket.connect((host, port))  # connect to the server
    except IOError:
      print('couldnt connect. Retrying')
      time.sleep(3)
      try:
          client_socket.connect((host, port))
      except IOError:
          print('Could not connect. Retry later.')
          client_socket.close()
          exit()

    message = input("Phone Number -> ")  # take input

    while True:
        # send Phone Number
        client_socket.send(message.encode())
        
        # receiev OTP from Wifi AP
        totp = client_socket.recv(1024).decode()  # receive response

        print('Received OTP from server: ' + totp)  # show in terminal
        break

    # Take OTP:
    message = input("Enter OTP -> ")

    while True:
        client_socket.send(str(totp).encode())

        # receive auth success / failure
        auth_result = client_socket.recv(1024).decode()

        print('User device authentication : ' + auth_result)
        break


    # Recieve OTP(mno) from MNO directly
    MNO_port = 5030

    UE_MNO_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    UE_MNO_socket.bind((host, MNO_port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    UE_MNO_socket.listen(5)
    conn, address = UE_MNO_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    

    while 1:
        try:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            OTP_MNO = conn.recv(1024).decode()
        except ConnectionReseteError:
            print("Issue in reading data.")
            continue
    
        print ("OTP Received from MNO : " + OTP_MNO)
        break


    # close the connection with MNO
    conn.close()
    UE_MNO_socket.close()

    # Take OTP:
    mno_otp = input("Enter OTP -> ")

    # Send the otp received from to WiFi
    # Basically entering it on a page sent by WiFi
    client_socket.send(str(mno_otp).encode())

    # Receive result of OTP verification from Wifi
    execution_result = client_socket.recv(1024).decode()

    print (execution_result)

    # close connection with Wifi
    client_socket.close()


if __name__ == '__main__':
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
    client_program()