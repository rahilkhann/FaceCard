import cv2
from simple_facerec import SimpleFacerec
import pandas as pd
from twilio.rest import Client

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
account_sid = "YOUR_ACCOUNT_SID"  # Replace with your Twilio account SID
auth_token = "YOUR_AUTH_TOKEN"   # Replace with your Twilio auth token
verify_sid = "YOUR_VERIFY_SID"   # Replace with your Twilio Verify service SID

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
        phone_number = get_phone_number(name)
        print(phone_number)

        # Send OTP if face is recognized and phone number is found
        if phone_number:
            cap.release()  # Close camera
            cv2.destroyAllWindows()

            verification = client.verify \
                                      .services(verify_sid) \
                                      .verifications \
                                      .create(to=phone_number, channel="sms")
            print(f"Verification status: {verification.status}")

            # User input for OTP and verification
            otp_code = input("Enter the OTP sent to your phone: ")

            verification_check = client.verify.v2.services(verify_sid) \
                                          .verification_checks \
                                          .create(to=phone_number, code=otp_code)
            print(f"Verification check status: {verification_check.status}")

            if verification_check.status == "approved":
                print("OTP verified successfully!")
                # Add your actions here after successful verification (e.g., access granted, door opened)
            else:
                print("Invalid OTP. Please try again.")

            break  # Exit the loop after OTP verification

    # No recognized face or unknown face - keep camera open
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1)
    if key == 27:  # Exit on Esc
        break

cap.release()
cv2.destroyAllWindows()