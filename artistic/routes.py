from artistic.views import api_bp, auth_bp, home_bp, image_bp, palettes_bp


def routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(palettes_bp)
    app.register_blueprint(api_bp.v1.images)
    app.register_blueprint(api_bp.v1.palettes)
