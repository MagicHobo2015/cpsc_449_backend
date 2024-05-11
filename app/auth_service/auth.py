from flask import Flask, jsonify, request, make_response
from dotenv import dotenv_values
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from flask_jwt_extended import create_access_token, JWTManager
from datetime import datetime, timedelta


# grab .env vars
private_stuff = dotenv_values('.env')
# create the app.
app = Flask(__name__)
# Config. app
app.config['SECRET_KEY'] = private_stuff['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = private_stuff['SQLALCHEMY_DATABASE_URI']
app.config['JWT_ALGORITHM'] = private_stuff['JWT_ALGORITHM']
db.init_app(app)
jwt=JWTManager(app)
with app.app_context(): 
     db.create_all()


#to store user credentials and appropriate permission level
@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
    email=data.get("email")
    password=data.get("password")
    is_admin=data.get("is_admin")
    if(email and password): 
         #provide data as a dictionary
         new_user = User(arg_dic={'email': email,'password': password,'is_admin': is_admin})
         db.session.add(new_user)
         db.session.commit()

         token=generateToken(email, is_admin)
         
         return jsonify({"message": "User created successfully"}, token), 201
    else:
         return jsonify({"message": "Invalid request parameters"}), 400

     
#generates token based on email, and permission (is_admin= True/False)
def generateToken(email, is_admin):
    data = {
    'email': email,
    'is_admin': is_admin
    }
    timeout = timedelta(seconds=3600)  # 1 hour
    access_token = create_access_token(identity=data, expires_delta=timeout)

    return access_token

    

if __name__=='__main__':
    app.run(debug=True)