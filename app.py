from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)