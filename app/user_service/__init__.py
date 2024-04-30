import os
from flask import Flask
from dotenv import load_dotenv


def _load_env_variables():
    try:
        # Fill the environment.
        load_dotenv('.env')
    except FileNotFoundError:
        # TODO: add logger
        print('Oops! .env file missing')
        # exit, let system know there was an error.
        exit(1)

def _init_flask_app():
    # create the app.
    app = Flask(__name__)
    # Setup Config.
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

if __name__ == '__main__':
    _init_flask_app()