from artistic.views import auth_bp, home_bp, api_bp

def routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
