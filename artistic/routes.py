from artistic.views import api_bp, auth_bp, home_bp


def routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(api_bp.v1.images)
