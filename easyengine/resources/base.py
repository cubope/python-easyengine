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
		if self._client:
			return

		kwargs = {
			'username': self._username,
			'password': self._password
		}

		if hasattr(self, '_port'):
			kwargs.update({'port': self._port	})

		self._client = paramiko.SSHClient()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._client.connect(self._host, **kwargs)

	def __eq__(self, other):
		return (isinstance(other, self.__class__) and self.__dict__ == other.__dict__)

	def __hash__(self):
		return hash(frozenset(self.__dict__))

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return "<%s %s>" % (self.__class__.__name__, self.name[0:5])

	def _close(self):
		if hasattr(self, '_data'):
			self._data = {}

		if self._client:
			self._client.close()
			self._client = False

	def execute(self, command):
		if not self._client:
			self._connect()

		return self._client.exec_command(command)

	def is_install(self):		
		stdin, stdout, stderr = self.execute('ee')

		response = ''.join(stderr.readlines())

		if 'command not found' in response:
			return False

		return True

	def response(self, data):
		self._close()

		return data

	def __str__(self):
		return self.name