from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/test')
def test():
    return 'test'

@app.route('/mem')
def mem():
    return render_template("mem/mem.html")

if __name__ == '__main__':
    app.run(debug=True)