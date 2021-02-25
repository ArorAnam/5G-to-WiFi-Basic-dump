import socket
import time

host = socket.gethostname()  # as both code is running on same pc
port = 5006  # socket server port number

def client_program():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    
    try:
        client_socket.connect((host, port))  # connect to the server
    except IOError:
      print('couldnt connect. Retrying')
      time.sleep(3)
      try:
          s.connect((TCP_IP, TCP_PORT_Hospital))
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

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()