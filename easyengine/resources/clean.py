from .base import Server
from .. import EasyEngineException

class Clean(Server):
	name = 'Clean'

	_choice = None

	valid_services = [
		None, 'fastcgi', 'memcache', 'opcache', 'pagespeed', 'redir', 'all'
	]

	def is_valid_service(self):
		if self._service in self.valid_services:
			return True

		return False

	def do(self, service=None):
		if self.is_install():
			raise EasyEngineException

		if service:
			self._service = service

		if not self.is_valid_service():
			return self.response(False)

		if self._service:
			stdin, stdout, stderr = self.execute('ee clean --%s' % self._service)
		else:
			stdin, stdout, stderr = self.execute('ee clean')
		
		stdout.readlines()

		return self.response(True)