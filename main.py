from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    login = "Alast0r"
    balance = 123455
    description_bl1 = "The Witcher 3 | Raft | The Forest | BeamNG | PAYDAY 2 | Garrys Mod | Far Cry 2 (БЕЗ ПРАЙМ-СТАТУСА)"
    price_bl1 = "Цена: 500P"
    seller_login = "Panovnic"
    seller_status = "Online"

    return render_template("index.html", description_bl1=description_bl1,
        price_bl1=price_bl1,
        login=login,
        balance=balance,
        seller_login=seller_login,
        seller_status=seller_status,
        
        
        
        )
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
    if query=="mem":
        return render_template("mem/mem.html")
    else:
    # Здесь вы можете использовать запрос query для вывода результатов поиска
        return f'Результаты поиска для: {query}'

@app.route('/help', methods=['POST'])
def help():
    return redirect("https://i.pinimg.com/736x/94/95/d9/9495d94e62132fb17ae2b9ddff0690bf.jpg")

if __name__ == '__main__':
    app.run(debug=True)