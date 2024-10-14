from flask import Flask
from flask_cors import CORS

from .routes import main as main_blueprint
from .celery_utils import make_celery
from .extensions import db

def create_app():
    app = Flask(__name__)
    CORS(app, origins=['http://localhost:5173'])

    # Configurações da aplicação
    app.config.from_object('app.config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
    app.config["CELERY_CONFIG"] = {
        "broker_url": "redis://127.0.0.1:6380",
        "result_backend": "redis://127.0.0.1:6380"
    }

    # Inicializa o banco de dados
    db.init_app(app)
    
    celery = make_celery(app)
    celery.set_default()

    # Registro de blueprints ou rotas
    app.register_blueprint(main_blueprint)

    return app, celery