from app.extensions import db, migrate, Flask
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app.extensions import db, mail, sess
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    sess.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)

    return app

