from .base import Server
from .. import EasyEngineException
from ..util import validate_ip, validate_port

class Secure(Server):
	name  = 'Secure'

	def auth(self, user=None, password=None):
		command = 'ee secure --auth'
		
		if not user and not password:
			credentials = False
		elif user and password:
			self._user     = validate_user(user)
			self._password = password
			command = '%s %s %s' % (command, self._user, self._password)
		else:
			raise EasyEngineException
		
		stdin, stdout, stderr = self.execute(command)

		if not credentials:
			stdin.write('\n\n')
			stdin.flush()

			lines = stdout.readlines()

			for line in lines:
				if 'HTTP authentication user name' in line:
					user = line.replace('Provide HTTP authentication user name [', '').replace(']', '').lstrip().rstrip('\r\n')
					
					self._user = user
				elif 'HTTP authentication password' in line:
					password = line.replace('Provide HTTP authentication password [', '').replace(']', '').lstrip().rstrip('\r\n')
					
					self._password = password

		data = {
			'user': self._user,
			'password':	self._password
		}

		return self.response(data)

	def port(self, port):
		self._port = validate_port(port)

		stdin, stdout, stderr = self.execute('ee secure --port %d' % self._port)
		stdout.readlines()

		return self.response(True)

	def ip(self, ip):
		if isinstance(ip, list):
			for ip_single in ip:
				validate_ip(ip_single)

			ip = ','.join(ip)
		else:
			ip = validate_ip(ip)

		stdin, stdout, stderr = self.execute('ee secure --ip %s' % ip)
		stdout.readlines()

		return self.response(True)