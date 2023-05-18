from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from dbSecrets import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

app = Flask(__name__)
# set the copnnection String
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{"CS504P@ssw3rd!"}@localhost:3306/user_db'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# create the DB object
db = SQLAlchemy(app)
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
    # tostring again

    def __repr__(self):
        return f"UserLogin(id={self.id}, user_id={self.user_id}, logged_in={self.logged_in})"

# endpoint for testing


@app.route('/')
def hello_world():
    return 'Hello, World!'

# users endpoint for testing database access


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_list = []

    for user in users:
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
        users_list.append(user_data)

    return jsonify(users_list)


if __name__ == '__main__':
    app.run(port=8080)