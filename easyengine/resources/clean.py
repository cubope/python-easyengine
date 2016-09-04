from .base import Server
from .. import EasyEngineException

class Clean(Server):
	name = 'Clean'

	_choice = None

	valid_choices = [
		None, 'fastcgi', 'memcache', 'opcache', 'pagespeed', 'redir', 'all'
	]

	def is_valid_choice(self):
		if self._choice in self.valid_choices:
			return True

		return False

	def do(self, choice=None):
		if self.is_install():
			raise EasyEngineException

		if choice:
			self._choice = choice

		if not self.is_valid_choice():
			return self.response(False)

		if self._choice:
			stdin, stdout, stderr = self.execute('ee clean --%s' % self._choice)
		else:
			stdin, stdout, stderr = self.execute('ee clean')
		
		stdout.readlines()

		return self.response(True)