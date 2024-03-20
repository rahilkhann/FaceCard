# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "ACa4ee53105ae55a3cae3ed9777da42919"
auth_token = "76d013aaa911d865b8ee9af9bcfcc08e"
verify_sid = "VAe8164f5cbc068f87c8c363eeee3c83b9"
verified_number = "+919871608864"

client = Client(account_sid, auth_token)

verification = client.verify.v2.services(verify_sid) \
  .verifications \
  .create(to=verified_number, channel="sms")
print(verification.status)

otp_code = input("Please enter the OTP:")

verification_check = client.verify.v2.services(verify_sid) \
  .verification_checks \
  .create(to=verified_number, code=otp_code)
print(verification_check.status)