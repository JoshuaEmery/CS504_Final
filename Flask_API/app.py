from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS 
from flask import request, jsonify
from dbSecretsLocal import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from datetime import datetime, timedelta
from mfahash import TFA
import hashlib

app = Flask(__name__)
CORS(app)
# set the copnnection String
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# create the DB object
db = SQLAlchemy(app)
# create the tfa object
authenticator = TFA('secretkey')

# class to represent the users table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45))
    email = db.Column(db.String(45))
    failed_login_count = db.Column(db.Integer)
    locked_out = db.Column(db.Integer)
    locked_out_end = db.Column(db.DateTime)
    email_to_upper = db.Column(db.String(45))
    password_hash = db.Column(db.String(255))
    failed_login_time = db.Column(db.DateTime)
    # this is a naviation property. this is not an actual column in the database
    logins = db.relationship('UserLogin', backref='user')
    # this is how you override the tostring method in python
    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"

# class to represent the userlogins table
class UserLogin(db.Model):
    __tablename__ = 'user_logins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    logged_in = db.Column(db.DateTime)
    successful = db.Column(db.Integer)
    # tostring again
    def __repr__(self):
        return f"UserLogin(id={self.id}, user_id={self.user_id}, logged_in={self.logged_in})"

# endpoint for testing


@app.route('/')
def hello_world():
    return 'Hello, World!'

# endpoint to get one user by id


@app.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'failed_login_count': user.failed_login_count,
        'locked_out': user.locked_out,
        'locked_out_end': user.locked_out_end,
        'email_to_upper': user.email_to_upper,
        'password_hash': user.password_hash,
        'failed_login_time': user.failed_login_time
    }
    return jsonify(user_data)

# endpoint to create a new user

#


@app.route('/users', methods=['POST'])
def create_user():
    # get the data from the request
    data = request.get_json()
    # check to see that the username, email and password are not empty
    if data['username'] == '' or data['email'] == '' or data['password'] == '':
        return 'username, email and password are required', 400
    # create a new user object populating the to_upper field with the email as uppercase
    new_user = User(
        username=data['username'], 
        email=data['email'], 
        email_to_upper=data['email'].upper(),
        failed_login_count=0,
        locked_out=0)
    # get the password from the request
    password = data['password']
    # hash the password using hashlib
    new_user.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # print the hashed password
    print(new_user.password_hash)
    # add the new user to the database
    db.session.add(new_user)
    # commit the changes
    db.session.commit()
    # return the new user for testing
    user_data = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'email_to_upper': new_user.email_to_upper,
        'password_hash': new_user.password_hash,
        'failed_login_count': new_user.failed_login_count,
        'locked_out': new_user.locked_out,
        'locked_out_end': new_user.locked_out_end
    }
    return jsonify(user_data)

#endpoint for login
@app.route('/login', methods=['POST'])
def login():
    # get the data from the request
    data = request.get_json()
    # check to see that the username and password are not empty
    if data['username'] == '' or data['password'] == '':
        return 'username and password are required', 400
    # get the user from the database
    user = User.query.filter_by(email_to_upper=data['username'].upper()).first()
    # check to see if the user exists
    if user is None:
        return 'user not found', 404
    # check to see if the user is locked out
    if user.locked_out == 1 and user.locked_out_end > datetime.now():
        return 'user is locked out', 403
    # get the password from the request
    password = data['password']
    # hash the password using hashlib
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # check to see if the password matches the password hash
    if password_hash != user.password_hash:
        uLogin = UserLogin(user_id=user.id, logged_in=datetime.now(), successful=0)
        db.session.add(uLogin)
        # increment the failed login count
        user.failed_login_count += 1
        # check to see if the failed login count is greater than 3
        if user.failed_login_count >= 3:
            # if it is, lock the user out
            user.locked_out = 1
            # reset the failed login count
            user.failed_login_count = 0
            # set the locked out end time to 5 minutes from now
            user.locked_out_end = datetime.now() + timedelta(minutes=5)
        db.session.commit()
        return 'invalid password', 401
    # if we make it down here we know the password is correct and the user is not locked out
    # reset the failed login count
    user.failed_login_count = 0
    uLogin = UserLogin(user_id=user.id, logged_in=datetime.now(), successful =  1)
    db.session.add(uLogin)
    # commit the changes
    db.session.commit()
    # return the user for testing
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'email_to_upper': user.email_to_upper,
        'password_hash': user.password_hash,
        'failed_login_count': user.failed_login_count,
        'locked_out': user.locked_out,
        'locked_out_end': user.locked_out_end
    }
    return jsonify(user_data)

@app.route('/tfa', methods=['POST'])
def tfa():
    data = request.get_json()
    if data['username'] == '':
        return 'username is required', 400
    user = User.query.filter_by(email_to_upper=data['username'].upper()).first()
    print(user)
    print(data['username'])
    if user is None:
        return 'user not found', 404
    tfa_code = authenticator.generate_tfa_code(user.username)
    return jsonify({'tfa_code': tfa_code})

@app.route('/tfa/validate', methods=['POST'])
def tfa_validate():
    data = request.get_json()
    if data['username'] == '' or data['tfa_code'] == '':
        return 'username and tfa_code are required', 400
    user = User.query.filter_by(email_to_upper=data['username'].upper()).first()
    if user is None:
        return 'user not found', 404
    if data['tfa_code'] == authenticator.generate_tfa_code(user.username):
        return 'tfa code is valid', 200
    else:
        return 'tfa code is invalid', 401

@app.route('/testtfa', methods=['GET'])
def test_tfa():
    return authenticator.generate_tfa_code('testuser')

if __name__ == '__main__':
    app.run(port=8080)
