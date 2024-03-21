from main import db, app

with app.app_context():
    db.create_all()
def upgrade():
    # Добавление столбца date
    op.add_column('tovar', sa.Column('date', sa.DateTime(), nullable=True))
upgrade()