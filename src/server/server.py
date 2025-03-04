from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return "website"    

# Dummy user credentials (replace with database later)
VALID_CREDENTIALS = {
    "user1": "password123",
    "testuser": "securepass"
}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
