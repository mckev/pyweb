import pyweb


class User(pyweb.Model):
    def get_attributes(self, user_id):
        registry = self.registry
        result = {'name': 'Kevin Haritmonds', 'address': 'Pune, India'}
        return result
