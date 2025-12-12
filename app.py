from flask import Flask
import os
import secrets

app = Flask(__name__)

# Load SECRET_KEY from environment variable
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    # For development only: generate a random secret key
    # In production, always set SECRET_KEY environment variable
    import warnings
    warnings.warn(
        "SECRET_KEY environment variable not set. Using a randomly generated key. "
        "This is insecure for production use. Set SECRET_KEY environment variable.",
        UserWarning
    )
    secret_key = secrets.token_hex(32)

app.config['SECRET_KEY'] = secret_key

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)