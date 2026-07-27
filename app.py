from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask import Flask, request , jsonify
# from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    # JWTManager,
    create_access_token,
    # jwt_required,
    
)
import psycopg
from psycopg.rows import dict_row
# since we are already using postgresql we use this psycopg library.
import os
import traceback

# -- App setup
app = Flask(__name__)
CORS(app)

bcrypt=Bcrypt(app)

# OUR CONFIGS
# app.config:app is an object and has libraries in it such as config and we can store our data in there. In our case we are storing jwt_secret_key, this is a key which will be assigned a value
# os.environ:python talks to our os to get environment variables and for us it is in render.
# .get():we use the function to prevent crashing of the app when we want to get the value rather than the key , value pair itself.
# We never code this in our code for security purposes.
app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

# we have made two changes, the database name variable is called dbname 
# and we require the port 
# sslmode = require : A connection is only established and data is allowed to move to database when everything is encrypted. 

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "dbname": os.environ.get("DB_NAME"),
    "port": os.environ.get("DB_PORT"),
    "sslmode": "require"
}

# our db helper to connect
# **-->unpacks our DB_CONFIG dictionary
# conn-->connection
def get_db(dict_cursor=False):

    try :
        conn = psycopg.connect(**DB_CONFIG)
        if dict_cursor:
            cursor = conn.cursor(row_factory=dict_row)
        else:
            cursor = conn.cursor()
        return conn,cursor
    except Exception as e :
        print("Database error:",repr(e))
        return None,None

#-----------Register/Sign Up-----------------------(this is only for the landlord)[Success]
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()


    landlord_name = data.get("landlord_name", "").strip()
    landlord_password = data.get("landlord_password", "").strip()
    landlord_email = data.get("landlord_email", "").strip().lower()
    phone_number = data.get("phone_number", "").strip()
    account_status = data.get("account_status", "").strip()


# This is to make sure that the user doesn't send to the backend any empty field. All fields must be filled.
    if not all([landlord_name,landlord_password,landlord_email,phone_number,account_status]):
        return jsonify({"error":"All fields are required"}),400

    # we hash the password before storing in database using Bcrypt
    # decode("utf-8")-this decrypts the hashed password
    password_hash= bcrypt.generate_password_hash(landlord_password).decode("utf-8")

    connection, cursor = get_db()
    try:
        # check if record already exists by either checking email or username.
        cursor.execute(
            "SELECT landlord_id FROM landlord WHERE landlord_email=%s OR landlord_name= %s",
            (landlord_email, landlord_name)
        )
        # return the message that the record already exists.
        if cursor.fetchone():
            return jsonify({"error":"Email or Username already registered",
                            "email":landlord_email}),409

        # if record doesn't exist:
        sql = "INSERT INTO landlord(landlord_name,landlord_email,password_hash,phone_number,account_status) values(%s,%s,%s,%s,%s)"
        cursor.execute(sql,(landlord_name,landlord_email,password_hash,phone_number,account_status))

        connection.commit()

        return jsonify({"message":"Account created successfully"}),201

    except Exception as e:
        traceback.print_exc()
        # return jsonify({"error":str(e)}),500
        # traceback prints our entire error, where what went wrong and how it got there
        return jsonify({
        "error": "Something went wrong. Please try again."
    }), 500

    finally:
        cursor.close()
        connection.close()


#----------Log in-------------(Landlord)[Success]
@app.route("/api/login", methods=["POST"])
def signin():
    data = request.get_json()

   



    landlord_email= data.get("landlord_email", "").strip()
    landlord_password = data.get("landlord_password", "").strip()

    # makes sure all fields are required
    if not landlord_email or not landlord_password:
        return jsonify({"error":"Email or password  are required"}),400

    connection, cursor = get_db(True)
    try:
        cursor.execute("SELECT * FROM landlord WHERE landlord_email= %s", (landlord_email,))
        landlord_user = cursor.fetchone()
        # this returns the row that matches the email and stores it in a variable called landlord_user

        if not landlord_user or not bcrypt.check_password_hash(landlord_user["password_hash"],landlord_password):
            return jsonify({"error":"Invalid credentials"}),401

        # we wanna create our access token but they will be uniquely identified via landlord_id
        access_token = create_access_token(identity=str(landlord_user["landlord_id"]))
        return jsonify({
            "message":"Login successful",
            "landlord_user":{
                "landlord_id":landlord_user["landlord_id"],
                "landlord_name": landlord_user["landlord_name"],
                "landlord_email":landlord_user["landlord_email"],
                "phone_number":landlord_user["phone_number"],
                "access_token":access_token
            }
        }),200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error":str(e)}),500
        # return jsonify({"error":"Something went wrong. Please try again."}),500
    finally:
        cursor.close()
        connection.close()


