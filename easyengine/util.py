import re
import socket
from . import EasyEngineException


def validate_country(country):
    if len(country) > 2:
        raise EasyEngineException("Invalid country.")

    return country


def validate_domain(domain):
    domain = str(domain)

    HOSTNAME_LABEL_PATTERN = re.compile("(?!-)[A-Z\d-]+(?<!-)$", re.IGNORECASE)

    if not domain:
        raise EasyEngineException("No value was provided.")

    if len(domain) > 255:
        raise EasyEngineException(
            "The domain name cannot be composed of more than 255 characters."
        )

    if domain[-1:] == ".":
        domain = domain[:-1]

    for label in domain.split("."):
        if len(label) > 63:
            raise EasyEngineException(
                "The label '%(label)s' is too long (maximum is 63 characters)."
                % {'label': label}
            )
        if not HOSTNAME_LABEL_PATTERN.match(label):
            raise EasyEngineException(
                "Unallowed characters in label '%(label)s'." % {'label': label}
            )

    return domain


def validate_email(email):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    if not EMAIL_REGEX.match(email):
        raise EasyEngineException("Invalid email.")

    return email


def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        raise EasyEngineException


def validate_port(port):
    port = int(port)

    if port < 1000 or port > 65535:
        raise EasyEngineException("Not a valid port value.")

    return port


def validate_user(user):
    return re.sub(r'\W+', '-', user)
