from flask import Flask, render_template, redirect, url_for, request, flash, session, redirect, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from sqlalchemy import desc
from datetime import datetime

# Создание Flask-приложения
app = Flask(__name__)

# Настройка подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Секретный ключ для безопасности сессий и других целей
app.config['SECRET_KEY'] = '25565e552625'

# Настройки для SQLAlchemy
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

# Создание объекта SQLAlchemy
db = SQLAlchemy(app)

# Класс модели пользователя
class User(db.Model):
    # Определение полей модели
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id

# Класс модели товара
class Tovar(db.Model):
    # Определение полей модели
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(15), nullable=False, unique=True)
    login = db.Column(db.String(15), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    connect= db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tovar %r>' % self.id

# Маршрут для отображения главной страницы
@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def index():
    # Получение списка товаров из базы данных, упорядоченного по дате добавления
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    
    # Проверка наличия пользователя в сессии и передача соответствующих данных в шаблон
    if 'userLogged' not in session:
        username = "Войти"
        balance = "0"
        email = ""
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""
        
    # Отображение главной страницы с передачей данных о пользователях и товарах
    return render_template("index.html", tovars=tovars, username=username, balance=balance, email=email)

# Маршрут для страницы "Пополнить счёт"
@app.route('/money', methods=['GET', 'POST'])
def money():
    if request.method == 'POST':
        # Проверка авторизации пользователя и пополнение баланса на 1000Р
        if 'userLogged' not in session:
            flash('Вы не авторизованы')
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(login=session['userLogged']).first()
            user.balance += 1000
            try:
                db.session.commit()
                flash('+1000Р')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding tovar: {str(e)}")
                flash('Ошибка')
        # Перенаправление на страницу с сообщением об успешном пополнении
        return render_template('scam.html', username=session['userLogged'], balance=user.balance, email=user.email)
    elif request.method == 'GET':
        pass

# Маршрут для страницы авторизации
@app.route('/login', methods=['POST', 'GET'])
def login():
    # Проверка наличия пользователя в сессии и перенаправление на его профиль, если он уже авторизован
    if 'userLogged' in session:
        user = User.query.filter_by(login=session['userLogged']).first()
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        # Обработка данных формы при отправке POST запроса
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(login=username).first()
        # Проверка введенных данных пользователя и установка соответствующей сессии
        if user and user.password == password:
            session['userLogged'] = username
            return redirect(url_for('profile', username=username))
        else:
            flash('Неверное имя пользователя или пароль')
    return render_template("login-user.html")

# Маршрут для выхода из учетной записи
@app.route('/logout')
def logout():
    # Удаление данных о пользователе из сессии при выходе
    session.pop('userLogged', None)
    return redirect(url_for('login'))

# Маршрут для отображения профиля пользователя
@app.route('/profile')
def profile():
    # Получение данных о пользователе из сессии и отображение их на странице профиля
    user = User.query.filter_by(login=session['userLogged']).first()
    email = user.email if user else ""
    balance = user.balance if user else ""
    return render_template('profile.html', user=user, email=email, balance=balance, username=session['userLogged'])

# Маршрут для отображения информации о товаре
@app.route('/tovar', methods=['POST'])
def tovar_details():
    # Получение информации о выбранном товаре и отображение его на отдельной странице
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    if 'userLogged' not in session:
        username = "Войти"
        balance = ""
        email = ""
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else ""
        email = user.email if user else ""
    if request.method == 'POST':
        tovar_id = request.form['tovar_id']
        tovar = Tovar.query.get(tovar_id)
        if tovar:
            return render_template('tovar.html', tovar=tovar, tovars=tovars, username=username, balance=balance, email=email)
        else:
            return "Товар не найден"

# Маршрут для создания нового товара
@app.route('/create-tovar', methods=['POST', 'GET'])
def create_tovar():
    # Обработка данных формы при создании нового товара
    if request.method == 'POST':
        description = request.form['description']
        login = session['userLogged']
        try:
            price = float(request.form['price'])
        except:
            flash('Товар добавлен')
            e="Неправильный формат цены"
            return render_template('error.html', error=str(e)), 500
        full_description = request.form['full_description']
        connect = request.form['connect']
        date = datetime.utcnow()
        tovar = Tovar(description=description, login=login, price=price, full_description=full_description,connect=connect, date=date)
        try:
            db.session.add(tovar)
            db.session.commit()
            flash('Товар добавлен')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            print(f"Error adding tovar: {str(e)}")
            return f"Произошла ошибка при добавлении товара: {str(e)}"
    else:
        if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            balance = user.balance if user else ""
            email = user.email if user else ""
        return render_template("create-tovar.html",username=username, balance=balance, email=email)

# Маршрут для создания нового пользователя
@app.route('/create-user', methods=['POST', 'GET'])
def create_user():
    # Обработка данных формы при создании нового пользователя
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
            balance = 0
            user = User(id=id, login=login, email=email, password=password, balance=balance)
            try:
                db.session.add(user)
                db.session.commit()
                print("User added successfully!")
                flash('Пользователь создан')
                return redirect('/login')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding user: {str(e)}")
                flash(f"Произошла ошибка при добавлении пользователя: {str(e)}")
                return f"Произошла ошибка при добавлении пользователя: {str(e)}"
    else:
        if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            balance = user.balance if user else ""
            email = user.email if user else ""
        return render_template("create-user.html", username=username, balance=balance, email=email)

# Маршрут для поиска товаров
@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        return redirect(url_for('search_results', query=query))

# Маршрут для отображения результатов поиска
@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    if query.lower() == "mem":
        return render_template("mem/mem.html")
    elif query.lower() == "test":
        tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    # Проверка наличия пользователя в сессии и передача соответствующих данных в шаблон
        if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            balance = user.balance if user else "Р"
            email = user.email if user else ""
        # Отображение главной страницы с передачей данных о пользователях и товарах
        return render_template("test.html", tovars=tovars, username=username, balance=balance, email=email)



    elif query.lower() == "ananas":
        return render_template("ananas.html")
    else:
        return render_template("not_found.html")

# Маршруты для отображения страниц создания пользователя и товара
@app.route('/create-user-page', methods=['GET', 'POST'])
def create_user_page():
    if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else ""
        email = user.email if user else ""
    return render_template("create-user.html",username=username, balance=balance, email=email)

@app.route('/create-tovar-page', methods=['GET', 'POST'])
def create_tovar_page():
    if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else ""
        email = user.email if user else ""
    return render_template("create-tovar.html",username=username, balance=balance, email=email)

# Маршрут для страницы помощи
@app.route('/help')
def help():
    return redirect("https://i.pinimg.com/736x/94/95/d9/9495d94e62132fb17ae2b9ddff0690bf.jpg")

# Обработчик ошибок для HTTP ошибки 404
@app.errorhandler(404)
def handle_exception(e):
    return render_template('error.html', error=str("Страница не найдена")), 500

# Обработчик ошибок для других исключений
@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error=str(e)), 500

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
