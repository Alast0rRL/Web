from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(15), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id
    

class Tovar(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(15), nullable=False, unique=True)
    login = db.Column(db.String(15), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tovar %r>' % self.id
    

@app.route('/' ,methods=['POST','GET'])
@app.route('/home' ,methods=['POST','GET'])
def index():

    tovars =Tovar.query.order_by(Tovar.date.desc()).all()


    login = "Alast0r"
    balance = 123455

    return render_template("index.html",tovars=tovars,
        login=login,
        balance=balance)

@app.route('/create-tovar', methods=['POST','GET'])
def create_tovar():
    if request.method == 'POST':
        with app.app_context():
            last_tovar = Tovar.query.order_by(desc(Tovar.id)).first()
            if last_tovar:
                id = last_tovar.id+1
            else:
                print("База данных пуста")
                return "База данных пуста"
            
            description = request.form['description']
            login = request.form['login']
            price = request.form['price']
            date = datetime.utcnow()  # Используем datetime.utcnow() для получения текущей даты и времени

            tovar = Tovar(id=id, description=description, login=login, price=price, date=date)  # Передаем значение date в объект Tovar
            try:
                db.session.add(tovar)
                db.session.commit()
                print("Tovar added successfully!")
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding tovar: {str(e)}")
                return f"Произошла ошибка при добавлении товара: {str(e)}"
    else:
        return render_template("create-tovar.html")

@app.route('/create-user', methods=['POST','GET'])
def create_user():
    if request.method == 'POST':
        with app.app_context():
            last_user = User.query.order_by(desc(User.id)).first()
            if last_user:
                id = last_user.id+1
            else:
                print("База данных пуста")
                return "База данных пуста"
            
            login = request.form['login']
            email = request.form['email']
            password = request.form['password']
            balance = request.form['balance']
            
            print(f"Trying to add user with login: {login}, email: {email}, password: {password}, balance: {balance}")

            user = User(id=id, login=login, email=email, password=password, balance=balance)
            try:
                print(f"User details: login={user.login}, email={user.email}, password={user.password}, balance={user.balance}")
                db.session.add(user)
                db.session.commit()
                print("User added successfully!")
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                print(f"Error adding user: {str(e)}")
                return f"Произошла ошибка при добавлении пользователя: {str(e)}"
    else:
        return render_template("create-user.html")



@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # Здесь можно выполнить логику поиска на основе запроса query

        # Предположим, что при успешном поиске вы хотите перенаправить пользователя на другую страницу с результатами
        return redirect(url_for('search_results', query=query))

@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    if query=="mem" or query=="мем" or query=="Mem" or query=="Мем":
        return render_template("mem/mem.html")
    elif query=="Равиль" or query=="равиль":
        return render_template("create-user.html")
    elif query=="Товар" or query=="товар":
        return render_template("create-tovar.html")
    else:
    # Здесь вы можете использовать запрос query для вывода результатов поиска
        return f'Результаты поиска для: {query}'


@app.route('/create-user-page', methods=['POST'])
def create_user_page():
    
    login = "Alast0r"
    balance = 123455

    return render_template("create-user.html",
        login=login,
        balance=balance)


@app.route('/create-tovar-page', methods=['POST'])
def create_tovar_page():
    login = "Alast0r"
    balance = 123455

    return render_template("create-tovar.html",
        login=login,
        balance=balance)

@app.route('/help', methods=['POST'])
def help():
    return redirect("https://i.pinimg.com/736x/94/95/d9/9495d94e62132fb17ae2b9ddff0690bf.jpg")

if __name__ == '__main__':
    app.run(debug=True)