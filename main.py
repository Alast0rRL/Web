from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    login = "Alast0r"
    balance = 123455
    description = "Ну тут текст типа"
    return render_template("index.html", description=description, login=login, balance=balance)
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
    # Здесь вы можете использовать запрос query для вывода результатов поиска
    return f'Результаты поиска для: {query}'

@app.route('/mem')
def mem():
    return render_template("mem/mem.html")

if __name__ == '__main__':
    app.run(debug=True)