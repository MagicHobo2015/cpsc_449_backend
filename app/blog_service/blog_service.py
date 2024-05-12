#------------------------------------------------------------------------------#
#	Welcome to my blog api!													   #
#		Discription: 	This is a simple flask CRUD api for a blog.            #
#			Author: Joshua Land												   #
#																			   #
#------------------------------------------------------------------------------#
from flask import Flask
from datetime import datetime
from dotenv import dotenv_values
from blog_models import db, BlogPost
from flask import request, jsonify, abort


#	Create a dictionary from the .env stuff
private_stuff = dotenv_values('.env')

# init Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = private_stuff["SQLALCHEMY_DATABASE_URI"]
db.init_app(app)

# This will only create the tables once.
with app.app_context():
	db.create_all()

# create - Blog Post, works.
@app.route("/post", methods=["POST"])
def create_post():

    if request.method == "POST":
        # Required parameters for a blog post
        required_params = ['title', 'content', 'author']
        blog_content = {}

        # Check if all required parameters are present in the request
        if all(param in request.form for param in required_params):
            # Gather required info from the request
            blog_content = {param: request.form[param] for param in required_params}
            
            # Create the post
            new_post = BlogPost(**blog_content)
            db.session.add(new_post)
            db.session.commit()
            db.session.refresh(new_post)

            # Prepare response data
            response_data = {
                'id': new_post.id,
                'date_posted': new_post.date_posted,
                **blog_content
            }
            return jsonify(response_data), 201
        else:
            return abort(400)
    else:
        return abort(404)

# Read - post 
@app.route("/post/<int:post_id>", methods=["GET"])
def get_post(post_id):
      post = BlogPost.query.get(post_id)
      if post is not None:
            return jsonify(post.to_json()), 200
      else:
           return abort(403)
           
# Update - blog Post
@app.route("/post/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    required_params = ['title', 'content', 'author']

    # Retrieve the post to update
    post = BlogPost.query.get(post_id)
    if post is None:
        return abort(403)

    # Validate request data
    if not all(param in request.json for param in required_params):
        return abort(400)

    # Update post attributes
    post.title = request.json.get('title')
    post.content = request.json.get('content')
    post.last_edit = datetime.utcnow()

    # Commit changes to database
    db.session.commit()

    # Return updated post data
    return jsonify(post.to_json()), 201
            
# Delete - post post
@app.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    # Retrieve the post to delete
    post = BlogPost.query.get(post_id)
    if post is None:
        return abort(404)

    # Delete the post
    db.session.delete(post)
    db.session.commit()

    # Return success message
    return jsonify({'result': True}), 200

@app.errorhandler(400)
def bad_request(error):
     return jsonify({"Error" : "Bad Request, Validation Error: Missing required Fields"}), 400

@app.errorhandler(403)
def bad_request(error):
     return jsonify({'error': 'Post Not found'}), 403

# ErrorHandler - endpoint not found (404)
@app.errorhandler(404)
def page_not_found(error):
	return "<h1>404</h1><p>Oops, It looks like the page you're looking for cannot be found.", 404
