# config.py

# config.py

import os



# LDAP Configuration from Environment Variables

LDAP_SERVER = os.getenv('LDAP_SERVER', 'ldap://localhost:389')  # Default: localhost LDAP
LDAP_USER_DN = os.getenv('LDAP_USER_DN', 'uid={},ou=users,dc=example,dc=com')
LDAP_BASE_DN = os.getenv('LDAP_BASE_DN', 'dc=example,dc=com')


# Vault Configuration from Environment Variables

VAULT_ADDR = os.getenv('VAULT_ADDR', 'http://localhost:8200')  # Default: localhost Vault
VAULT_TOKEN = os.getenv('VAULT_TOKEN', 'root')  # Default: root token
TOTP_PATH = os.getenv('TOTP_PATH', 'totp')  # Vault TOTP path, default is 'totp'


