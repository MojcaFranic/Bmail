__author__ = 'Mojca'

import os
import jinja2
import webapp2
import datetime
import time
import hmac
import hashlib
from models import User
from secret import secret


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        cookie_value = self.request.cookies.get("uid")

        if cookie_value:
            params["logedin"] = self.check_cookie(cookie_vrednost=cookie_value)
        else:
            params["logedin"] = False
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))

    def create_cookie(self, user):
        user_id = user.key.id()
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        expires_ts = int(time.mktime(expires.timetuple()))
        code = hmac.new(str(user_id), str(secret)).hexdigest()
        vrednost = "%s:%s:%s" % (user_id, code, expires_ts)
        self.response.set_cookie(key="uid", value=vrednost, expires=expires)

    def check_cookie(self, cookie_vrednost):
        user_id, code, expires_ts = cookie_vrednost.split(":")

        if datetime.datetime.utcfromtimestamp(float(expires_ts)) > datetime.datetime.now():
            test_cookie = hmac.new(str(user_id), str(secret) + str(expires_ts), hashlib.sha1).hexdigest()

            if code == test_cookie:
                return True
            else:
                return False
        else:
            return False


class MainHandler(BaseHandler):
    def get(self):
        self.render_template("index.html")

class RegisterHandler(BaseHandler):
    def get(self):
        self.render_template("register.html")

    def post(self):
        ime = self.request.get("nickname")
        mail = self.request.get("email")
        geslo = self.request.get("password")
        ponovitev = self.request.get("again")

        if geslo == ponovitev:
            user = User.query(User.mail == mail).get()
            user2 = User.query(User.ime == ime).get()
            if user:
                return self.write("User with this e-mail already exists")
            elif user2:
                return self.write("User with this nickname already exists")
            else:
                user = User.create(ime=ime,
                                    mail=mail,
                                    password=geslo,)
                return self.redirect_to("hello")
        else:
            params = {"ime": ime, "mail": mail}
            return self.render_template("register.html", params)

class LoginHandler(BaseHandler):
    def get(self):
        self.render_template("login.html")

    def post(self):
        ime = self.request.get("nickname")
        geslo = self.request.get("password")

        user = User.query(User.ime == ime).get()
        if user:
            check_user = User.check_password(user, geslo)

            if check_user:
                self.create_cookie(user=user)
                return self.redirect_to("hello")
            else:
                return self.write("Wrong password")
        else:
            return self.redirect_to("register")

class HelloHandler(BaseHandler):
    def get(self):
        ime = self.request.get("nickname")
        params = {"oseba": ime}
        self.render_template("hello.html", params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/register', RegisterHandler, name="register"),
    webapp2.Route('/login', LoginHandler),
    webapp2.Route('/hello', HelloHandler, name="hello"),
], debug=True)
