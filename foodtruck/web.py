import os.path
import logging
from flask import Flask, g, render_template
from .config import FoodTruckConfig, FoodTruckConfigNotFoundError
from .sites import FoodTruckSites


_cfg_path = os.path.join(os.path.dirname(__file__), 'foodtruck.cfg')


def _get_foodtruck_config():
    return FoodTruckConfig(_cfg_path, defaults_path=(_cfg_path + '.defaults'))


app = Flask(__name__)


_cfg = _get_foodtruck_config()
app.secret_key = _cfg.get('foodtruck', 'secret_key')
del _cfg


@app.before_request
def _load_config():
    g.config = _get_foodtruck_config()
    g.sites = FoodTruckSites(g.config)


@app.errorhandler(FoodTruckConfigNotFoundError)
def _on_config_missing(ex):
    return render_template('install.html')


@app.errorhandler
def _on_error(ex):
    logging.exception(ex)


from flask.ext.login import LoginManager, UserMixin


class User(UserMixin):
    def __init__(self, uid, pwd):
        self.id = uid
        self.password = pwd


def load_user(user_id):
    admin_id = g.config.get('security', 'username')
    if admin_id == user_id:
        admin_pwd = g.config.get('security', 'password')
        return User(admin_id, admin_pwd)
    return None


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.user_loader(load_user)


try:
    from flask.ext.bcrypt import Bcrypt
except ImportError:
    logging.warning("Bcrypt not available... falling back to SHA512.")
    logging.warning("Run `pip install Flask-Bcrypt` for more secure "
                    "password hashing.")

    import hashlib

    def generate_password_hash(password):
        return hashlib.sha512(password.encode('utf8')).hexdigest()

    def check_password_hash(reference, check):
        check_hash = hashlib.sha512(check.encode('utf8')).hexdigest()
        return check_hash == reference

    class SHA512Fallback(object):
        def __init__(self, app=None):
            self.generate_password_hash = generate_password_hash
            self.check_password_hash = check_password_hash

    Bcrypt = SHA512Fallback

app.bcrypt = Bcrypt(app)


import foodtruck.views.create  # NOQA
import foodtruck.views.edit  # NOQA
import foodtruck.views.main  # NOQA
import foodtruck.views.menu  # NOQA
import foodtruck.views.preview  # NOQA
import foodtruck.views.settings  # NOQA
import foodtruck.views.sources  # NOQA

