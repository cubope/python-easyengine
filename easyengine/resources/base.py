import paramiko

class Server(object):
	name = 'Server'
	
	_client = False

	def __init__(self, host, username, password, port=None, *args, **kwargs):
		"""
		Connect to an SSH server and authenticate to it.

		:param str hostname: the server to connect to
		:param int port: the server port to connect to
		:param str username:
			the username to authenticate as (defaults to the current local
			username)
		:param str password:
			a password to use for authentication or for unlocking a private key

		:raises AuthenticationException: if authentication failed
		:raises SSHException: if there was any other error connecting or
			establishing an SSH session
		:raises socket.error: if a socket error occurred while connecting
		"""
		self._host     = host
		self._username = username
		self._password = password

		if port:
			self._port = int(port)

	def _connect(self):
		kwargs = {
			'username': self._username,
			'password': self._password
		}

		if hasattr(self, '_port'):
			kwargs.update({'port': self._port	})

		self._client = paramiko.SSHClient()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._client.connect(self._host, **kwargs)

	def _close(self):
		if self._client:
			self._client.close()
			self._client = False
	
	def execute(self, command):
		return self._client.exec_command(command)

	def response(self, data):
		self._close()

		return data

	def __str__(self):
		return self.name