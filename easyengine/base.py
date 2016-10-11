from easyengine.resources import (
	Clean,
	Install,
	Site,
	Secure,
	Stack
)

class EasyEngine(object):
	name = 'EasyEngine'

	def __init__(self, host, username=None, password=None, port=None, key_path=None, *args, **kwargs):
		self._host     = host
		self._username = username if username else None
		self._password = password if username else None
		self._key_path = key_path if key_path else None
		
		if port:
			self._port   = int(port)
		
		self.clean   = Clean(self._host, **self.auth)
		self.install = Install(self._host, **self.auth)
		self.site    = Site(self._host, **self.auth)
		self.secure  = Secure(self._host, **self.auth)
		self.stack   = Stack(self._host, **self.auth)

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

	def __hash__(self):
		return hash(frozenset(self.__dict__))

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "<%s %s>" % (self.__class__.__name__, self.name[0:5])

	@property
	def auth(self):
		kwargs = {
			'username': self._username,
			'password': self._password,
		}

		if hasattr(self, '_port'):
			kwargs.update({'port': self._port})

		return kwargs