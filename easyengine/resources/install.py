from ..util import validate_email
from .base import Server

class Install(Server):
	name = 'Install'

	def is_install(self):
		stdin, stdout, stderr = self.execute('ee')

		response = ''.join(stderr.readlines())

		if 'ee: command not found' in response:
			return False

		return True

	def do(self, name, email):
		if not self._client:
			self._connect()

		if not self.is_install():
			self._name  = str(name)
			self._email = validate_email(email)

			""" Install command """
			stdin, stdout, stderr = self.execute('wget -qO ee rt.cx/ee && sudo bash ee')
			""" Set name and email """
			stdin.write('%s\n%s\n' % (self._name, self._email))
			stdin.flush()
			""" Execute """
			stdout.readlines()

			""" Add to .bash_profile """
			stdin, stdout, stderr = self.execute('source /etc/bash_completion.d/ee_auto.rc')
			response = stderr.readlines()

			if 'No such file or directory' in response:
				return self.response(False)

			return self.response(True)

		return self.response(False)

	def update(self):
		self._connect()

		if not self.is_install():
			stdin, stdout, stderr = self.execute('ee update')
			""" Agree """
			stdin.write('y\n')
			stdin.flush()

			stdout.readlines()

			return self.response(True)

		return self.response(False)