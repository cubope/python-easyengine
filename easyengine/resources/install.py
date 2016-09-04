from ..util import validate_email
from .base import Server

class Install(Server):
	name = 'Install'

	def do(self, name, email):
		if self.is_install():
			return self.response(False)
			
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

	def update(self):
		if not self.is_install():
			return self.response(False)
		
		stdin, stdout, stderr = self.execute('ee update')
		""" Agree """
		stdin.write('y\n')
		stdin.flush()

		stdout.readlines()

		return self.response(True)