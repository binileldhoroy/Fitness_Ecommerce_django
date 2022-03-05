from twilio.rest import Client
from decouple import config

def otp_login_code(request,number) :
    
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    verification = client.verify \
                    .services(config('messaging_service_sid')) \
                    .verifications \
                    .create(to=number, channel='sms')

    print(verification.status)
    return verification.status

def otp_verify_code(request,number,otp) :
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
                        .services(config('messaging_service_sid')) \
                        .verification_checks \
                        .create(to= number, code= str(otp))

    return verification_check.status