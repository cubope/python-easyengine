from . import Server
from .. import EasyEngineException
from ..util import validate_domain

class Site(Server):
	name = 'Site'
	
	service_site = [
		'html', 'php', 'mysql'
	]
	
	service_wordpress = [
		'wp', 'wpfc', 'w3tc', 'wpsc', 'wpredis',
	]
	
	_service = 'wp'

	_data = {}

	def is_wordpress(self):
		if self._service in self.service_wordpress:
			return True

		return False

	def validate_service(self, service):
		if service not in self.service_site and service not in self.service_wordpress:
			raise EasyEngineException

		return service

	def exists(self):
		if hasattr(self, '_domain'):
			if not self._client:
				self._connect()
			
			stdin, stdout, stderr = self.execute('ee site info %s' % self._domain)

			response = ''.join(stdout.readlines())

			if 'does not exist' in response:
				return False

			return True

		raise EasyEngineException

	def create(self, domain, service=None):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)
		
		if self.exists():
			raise EasyEngineException
		
		if service:
			self._service = self.validate_service(service)

		stdin, stdout, stderr = self.execute('ee site create %s --%s' % (self._domain, self._service))

		if self._service == 'wpredis':
			stdin.write('y\n')
			stdin.flush()

		lines = stdout.readlines()

		for line in lines:
			if 'Successfully created site' in line:
				url = line.replace('\x1b[94mSuccessfully created site ', '').replace('\x1b[0m\n','')

				self.data.update({'url': url})
			elif 'WordPress admin user:' in line:
				username = line.replace('\x1b[94m\x1b[0mWordPress admin user : ', '').replace('\x1b[0m\n', '')

				self.data.update({'username': username})
			elif 'WordPress admin user password:' in line:
				password   = line.replace('\x1b[94m\x1b[0mWordPress admin user password : ', '').replace('\x1b[0m\n', '')		
				
				self.data.update({'password': password})

		return self.response(data)


	def delete(self, domain):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site delete %s --no-prompt' % self._domain)
		stdout.readlines()

		return self.response(data)

	def list(self):
		if not self._client:
			self._connect()

		self._data.update({'sites': list()})

		stdin, stdout, stderr = self.execute('ee site list')
		lines = stdout.readlines()

		for line in lines:
			domain = line.replace('\x1b[94m\x1b[0m', '').replace('\x1b[0m\n','')
			self._data['sites'].append(domain)

		return self.response(self._data)

	def info(self, domain):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site info %s' % self._domain)
		lines = stdout.readlines()

		for line in lines:
			if 'Webroot' in line:
				webroot = line.replace('Webroot', '').lstrip().rstrip('\r\n')
				
				self._data.update({'webroot': webroot})
			elif 'DB_NAME' in line:
				db_name = line.replace('DB_NAME', '').lstrip().rstrip('\r\n')
				
				self._data.update({'db_name': db_name})
			elif 'DB_USER' in line:
				db_user = line.replace('DB_USER', '').lstrip().rstrip('\r\n')
				
				self._data.update({'db_user': db_user})
			elif 'DB_PASS' in line:
				db_pass = line.replace('DB_PASS', '').lstrip().rstrip('\r\n')
				
				self._data.update({'db_pass': db_pass})

		return self.response(self._data)

	def update(self, domain, service=None, user=None, password=None):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		if user and password:
			self._user     = user
			self._password = password
		elif service:
			self._service = validate_service(service)
		else:
			raise EasyEngineException

		if hasattr(self, '_user') and hasattr(self, '_password'):
			stdin, stdout, stderr = self.execute('ee site update %s --password' % self._domain)
			stdin.write('%s\n%s' % (self._user, self._password))
			stdin.flush()

			response = ''.join(stdout.readlines())
			
			if 'Password updated successfully' in response:
				return self.response(True)
		else:
			stdin, stdout, stderr = self.execute('ee site update %s --%s' % (self._domain, self._service))
			response = ''.join(stdout.readlines())
			
			if 'Successfully updated' in response:
				return self.response(True)

		return self.response(False)

	def enable(self, domain):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site enable %s' % self._domain)
		stdout.readlines()

		return self.response(True)

	def disable(self, domain):
		if not self._client:
			self._connect()

		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site disable %s' % self._domain)
		stdout.readlines()

		return self.response(True)