# app.py
import os
import qrcode
import base64
from io import BytesIO
import pyotp
import json
import requests
from flask import Flask, render_template, request, session
from config import LDAP_SERVER, LDAP_USER_DN, LDAP_BASE_DN, VAULT_ADDR, VAULT_TOKEN, TOTP_PATH

app = Flask(__name__)
app.secret_key = os.urandom(24)


# Vault headers for authentication
vault_headers = {
    'X-Vault-Token': VAULT_TOKEN
}


def authenticate_ldap(username, password):
    """Authenticate the user with LDAP server."""
    from ldap3 import Server, Connection, ALL, SIMPLE
    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        user_dn = LDAP_USER_DN.format(username)
        conn = Connection(server, user_dn, password, auto_bind=True, authentication=SIMPLE)
        return conn.bind()
    except Exception as e:
        print(f"LDAP authentication failed: {e}")
        return False


def get_totp_key(username):
    """Retrieve TOTP key for a user from Vault using the API."""
    try:
        path = f"{VAULT_ADDR}/v1/{TOTP_PATH}/keys/{username}"
        print(f"Vault Path: {path}")
        response = requests.get(path, headers=vault_headers)
        if response.status_code == 200:
            totp_data = response.json().get('data', {})
            return totp_data.get('url'), True
        else:
            print(f"Error retrieving TOTP key: {response.text}")
    except Exception as e:
        print(f"Error retrieving TOTP key from Vault: {e}")
    return None, False

def verify_totp(otp,username):
    """Verify OTP using Vault API."""
    try:
        path = f"{VAULT_ADDR}/v1/{TOTP_PATH}/code/{username}"
        print(f"Vault Path: {path}")
        data = {
            "code": otp
        }
        response = requests.post(path, headers=vault_headers, json=data)
        print(f" Verify TOTP: {response.text}")
        if response.status_code == 200:
            totp_data = response.json().get('data', {})
            print(f"totp isValid : {totp_data}")
            if totp_data['valid']: 
                return True
            else:
                return False
        else:
            print(f"Error validating TOTP: {response.text}")
    except Exception as e:
        print(f"Error validating TOTP from Vault: {e}")
    return None


def create_totp_key(username):
    """Create a new TOTP key for a user in Vault using the API."""
    try:
        path = f"{VAULT_ADDR}/v1/{TOTP_PATH}/keys/{username}"
        print(f"Vault Path: {path}")
        data = {
            "generate": True,
            "issuer": "MyApp",
            "account_name": username
        }
        print(f"Payload: {data}")
        response = requests.post(path, headers=vault_headers, json=data)
        print(f"response: {response.text}")
        key  = response.json() 
        print(json.dumps(key, indent=4))
        if response.status_code == 200:
            # Fetch the key's URL after creation
            return key['data']['barcode']
        else:
            print(f"Error creating TOTP key: {response.text}")
    except Exception as e:
        print(f"Error creating TOTP key in Vault: {e}")
    return None


@app.route('/')

def index():
    if 'username' in session:
        return render_template('index.html', otp_required=True)
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    

    # Authenticate with LDAP
    if not authenticate_ldap(username, password):
        return "Invalid credentials", 403

    # Check if user already has TOTP key
    totp_url, key_exists = get_totp_key(username)
    if not key_exists:
        # Create TOTP key and generate QR code for user
        totp_url = create_totp_key(username)
        if totp_url:
            return render_template('index.html', qr_image=totp_url, data=totp_url, qr_code=True)
        else:
            return "Error creating TOTP key", 500


    # If TOTP key exists, verify OTP
    otp = request.form.get('otp')
    if otp:
        totp = verify_totp(otp,username) 
        print(f" Verify TOTP in login: {totp}")
        if totp:
            session['username'] = username
            return "Login successful!"
        else:
            return "Invalid OTP", 403
    return render_template('index.html', otp_required=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

