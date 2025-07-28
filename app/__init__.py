import os
from flask import Flask
from app.extensions import db, migrate, mail, sess
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.dashboard import dashboard_bp
import app.models
from app.utils.seed import seed_database

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    sess.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)

    # Create tables and seed database if not exists
    with app.app_context():
        db.create_all()
        try:
            seed_database()
        except Exception as e:
            print("Seeding error:", e)

    return app