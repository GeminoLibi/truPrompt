#!/usr/bin/env python3
"""
Simple Credential Encoding System for dataPull Agent
Uses Fernet symmetric encryption for secure credential storage
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from datetime import datetime
import getpass

class SimpleCredentialEncoder:
    """Simple secure credential encoding and decoding system"""
    
    def __init__(self, key_dir="credentials"):
        """Initialize the credential encoder"""
        self.key_dir = key_dir
        self.key_file = os.path.join(key_dir, "encryption_key.key")
        self.credentials_file = os.path.join(key_dir, "encrypted_credentials.json")
        
        # Create directory if it doesn't exist
        os.makedirs(key_dir, exist_ok=True)
        
        # Generate or load encryption key
        self._setup_key()
    
    def _setup_key(self):
        """Generate or load encryption key"""
        if not os.path.exists(self.key_file):
            print("Generating new encryption key...")
            self._generate_key()
        else:
            print("Loading existing encryption key...")
            self._load_key()
    
    def _generate_key(self):
        """Generate Fernet encryption key"""
        self.key = Fernet.generate_key()
        
        # Save key
        with open(self.key_file, 'wb') as f:
            f.write(self.key)
        
        self.cipher = Fernet(self.key)
        print(f"Encryption key generated and saved to {self.key_file}")
    
    def _load_key(self):
        """Load existing encryption key"""
        with open(self.key_file, 'rb') as f:
            self.key = f.read()
        
        self.cipher = Fernet(self.key)
    
    def encode_credentials(self, agency_data: dict) -> str:
        """Encode agency credentials into encrypted format"""
        # Extract credentials
        credentials = {
            'agency_abbrev': agency_data.get('agency_abbrev', ''),
            'rms_username': agency_data.get('rms_username', ''),
            'rms_password': agency_data.get('rms_password', ''),
            'copware_username': agency_data.get('copware_username', ''),
            'copware_password': agency_data.get('copware_password', ''),
            'other_systems': agency_data.get('other_systems', {}),
            'encoded_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Convert to JSON
        credentials_json = json.dumps(credentials, indent=2)
        
        # Encrypt
        encrypted_credentials = self.cipher.encrypt(credentials_json.encode('utf-8'))
        
        # Save to file
        with open(self.credentials_file, 'w') as f:
            f.write(encrypted_credentials.decode('utf-8'))
        
        print(f"Credentials encrypted and saved to {self.credentials_file}")
        return encrypted_credentials.decode('utf-8')
    
    def decode_credentials(self, agency_abbrev: str) -> dict:
        """Decode credentials for specific agency"""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError("No encrypted credentials file found")
        
        # Read encrypted data
        with open(self.credentials_file, 'r') as f:
            encrypted_data = f.read().strip()
        
        # Decrypt
        decrypted_json = self.cipher.decrypt(encrypted_data.encode('utf-8'))
        credentials = json.loads(decrypted_json.decode('utf-8'))
        
        # Verify agency match
        if credentials.get('agency_abbrev') != agency_abbrev:
            raise ValueError(f"Credentials do not match agency {agency_abbrev}")
        
        return credentials
    
    def get_encryption_key_for_prompt(self) -> str:
        """Get encryption key in format suitable for embedding in prompts"""
        return base64.b64encode(self.key).decode('utf-8')
    
    def create_credential_loader_script(self) -> str:
        """Create a script that can be embedded in prompts to load credentials"""
        script = f'''#!/usr/bin/env python3
"""
Credential Loader for dataPull Agent
Automatically loads and decrypts credentials using embedded encryption key
"""

import base64
import json
from cryptography.fernet import Fernet

# Embedded encryption key (will be replaced during generation)
ENCRYPTION_KEY = "{{ENCRYPTION_KEY}}"

def load_credentials(credentials_file="credentials/encrypted_credentials.json"):
    """Load and decrypt credentials"""
    try:
        # Decode encryption key
        key = base64.b64decode(ENCRYPTION_KEY.encode('utf-8'))
        cipher = Fernet(key)
        
        # Read encrypted credentials
        with open(credentials_file, 'r') as f:
            encrypted_data = f.read().strip()
        
        # Decrypt
        decrypted_json = cipher.decrypt(encrypted_data.encode('utf-8'))
        credentials = json.loads(decrypted_json.decode('utf-8'))
        
        return credentials
        
    except Exception as e:
        print(f"Error loading credentials: {{e}}")
        return None

if __name__ == "__main__":
    creds = load_credentials()
    if creds:
        print("Credentials loaded successfully")
        print(f"Agency: {{creds.get('agency_abbrev', 'Unknown')}}")
    else:
        print("Failed to load credentials")
'''
        return script

def main():
    """Main function for credential encoding"""
    print("=== dataPull Agent Credential Encoder (Simple) ===")
    print()
    
    # Initialize encoder
    encoder = SimpleCredentialEncoder()
    
    # Get agency data
    print("Enter agency information:")
    agency_data = {}
    agency_data['agency_abbrev'] = input("Agency abbreviation: ").strip()
    agency_data['rms_username'] = input("RMS username: ").strip()
    agency_data['rms_password'] = getpass.getpass("RMS password: ")
    
    # Optional COPWARE credentials
    use_copware = input("Include COPWARE credentials? (y/n): ").lower().strip() == 'y'
    if use_copware:
        agency_data['copware_username'] = input("COPWARE username: ").strip()
        agency_data['copware_password'] = getpass.getpass("COPWARE password: ")
    
    # Optional other systems
    other_systems = {}
    while True:
        system_name = input("Other system name (or 'done'): ").strip()
        if system_name.lower() == 'done':
            break
        if system_name:
            username = input(f"{system_name} username: ").strip()
            password = getpass.getpass(f"{system_name} password: ")
            other_systems[system_name] = {
                'username': username,
                'password': password
            }
    
    if other_systems:
        agency_data['other_systems'] = other_systems
    
    # Encode credentials
    print("\\nEncoding credentials...")
    encrypted_creds = encoder.encode_credentials(agency_data)
    
    # Get encryption key for prompt embedding
    encryption_key = encoder.get_encryption_key_for_prompt()
    
    print("\\n=== Credential Encoding Complete ===")
    print(f"Encrypted credentials saved to: {encoder.credentials_file}")
    print(f"Encryption key for prompt embedding:")
    print(encryption_key)
    
    # Create credential loader script
    loader_script = encoder.create_credential_loader_script()
    loader_script = loader_script.replace("{{ENCRYPTION_KEY}}", encryption_key)
    
    with open("credential_loader.py", "w") as f:
        f.write(loader_script)
    
    print("\\nCredential loader script created: credential_loader.py")
    print("\\nTo use in prompts:")
    print("1. Include the encryption key in the prompt")
    print("2. Include the credential_loader.py script")
    print("3. The agent can load credentials using the loader script")

if __name__ == "__main__":
    main()

