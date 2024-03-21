from main import app, db

# Создайте контекст приложения
with app.app_context():
    # Теперь вы можете работать с вашей базой данных
    db.create_all()
