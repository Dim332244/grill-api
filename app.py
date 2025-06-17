from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Grill API is working!"

@app.route('/upload', methods=['POST'])
def upload():
    return jsonify({"message": "Grill design processing will happen here"})

if __name__ == '__main__':
    app.run(debug=True)
