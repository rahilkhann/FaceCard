import cv2
from simple_facerec import SimpleFacerec
import pandas as pd
from twilio.rest import Client
import os
import time 


# Load customer data from Excel
customer_data = pd.read_excel("customer_data.xlsx")
customer_data['Cust_ID'] = customer_data['Cust_ID'].astype(str)
print(customer_data.dtypes)


def get_phone_number(cust_id):
    row = customer_data[customer_data['Cust_ID'] == cust_id]
    if not row.empty:
        return str(row.iloc[0]['Phone'])
    else:
        return None


# Face recognition setup
sfr = SimpleFacerec()
sfr.load_encoding_images("images/")

# Twilio credentials (replace with your own)
account_sid = "ACa4ee53105ae55a3cae3ed9777da42919"  # Replace with your Twilio account SID
auth_token = "76d013aaa911d865b8ee9af9bcfcc08e"   # Replace with your Twilio auth token
verify_sid = "VAe8164f5cbc068f87c8c363eeee3c83b9"   # Replace with your Twilio Verify service SID

# Initialize Twilio client
client = Client(account_sid, auth_token)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Detect faces
    face_locations, face_names = sfr.detect_known_faces(frame)
    
    # Check for recognized face and handle accordingly
    if face_names:
        # Recognized face found - handle OTP and close camera
        name = face_names[0]  # Assuming only one face is recognized at a time
        print(f"Recognized face: {name}")
        print(type(name))
        phone_number = str(get_phone_number(name))
        phone_number = "+91"+phone_number
        print(phone_number)

        # Send OTP if face is recognized and phone number is found
        if phone_number:
            cap.release()  # Close camera
            cv2.destroyAllWindows()

            

            account_sid = "ACa4ee53105ae55a3cae3ed9777da42919"
            auth_token = "daa76931e820e38f7480a78dc43585e5"
            verify_sid = "VAe8164f5cbc068f87c8c363eeee3c83b9"
            verified_number = "+919963293874"

            client = Client(account_sid, auth_token)

            verification = client.verify.v2.services(verify_sid) \
            .verifications \
            .create(to=phone_number, channel="sms")
            print(verification.status)

            otp_code = input("Please enter the OTP:")

            verification_check = client.verify.v2.services(verify_sid) \
            .verification_checks \
            .create(to=phone_number, code=otp_code)
            print(verification_check.status)

            break  # Exit the loop after OTP verification

    # No recognized face or unknown face - keep camera open
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:  # Exit on Esc
        break

cap.release()
cv2.destroyAllWindows()