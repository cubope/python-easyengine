from .base import Server
from .. import EasyEngineException
from ..util import validate_country, validate_domain, validate_email

class Site(Server):
	name = 'Site'
	
	service_site = [
		'html', 'php', 'mysql'
	]
	
	service_wordpress = [
		'wp', 'wpfc', 'w3tc', 'wpsc', 'wpredis',
	]
	
	_service = 'wp'

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
			stdin, stdout, stderr = self.execute('ee site info %s' % self._domain)

			response = ''.join(stdout.readlines())

			if 'does not exist' in response:
				return False

			return True

		raise EasyEngineException

	def create(self, domain, service=None):
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
		data  = {}

		for line in lines:
			if 'Successfully created site' in line:
				url = line.replace('\x1b[94mSuccessfully created site ', '').replace('\x1b[0m\n','')

				data.update({'url': url})
			elif 'WordPress admin user : ' in line:
				username = line.replace('\x1b[94m\x1b[0m','').replace('WordPress admin user : ', '').replace('\x1b[0m\n', '')

				data.update({'username': username})
			elif 'WordPress admin user password : ' in line:
				password   = line.replace('\x1b[94m\x1b[0m','').replace('WordPress admin user password : ', '').replace('\x1b[0m\n', '')		
				
				data.update({'password': password})

		return self.response(data)

	def delete(self, domain):
		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site delete %s --no-prompt' % self._domain)
		stdout.readlines()

		return self.response(True)

	def list(self):
		data = list()

		stdin, stdout, stderr = self.execute('ee site list')
		lines = stdout.readlines()

		for line in lines:
			domain = line.replace('\x1b[94m\x1b[0m', '').replace('\x1b[0m\n','')
			data.append(domain)

		return self.response(data)

	def info(self, domain):
		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site info %s' % self._domain)
		lines = stdout.readlines()
		data  = {}

		for line in lines:
			if 'Webroot' in line:
				webroot = line.replace('Webroot', '').lstrip().rstrip('\r\n')
				
				data.update({'webroot': webroot})
			elif 'DB_NAME' in line:
				db_name = line.replace('DB_NAME', '').lstrip().rstrip('\r\n')
				
				data.update({'db_name': db_name})
			elif 'DB_USER' in line:
				db_user = line.replace('DB_USER', '').lstrip().rstrip('\r\n')
				
				data.update({'db_user': db_user})
			elif 'DB_PASS' in line:
				db_pass = line.replace('DB_PASS', '').lstrip().rstrip('\r\n')
				
				data.update({'db_pass': db_pass})

		return self.response(data)

	def update(self, domain, service=None, user=None, password=None):
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
		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site enable %s' % self._domain)
		stdout.readlines()

		return self.response(True)

	def disable(self, domain):
		self._domain = validate_domain(domain)

		if not self.exists():
			raise EasyEngineException

		stdin, stdout, stderr = self.execute('ee site disable %s' % self._domain)
		stdout.readlines()

		return self.response(True)

	def generate_csr(self, domain, country, state, city, company, industry, email):
		self._domain   = validate_domain(domain)
		self._path     = '/var/www/%s' % self._domain
		self._country  = validate_country(country)
		self._state    = state
		self._city     = city
		self._company  = company
		self._industry = industry
		self._email    = validate_email(email)

		if not self.exists():
			raise EasyEngineException

		# Delete certs folders
		command = (
			'rm -rf %s/cert/' % self._path
		)
		stdin, stdout, stderr = self.execute(command)
		stdout.readlines()

		command = (
			'mkdir %s/cert/ && ' % self._path +
			'cd %s/cert/ && ' % self._path +
			'openssl genrsa -out %s.key 2048 && ' %  self._domain +
			'openssl req -new -key %(domain)s.key -out %(domain)s.csr -sha256' % dict(domain=self._domain) 
		)
		stdin, stdout, stderr = self.execute(command)

		payload = '%(country)s\n%(state)s\n%(city)s\n%(company)s\n%(industry)s\n%(domain)s\n%(email)s\n\n\n' % dict(
			country  = self._country,
			state    = self._state,
			city     = self._city,
			company  = self._company,
			industry = self._industry,
			domain   = self._domain,
			email    = self._email,
		)
		stdin.write(payload)
		stdin.flush()
		stdout.readlines()

		command = 'cd %s/cert/ && cat %s.csr' % (self._path, self._domain)
		stdin, stdout, stderr = self.execute(command)
		response = ''.join(stdout.readlines())

		data = {'csr': response}

		return self.response(data)

	def install_ssl(self, domain, certificate_code, ca_chain):
		self._domain           = validate_domain(domain)
		self._path             = '/var/www/%s' % self._domain
		self._certificate_code = certificate_code
		self._ca_chain         = ca_chain

		if not self.exists():
			raise EasyEngineException

		# Write certificate
		command = 'echo "%(certificate_code)s" >> %(path)s/cert/%(domain)s.crt' % dict(
			certificate_code = self._certificate_code,
			path             = self._path,
			domain           = self._domain
		)
		stdin, stdout, stderr = self.execute(command)
		stdout.readlines()
		
		# Write CA chain
		command = 'echo "%(ca_chain)s" >> %(path)s/cert/%(domain)s.crt' % dict(
			ca_chain = self._ca_chain,
			path     = self._path,
			domain   = self._domain
		)
		stdin, stdout, stderr = self.execute(command)
		stdout.readlines()

		# Verify matching
		command = 'diff  <(openssl x509 -in %(path)s/cert/%(domain)s.crt -pubkey -noout) <(openssl rsa -in %(path)s/cert/%(domain)s.key -pubout)' % dict(
			path   = self._path,
			domain = self._domain
		)
		stdin, stdout, stderr = self.execute(command)
		errors = stderr.readlines()

		if len(errors):
			# Insert information
			command = (
				"sed -i '/www.%(domain)s;/a\    listen 80;" % dict(domain=self._domain) +
				"\\n    listen 443 ssl spdy;" +
				"\\n    ssl on;" +
				"\\n    ssl_certificate %(path)s/cert/%(domain)s.crt;" % dict(path=self._path, domain=self._domain) +
				"\\n    ssl_certificate_key %(path)s/cert/%(domain)s.key;' /etc/nginx/sites-available/%(domain)s" % dict(path=self._path, domain=self._domain)
			)
			stdin, stdout, stderr = self.execute(command)
			stdout.readlines()

			# Reload nginx
			command = 'service nginx reload'
			stdin, stdout, stderr = self.execute(command)
			stdout.readlines()

			return self.response(True)
		else:
			# Remove
			command = 'rm -rf  %(path)s/cert/%(domain)s.crt' % dict(
				path             = self._path,
				domain           = self._domain
			)
			stdin, stdout, stderr = self.execute(command)
			stdout.readlines()

			return self.response(False)

	def uninstall_ssl(self, domain):
		self._domain = validate_domain(domain)
		self._path   = '/var/www/%s' % self._domain

		if not self.exists():
			raise EasyEngineException

		command = (
			"sed -i '/listen 80;/d' /etc/nginx/sites-available/%(domain)s && " % dict(domain=self._domain) +
			"sed -i '/listen 443 ssl spdy;/d' /etc/nginx/sites-available/%(domain)s && " % dict(domain=self._domain) +
			"sed -i '/ssl on;/d' /etc/nginx/sites-available/%(domain)s && " % dict(domain=self._domain) +
			"sed -i '/ssl_certificate %(path)s/cert/%(domain)s.crt;/d' /etc/nginx/sites-available/%(domain)s && " % dict(path=self._path, domain=self._domain) +
			"sed -i '/ssl_certificate_key %(path)s/cert/%(domain)s.key;/d' /etc/nginx/sites-available/%(domain)s" % dict(path=self._path, domain=self._domain)
		)
		stdin, stdout, stderr = self.execute(command)
		stdout.readlines()

		command = (
			"rm -rf %(path)s/cert/%(domain)s.crt" % dict(path=self._path, domain=self._domain)
		)
		stdin, stdout, stderr = self.execute(command)
		stdout.readlines()

		return self.response(True)