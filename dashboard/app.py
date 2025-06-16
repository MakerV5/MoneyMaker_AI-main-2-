from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prediction')
def prediction():
    # return random prediction
    return jsonify({'prediction': random.random()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
