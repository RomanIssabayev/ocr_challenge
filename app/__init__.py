from flask import Flask, current_app
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db, User
from werkzeug.security import generate_password_hash

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .views.login import login_bp
    from .views.home import home_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(home_bp)

    return app

def create_first_user():
    admin_username = current_app.config["ADMIN_LOGIN"]
    admin_password = current_app.config["ADMIN_PASSWORD"]
    admin_access_level = current_app.config["ADMIN_ACCESS"]

    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        hashed_password = generate_password_hash(admin_password, method="scrypt")
        admin_user = User(
            username=admin_username,
            password=hashed_password,
            access_level=admin_access_level
        )
        db.session.add(admin_user)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
