import socket
import pyotp
import time
import json
import pickle

import os
from flask import Flask, request, render_template, session, flash, redirect, url_for
from dotenv import load_dotenv
from twilio.rest import Client
import requests

# get the hostname
host = socket.gethostname()
port = 5020  # initiate port no above 1024

app = Flask(__name__)
app.secret_key = 'secret'
twilio_client = Client(str(os.getenv('TWILIO_ACCOUNT_SID')),
                       str(os.getenv('TWILIO_AUTH_TOKEN')))
generateotp_url = 'https://api.generateotp.com/'


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('generate.html')
    phone_number = request.form['phone_number']
    channel = request.form['channel']
    error = None
    if not phone_number:
        error = 'Phone Number is required'
    if channel != 'voice' and channel != 'sms':
        error = 'Invalid channel'
    if error is None:
        formatted_phone_number = phone_number[1:]
        session['phone_number'] = formatted_phone_number
        otp_code = make_otp_request(formatted_phone_number)
        if otp_code:
            send_otp_code(phone_number, otp_code, channel)
            flash('OTP has been generated successfully', 'success')
            return redirect(url_for('validate'))
        error = 'Something went wrong, could not generate OTP'
    flash(error, 'danger')
    return redirect(url_for('generate'))


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'GET':
        return render_template('validate.html')
    otp_code = request.form['otp_code']
    error = None
    if not otp_code:
        error = 'OTP code is required'
    if 'phone_number' in session:
        phone_number = session['phone_number']
    else:
        error = 'Please request a new OTP'
    if error is None:
        phone_number = session.get('phone_number')
        status, message = verify_otp_code(otp_code, phone_number)
        if status is True:
            flash(message, 'success')
            del session['phone_number']
            return redirect(url_for('validate'))
        elif status is False:
            flash(message, 'danger')
            return redirect(url_for('validate'))
        error = 'Something went wrong, could not validate OTP'
    flash(error, 'danger')
    return redirect(url_for('generate'))


def make_otp_request(phone_number):
    r = requests.post(f"{generateotp_url}/generate",
                      data={'initiator_id': phone_number})
    if r.status_code == 201:
        data = r.json()
        otp_code = str(data["code"])
        return otp_code


def send_otp_code(phone_number, otp_code, channel):
    if channel == 'voice':
        return send_otp_via_voice_call(phone_number, otp_code)
    if channel == 'sms':
        return send_otp_via_sms(phone_number, otp_code)


def send_otp_via_voice_call(number, code):
    outline_code = split_code(code)
    call = twilio_client.calls.create(
        twiml=f"<Response><Say voice='alice'>Your one-time password is {outline_code}</Say><Pause length='1'/><Say>Your one-time password is {outline_code}</Say><Pause length='1'/><Say>Goodbye</Say></Response>",
        to=f"{number}",
        from_=os.getenv('TWILIO_NUMBER')
    )


def send_otp_via_sms(number, code):
    messages = twilio_client.messages.create(to=f"{number}", from_=os.getenv(
        'TWILIO_NUMBER'), body=f"Your one-time password is {code}")


def split_code(code):
    return " ".join(code)


def verify_otp_code(otp_code, phone_number):
    r = requests.post(f"{generateotp_url}/validate/{otp_code}/{phone_number}")
    if r.status_code == 200:
        data = r.json()
        status = data["status"]
        message = data["message"]
        return status, message
    return None, None


def homepage():
    return redirect(url_for('generate'))


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
        # b = json.dumps(MNO_message).encode('utf-8')
        # conn.sendall(b)

        conn.send(pickle.dumps(MNO_message))

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
    #app.run()