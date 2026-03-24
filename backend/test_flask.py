from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Flask is working!"

if __name__ == '__main__':
    print("Flask imported successfully!")
    print("Flask app created successfully!")
    print("Test script completed successfully!")
