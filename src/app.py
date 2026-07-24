from flask_cors import CORS
from flask import Flask, request , jsonify
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import (
#     JWTManager,
#     create_access_token,
#     jwt_required,
#     get_jwt_required,
# )
import pymysql
import os

# -- App setup
app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME")
}

# our db helper to connect
def get_db(dict_cursor=False):
    conn = pymysql.connect(**DB_CONFIG)
    if dict_cursor:
        return conn,conn.cursor(pymysql.cursors.DictCursor)
    return conn, conn.cursor()

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
        sql = "INSERT INTO landlord(landlord_name,landlord_email,password_harsh,phone_number,account_status) values(%s,%s,%s,%s,%s)"
        cursor.execute(sql,(landlord_name,landlord_email,password_hash,phone_number,account_status))
        connection.commit()

    except Exception as e:
        print("Signup error:",repr(e))
        return jsonify({"error":"Something went wrong.Please try again."}),500

if __name__ == "__main__":
    app.run()