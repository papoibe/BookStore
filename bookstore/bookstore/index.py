from flask import Flask
from bookstore import app, db

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)