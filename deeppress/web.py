from functools import wraps

from deeppress.bottle import request, HTTPError


class AuthPlugin(object):
    name = 'AuthPlugin'
    keyword = 'auth'

    def __init__(self, token):
        self.token = token

    def get_token(self):
        try:
            token = request.query.get('access_token', None)
            if token:
                return token
            _type, token = request.headers['Authorization'].split(" ")
            if _type.lower() != "basic":
                return None
            return token
        except:
            return None

    def get_auth(self):
        token = self.get_token()
        if not token:
            raise HTTPError(403, "Forbidden")
        return token

    def apply(self, callback, route):
        auth_value = route.config.get(self.keyword, None)
        if not auth_value:
            return callback

        @wraps(callback)
        def wrapper(*args, **kwargs):
            auth = self.get_auth()
            if auth == self.token:
                return callback(*args, **kwargs)
            else:
                raise HTTPError(401, "Unauthorized")
        return wrapper