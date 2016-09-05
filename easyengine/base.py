from easyengine.resources import (
	Install,
	Site,
	Secure,
	Stack
)

class EasyEngine(object):
	def __init__(self, host, username, password, port=None, *args, **kwargs):
		self._host     = host
		self._username = username
		self._password = password
		
		if port:
			self._port   = int(port)
		
		self.clean   = Clean(self._host, **self.auth)
		self.install = Install(self._host, **self.auth)
		self.site    = Site(self._host, **self.auth)
		self.secure  = Secure(self._host, **self.auth)
		self.stack   = Stack(self._host, **self.auth)

	@property
	def auth(self):
		kwargs = {
			'username': self._username,
			'password': self._password,
		}

		if hasattr(self, '_port'):
			kwargs.update({'port': self._port})

		return kwargs