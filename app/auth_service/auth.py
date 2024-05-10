from flask import Flask, jsonify, request, make_response
from dotenv import dotenv_values
import datetime
import jwt


# grab .env vars
private_stuff = dotenv_values('.env')
# create the app.
app = Flask(__name__)
# Config. app
app.config['SECRET_KEY'] = private_stuff['SECRET_KEY']

#to generate a token if login credentials are correct
@app.route('/login', methods=['POST'])
def login():
    #get username, email and pwd from the request
    user_data = request.get_json()
    username = user_data.get("username")
    email = user_data.get("email")
    password = user_data.get("password")
    #generate token if everything matches
    if(username=="username" and email=="abc@gmail.com" 
           and password=="hashed_password"):
            token=jwt.encode({'user':username, 'password':password, 'exp': datetime.datetime.now()+datetime.timedelta(seconds=10)}, app.config['SECRET_KEY'])

            return token
    #incorrect credentials
    else:
        return make_response('Could not verify!', 401)
    

if __name__=='__main__':
    app.run(debug=True)