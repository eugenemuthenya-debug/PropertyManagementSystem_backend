from flask_cors import CORS
from flask import Flask, request , jsonify
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import (
#     JWTManager,
#     create_access_token,
#     jwt_required,
#     get_jwt_required,
# )
import psycopg
from psycopg.rows import dict_row
# since we are already using postgresql we use this psycopg library.
import os

# -- App setup
app = Flask(__name__)
CORS(app)

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

#-----------Register/Sign Up-----------------------(this is only for the landlord)
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()


    landlord_name = data.get("landlord_name", "").strip()
    password_hash = data.get("password_hash", "").strip()
    landlord_email = data.get("landlord_email", "").strip().lower()
    phone_number = data.get("phone_number", "").strip()
    account_status = data.get("account_status", "").strip()


# This is to make sure that the user doesn't send to the backend any empty field. All fields must be filled.
    if not all([landlord_name,password_hash,landlord_email,phone_number,account_status]):
        return jsonify({"error":"All fields are required"}),400

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
        print("Signup error:",repr(e))
        return jsonify({"error":"Something went wrong.Please try again."}),500

    finally:
        cursor.close()
        connection.close()

