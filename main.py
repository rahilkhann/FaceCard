from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form
import openpyxl

from datetime import datetime
import geocoder
from pydantic import BaseModel

#------------------------------------------------------
import cv2
from simple_facerec import SimpleFacerec
import pandas as pd
from twilio.rest import Client
import os
import time 
import face_recognition
#-----------------------------------------------------


import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, amount REAL)''')


app = FastAPI()

class OTP(BaseModel):
    otp: str



#public dictionary 
info = {}


#public function 
account_sid = "AC8424c4cb0effea41160fd681f696b814"
auth_token = "4eb094945a92f61dd78b9f984848089e"
verify_sid = "VAaeba53c152025def044ab6da1048e545"
client = Client(account_sid, auth_token)

def send_otp(phone_number):
    try:
        verification = client.verify.v2.services(verify_sid) \
                        .verifications \
                        .create(to=phone_number, channel="sms")
        print(verification.status)
    except:
        return "Error sending OTP"
    else:
        return "OTP sent Successfully"
    

def verification_(verified_number,otp_code):
    try:
        verification_check = client.verify.v2.services(verify_sid) \
        .verification_checks \
        .create(to=verified_number, code=otp_code)
        print(verification_check.status)
        return verification_check.status
    except:
        return "Error Verification"

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory for serving HTML files
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_payment_page(request: Request):
    return templates.TemplateResponse("payment_page.html", {"request": request})

@app.get("/payment-options", response_class=HTMLResponse)
async def get_payment_options_page(request: Request):


    print("I am insisde payment-options")
    print("Request :",request)
    return templates.TemplateResponse("payment_options.html", {"request": request})

@app.get("/otp", response_class=HTMLResponse)
async def get_payment_page(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})

@app.get("/final", response_class=HTMLResponse)
async def get_payment_page(request: Request):
    return templates.TemplateResponse("fi.html", {"request": request})

@app.post("/capture_face")
async def capture_face():
    print("I am capture face")
    
    #--------------------------------------------------------------------------
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
    # ... (replace placeholders with your actual credentials)

    # Initialize Twilio client (commented out for security)
    # client = Client(account_sid, auth_token)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Detect faces
        face_locations, face_names = sfr.detect_known_faces(frame)

        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            # Get current timestamp
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            # Get current location (using geocoder library)
            g = geocoder.ip('me')  # Get location based on IP address
            latitude = str(g.lat)
            longitude = str(g.lng)
            current_location = f"Lat: {latitude}, Long: {longitude}"

            # Combine location and timestamp for display
            location_and_timestamp = f"{current_location} - {timestamp}"

            # Display text with name, location, and timestamp
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.putText(frame, location_and_timestamp, (x1, y2 + 15), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        # Check for recognized face and handle accordingly
        if face_names:
            # Recognized face found - handle OTP and close camera
            name = face_names[0]  # Assuming only one face is recognized at a time
            print(f"Recognized face: {name}")

            phone_number = str(get_phone_number(name))
            phone_number = "+91" + phone_number
            print(phone_number)
            info["Phone"] = phone_number

            # Send OTP if face is recognized and phone number is found
            if name != "Unknown":
                if phone_number:
                    # Display bounding box and label for 4 seconds
                    cv2.imshow("Frame", frame)
                    cv2.waitKey(1)  # Wait for a key press to avoid immediate close
                    time.sleep(4)  # Delay for 4 seconds

                    # ... (OTP process using Twilio - commented out)
                    cap.release()  # Close camera
                    cv2.destroyAllWindows()

                    result = send_otp(phone_number)
                    
                    # account_sid = "ACa4ee53105ae55a3cae3ed9777da42919"
                    # auth_token = "daa76931e820e38f7480a78dc43585e5"
                    # verify_sid = "VAe8164f5cbc068f87c8c363eeee3c83b9"

                    # client = Client(account_sid, auth_token)

                    # verification = client.verify.v2.services(verify_sid) \
                    # .verifications \
                    # .create(to=phone_number, channel="sms")
                    # print(verification.status)

                    # otp_code = input("Please enter the OTP:")

                    # verification_check = client.verify.v2.services(verify_sid) \
                    # .verification_checks \
                    # .create(to=phone_number, code=otp_code)
                    # print(verification_check.status)

                    cap.release()  # Close camera
                    cv2.destroyAllWindows()
                    break  # Exit the loop after OTP verification

        # No recognized face or unknown face - keep camera open
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:  # Exit on Esc
            break

    cap.release()
    cv2.destroyAllWindows()

    return {"message": "Face captured successfully"}


@app.post("/_secure")
async def process_secure_otp(otp_data: OTP):

    print("I am otp_secureee")
    print(info['Phone'])
    #--------------------------------------------------------------------
    phone_number = info["Phone"]
    # account_sid = "ACa4ee53105ae55a3cae3ed9777da42919"
    # auth_token = "daa76931e820e38f7480a78dc43585e5"
    # verify_sid = "VAe8164f5cbc068f87c8c363eeee3c83b9"

    # client = Client(account_sid, auth_token)

    # Retrieve the OTP from the request body
    otp_code = otp_data.otp
    print(otp_code)

    # verification_check = client.verify.v2.services(verify_sid) \
    # .verification_checks \
    # .create(to=phone_number, code=otp_code)
    # print(verification_check.status)

    result = verification_(phone_number,otp_code)
    
    # otp = otp_data.otp
    # print(otp)

    # Dummy validation (you should implement your own validation logic)
    # expected_otp = "123456"  # Example expected OTP
    if result== 'approved':
        print("I am approved")
        return {"message": "OTP processed successfully"}
        
    elif result=="pending":
        return {"message": "OTP verification unsuccessfull"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")



@app.post("/process-payment")
async def process_payment(amount: float =Form(...)):
    # Insert payment record into the database
    print("the amount is :",amount)
    print("satwik")
    cursor.execute("INSERT INTO payments (amount) VALUES (?)", (amount,))
    conn.commit()
    return {"message": "Payment processed successfully"}

@app.get("/payments")
async def get_payments():
    # Retrieve all payments from the database
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()
    return {"payments": payments}