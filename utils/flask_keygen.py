import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key for Flask"""
    return secrets.token_hex(32)

def update_env_file():
    """Update or create .env file with new secret key"""
    env_path = Path('.env')
    secret_key = generate_secret_key()
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update existing secret key
        secret_key_found = False
        for i, line in enumerate(lines):
            if line.startswith('FLASK_SECRET_KEY='):
                lines[i] = f'FLASK_SECRET_KEY={secret_key}\n'
                secret_key_found = True
                break
        
        if not secret_key_found:
            lines.append(f'FLASK_SECRET_KEY={secret_key}\n')
            
        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        with open(env_path, 'w') as f:
            f.write(f'FLASK_SECRET_KEY={secret_key}\n')
    
    print(f'Secret key generated and saved to .env file')

if __name__ == '__main__':
    update_env_file()
