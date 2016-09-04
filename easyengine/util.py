import re
from . import EasyEngineException

def validate_email(email):
	EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

	if not EMAIL_REGEX.match(email):
		raise EasyEngineException

	return email

def validate_domain(domain):
	HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)
	
	if not domain:
		raise EasyEngineException
	
	if len(domain) > 255:
		raise EasyEngineException("The domain name cannot be composed of more than 255 characters.")
	
	if domain[-1:] == ".":
		domain = domain[:-1]  # strip exactly one dot from the right, if present
	
	for label in domain.split("."):
		if len(label) > 63:
			raise EasyEngineException(
				"The label '%(label)s' is too long (maximum is 63 characters)." % {'label': label})
		if not HOSTNAME_LABEL_PATTERN.match(label):
			raise EasyEngineException("Unallowed characters in label '%(label)s'." % {'label': label})

	return domain
