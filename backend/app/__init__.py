from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=['http://localhost:5173'])

    # Configurações da aplicação
    app.config.from_object('app.config.Config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    # app.

    # Inicializa o banco de dados
    db.init_app(app)

    # Registro de blueprints ou rotas
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app