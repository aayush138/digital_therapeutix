from app.extensions import db, migrate, Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from app.extensions import db, mail, sess
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    sess.init_app(app)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app

