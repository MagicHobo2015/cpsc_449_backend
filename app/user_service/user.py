from flask import Flask, jsonify, request
from sqlalchemy import select
from dotenv import dotenv_values
from werkzeug.security import generate_password_hash
from models import db, User


# grab .env vars
private_stuff = dotenv_values('.env')
# create the app.
app = Flask(__name__)
# Config. 
app.config['SQLALCHEMY_DATABASE_URI'] = private_stuff['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = private_stuff['SECRET_KEY']  # Same secret key as in the authentication service
# Initialize the database with the app.
db.init_app(app)

# Create the tables if they dont exist already.
with app.app_context(): 
     db.create_all()

# Create - User
# This wants form data, not json.
@app.route('/user', methods=["POST"])
def create_user():
      # Seems redundant, cant even get here if it isnt a post request.
      if request.method == "POST":
            # make sure everything is here.
            # start with a list of all thats required
            required_params = [ 'email', 'username', 'first_name', 'last_name' ]

            # Look through params and make a dictionary if all is well.
            user_params = {}
            if all(param in request.form for param in required_params):
                if app.debug:
                    # this is just so that I can test
                    hashed_password = generate_password_hash(request.form['password'])
                # gather everything.
                user_params = {param : request.form[param] for param in required_params}
                user_params['password'] = hashed_password
                print(user_params['password'])

                # Now check that email and username are unique.
                # email = User.query.get('email')
                # username = User.query.get('user_name')
                email = db.session.execute(select(User.email_address).where(User.email_address == user_params['email']))
                username = db.session.execute(select(User.user_name).where(User.user_name == user_params['username']))
 
                if (email is not None) or (username is not None):
                    return jsonify(error='Account Already exists..'), 400

                # Create the user.
                new_user = User(user_params)
                db.session.add(new_user)
                db.session.commit()
                db.session.refresh(new_user)

                #Prepare response
                response_data = new_user.to_json()
                return response_data, 201
            else:
                  return jsonify(error='Missing Required Fields'), 400
      else:
           return jsonify(error='Bad Request'), 400
    
# Read - User
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Grabs the user from the db, if not returns 404.
     user = db.get_or_404(User, user_id)
     return user.to_json()

# Update - User
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
     required_params = ['first_name', 'last_name', 'user_name']
     if all(param in request.json for param in required_params):
          # grab the user.
          user = get_user(user_id)

          user.first_name = request.json.get('first_name')
          user.last_name = request.json.get('last_name')

          db.session.commit()
          return user.to_json(), 201 # success
     else:
          return jsonify(error="Missing a parameter!"), 400


@app.route('/protected')
@jwt_required()
def protected():
    return jsonify(logged_in_as=current_identity.username), 200



# Delete - User
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
     # get the user
     user = db.session.get(user_id)
     if user is None:
          return jsonify(error='Bad User ID'), 400

     db.session.delete(user)
     db.session.commit()
     return jsonify({'result' : True}), 200

# List of required error handlers

# Bad Request Error
@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify(error=str(error)), 400

# Unauthorized Action Error
@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors."""
    return jsonify(error=str(error)), 401

# Forbidden Error
@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors."""
    return jsonify(error=str(error)), 403

# Page Not Found Error
@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 Page Not Found errors."""
    return jsonify(error=str(error)), 404

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error errors."""
    return jsonify(error=str(error)), 500


if __name__ == '__main__':
    # run if called.
    app.run(debug=True)