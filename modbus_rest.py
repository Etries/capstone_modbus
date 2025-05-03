#!/usr/bin/env python3

from flask import Flask, g
from flask_restful import Api, Resource
from flask_httpauth import HTTPTokenAuth
import sqlite3
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
api = Api(app)
auth = HTTPTokenAuth(scheme='Token')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "modbus_db.sqlite")




@auth.verify_token
def verify_token(token):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT username FROM tokens WHERE password = ?", (token,))
        row = cur.fetchone()
        conn.close()
        if row:
            g.current_user = row[0]
            return True
    except Exception as e:
        print(f"DB error in token verification: {e}")
    return False


class ModbusStatus(Resource):
    @auth.login_required
    def get(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT ip, di, co, ir, hr FROM modbus LIMIT 1")
            row = cur.fetchone()
            conn.close()

            if row:
                return {
                    "user": g.current_user,
                    "ip": row[0],
                    "di": row[1],
                    "co": row[2],
                    "ir": row[3],
                    "hr": row[4]
                }
            else:
                return {"error": "No modbus data found"}, 404

        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(ModbusStatus, "/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
