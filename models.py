__author__ = 'Mojca'

from google.appengine.ext import ndb
import uuid
import hmac
import hashlib

class User(ndb.Model):
    ime = ndb.StringProperty()
    mail = ndb.StringProperty()
    coded_password = ndb.StringProperty()

    @classmethod
    def create (cls, ime, mail, password):
        user = cls(ime=ime,
                        mail=mail,
                        coded_password=cls.code_password(original_password=password))
        user.put()
        return user

    @classmethod
    def code_password(cls, original_password):
        salt = uuid.uuid4().hex
        code = hmac.new(str(salt), str(original_password), hashlib.sha512).hexdigest()
        result = "%s:%s" % (code, salt)
        return result

    @classmethod
    def check_password(cls, user, password):
        code, salt = user.coded_password.split(":")
        new_code = hmac.new(str(salt), str(password), hashlib.sha512).hexdigest()

        if new_code == code:
            return True
        else:
            return False


