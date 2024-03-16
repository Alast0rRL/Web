from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return index.html

@app.route('/test')
def test():
    return 'test'

if __name__ == '__main__':
    app.run(debug=True)