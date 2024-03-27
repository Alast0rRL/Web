from flask import Flask, render_template, redirect, url_for, request, flash, session, redirect, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy import desc
from datetime import datetime







app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '25565e552625'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
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
    if 'userLogged' not in session:
        username = "Войти"
        balance = "0Р"
        email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
    return render_template("index.html", tovars=tovars, username=username, balance=balance, email=email)










@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        user = User.query.filter_by(login=session['userLogged']).first()
        print("worked")
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(password)
        user = User.query.filter_by(login=username).first()
        if user and user.password == password:
            session['userLogged'] = username
            return redirect(url_for('profile', username=username, password =password))
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template("login-user.html")
@app.route('/logout')
def logout():
    user = User.query.filter_by(login=session['userLogged']).first()
    session.pop('userLogged', None)
    return redirect(url_for('login'))


# @app.route('/profile/<username>')
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#     user = User.query.filter_by(login=session['userLogged']).first()
#     return render_template('profile.html',user=user, email=user.email, password = user.password, balance=user.balance ,username=session['userLogged'])





@app.route('/profile')
def profile():
    users = User.query.all()
    tovars = Tovar.query.all()
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    user = User.query.filter_by(login=session['userLogged']).first()
    return render_template('profile.html',user=user, email=user.email, password = user.password, balance=user.balance ,username=session['userLogged'])
#    return f"{tovars}     |     {users}"





@app.route('/tovar', methods=['POST'])
def tovar_details():
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    if 'userLogged' not in session:
        username = "Войти"
        balance = ""
        email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
    if request.method == 'POST':
        tovar_id = request.form['tovar_id']
        tovar = Tovar.query.get(tovar_id)  # Получаем информацию о товаре по его идентификатору из базы данных
        if tovar:
            return render_template('tovar.html', tovar=tovar, tovars=tovars, username=username, balance=balance, email=email)
        else:
            return "Товар не найден"





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


@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
