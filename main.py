from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy import desc
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '25565egorovpidor552625'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.secret_key = 'your_secret_key'

#login
#login_manager = LoginManager(app)


db = SQLAlchemy(app)




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id

class Tovar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(15), nullable=False, unique=True)
    login = db.Column(db.String(15), nullable=False)  # Убран параметр unique=True
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tovar %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def index():
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    login = "Alast0r"
    balance = 123455
    flash('Пользователь создан')
    return render_template("index.html", tovars=tovars, login=login, balance=balance)

@app.route('/login-user', methods=['POST', 'GET'])
def login_user():
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    login = "Alast0r"
    balance = 123455
    return render_template("login-user.html", tovars=tovars, login=login, balance=balance)

@app.route('/create-tovar', methods=['POST', 'GET'])
def create_tovar():
    if request.method == 'POST':
        with app.app_context():
            last_tovar = Tovar.query.order_by(desc(Tovar.id)).first()
            if last_tovar:
                id = last_tovar.id + 1
            else:
                id = 1
            
            description = request.form['description']
            login = request.form['login']
            price = request.form['price']
            date = datetime.utcnow()
            tovar = Tovar(id=id, description=description, login=login, price=price, date=date)
            try:
                db.session.add(tovar)
                db.session.commit()
                flash('Товар добавлен')
                print("Tovar added successfully!")
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding tovar: {str(e)}")
                return f"Произошла ошибка при добавлении товара: {str(e)}"
    else:
        return render_template("create-tovar.html")

@app.route('/create-user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'POST':
        with app.app_context():
            last_user = User.query.order_by(desc(User.id)).first()
            if last_user:
                id = last_user.id + 1
            else:
                id = 1
            
            login = request.form['login']
            email = request.form['email']
            password = request.form['password']
            balance = request.form['balance']
            user = User(id=id, login=login, email=email, password=password, balance=balance)
            try:
                db.session.add(user)
                db.session.commit()
                print("User added successfully!")
                flash('Пользователь создан')
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding user: {str(e)}")
                flash(f"Произошла ошибка при добавлении пользователя: {str(e)}")
                return f"Произошла ошибка при добавлении пользователя: {str(e)}"
    else:
        return render_template("create-user.html")

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        return redirect(url_for('search_results', query=query))

@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    if query.lower() == "mem":  # Исправлено на использование lower()
        return render_template("mem/mem.html")
    elif query.lower() == "равиль":
        return render_template("create-user.html")
    elif query.lower() == "товар":
        return render_template("create-tovar.html")
    elif query.lower() == "ананас":
        return render_template("ananas.html")
    else:
        return render_template("not_found.html")  # Добавлено сообщение о том, что запрос не найден

@app.route('/create-user-page', methods=['GET', 'POST'])
def create_user_page():
    login = "Alast0r"
    balance = 123455
    return render_template("create-user.html", login=login, balance=balance)

@app.route('/create-tovar-page', methods=['GET', 'POST'])
def create_tovar_page():
    login = "Alast0r"
    balance = 123455
    return render_template("create-tovar.html", login=login, balance=balance)


@app.route('/help')
def help():
    return redirect("https://i.pinimg.com/736x/94/95/d9/9495d94e62132fb17ae2b9ddff0690bf.jpg")

if __name__ == '__main__':
    app.run(debug=True)
