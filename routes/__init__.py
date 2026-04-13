from .members import members_bp
from .bookings import bookings_bp
from .stats import stats_bp
from .guests import guests_bp


def register_routes(app):
    app.register_blueprint(members_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(guests_bp)
