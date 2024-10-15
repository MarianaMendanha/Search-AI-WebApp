from app import create_app
from app.extensions import db

# app = create_app()
app, celery = create_app()
app.app_context().push()

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)

