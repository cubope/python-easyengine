from .base import Server
from .. import EasyEngineException

class Stack(Server):
	name = 'Stack'

	_service = None

	services_stack = [
		'web', 'nginx', 'php', 'php7', 'hhvm', 'mysql', 'postfix', 'wpcli',
		'redis', 'adminer', 'phpmyadmin', 'phpredisadmin', 'utils', 'admin'
	]

	def is_valid_service(self):
		if self._service in self.services_stack:
			return True
		return False

	def install(self, service):
		if not self.is_install():
			raise EasyEngineException

		self._service = service

		if not self.is_valid_service():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee stack install --%s' % self._service)
		response = ''.join(stdout.readlines())

		if 'Successfully installed' or 'already installed' in response:
			return self.response(True)

		return self.response(False)

	def remove(self, service):
		if not self.is_install():
			raise EasyEngineException

		self._service = service

		if not self.is_valid_service():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee stack remove --%s' % self._service)
		stdin.write('yes\n')
		stdin.flush()
		response = ''.join(stdout.readlines())

		return self.response(True)

	def purge(self, service):
		if not self.is_install():
			raise EasyEngineException

		self._service = service

		if not self.is_valid_service():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee stack purge --%s' % self._service)
		stdin.write('yes\n')
		stdin.flush()
		response = ''.join(stdout.readlines())

		if 'Successfully purged' in response:
			return self.response(True)

		return self.response(False)

	def upgrade(self, service):
		if not self.is_install():
			raise EasyEngineException

		self._service = service

		if not self.is_valid_service():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee stack upgrade --%s' % self._service)
		stdin.write('y\n')
		stdin.flush()
		response = ''.join(stdout.readlines())

		if 'Successfully updated' in response:
			return self.response(True)

		return self.response(False)