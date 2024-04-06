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
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
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
    full_description = db.Column(db.Text, nullable=False)
    connect= db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<Tovar %r>' % self.id







@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def index():
    tovars = Tovar.query.order_by(Tovar.date.desc()).all()
    if 'userLogged' not in session:
        username = "Войти"
        balance = "0"
        email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
    return render_template("index.html", tovars=tovars, username=username, balance=balance, email=email)



















@app.route('/money', methods=['GET', 'POST'])
def money():
    if request.method == 'POST':
        # Ваша логика для обработки POST-запроса
        if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
            flash('Вы не авторизованы')
            return redirect(url_for('login'))
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            user.balance += 1000
            try:
                db.session.commit()
                flash('+1000Р')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding tovar: {str(e)}")
                flash('Ошибка')
            return redirect('/')
    elif request.method == 'GET':
        # Ваша логика для обработки GET-запроса (если необходимо)
        pass


@app.route('/demoney', methods=['GET', 'POST'])
def demoney():
    if request.method == 'POST':
        # Ваша логика для обработки POST-запроса
        if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
            flash('Вы не авторизованы')
            return redirect(url_for('login'))
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            user.balance -= 1000
            try:
                db.session.commit()
                flash('-1000Р')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding tovar: {str(e)}")
                flash('Ошибка')
            return redirect('/')
    elif request.method == 'GET':
        # Ваша логика для обработки GET-запроса (если необходимо)
        pass

























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
    user = User.query.filter_by(login=session['userLogged']).first()
    if user:
        email = user.email
        password = user.password
        balance = user.balance
    else:
        email = ""  # установите значение по умолчанию для email, если пользователь не найден
        password = ""  # установите значение по умолчанию для password, если пользователь не найден
        balance = ""  # установите значение по умолчанию для balance, если пользователь не найден
    return render_template('profile.html', user=user, email=email, password=password, balance=balance, username=session['userLogged'])





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
        description = request.form['description']
        login = session['userLogged']
        try:
            price = float(request.form['price'])
        except:
            flash('Товар добавлен')
            e="Неправильный формат цены"
            return render_template('error.html', error=str(e)), 500
        full_description = request.form['full_description']  # Получаем полное описание товара из формы
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
            email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
        else:
            username = session['userLogged']
            user = User.query.filter_by(login=session['userLogged']).first()
            balance = user.balance if user else "Р"
            email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
        return render_template("create-tovar.html",username=username, balance=balance, email=email)

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
    elif query.lower() == "ananas":
        return render_template("ananas.html")
    else:
        return render_template("not_found.html")  # Добавлено сообщение о том, что запрос не найден

@app.route('/create-user-page', methods=['GET', 'POST'])
def create_user_page():
    if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
    return render_template("create-user.html",username=username, balance=balance, email=email)

@app.route('/create-tovar-page', methods=['GET', 'POST'])
def create_tovar_page():
    if 'userLogged' not in session:
            username = "Войти"
            balance = "0"
            email = ""  # Добавляем пустую строку для email, чтобы избежать ошибки
    else:
        username = session['userLogged']
        user = User.query.filter_by(login=session['userLogged']).first()
        balance = user.balance if user else "Р"
        email = user.email if user else ""  # Получаем email пользователя или устанавливаем пустую строку
    return render_template("create-tovar.html",username=username, balance=balance, email=email)


@app.route('/help')
def help():
    return redirect("https://i.pinimg.com/736x/94/95/d9/9495d94e62132fb17ae2b9ddff0690bf.jpg")









@app.errorhandler(404)
def handle_exception(e):
    return render_template('error.html', error=str("Страница не найдена")), 500



@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', error=str(e)), 500



# @app.errorhandler(userLogged)
# def handle_exception(e):
#     return render_template('error.html', error=str("Страница не найдена")), 500















def application(environ, start_response):
    status = '200 OK'
    output = b'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    
    return [output]




if __name__ == '__main__':
    app.run(debug=True)
