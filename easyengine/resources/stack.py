from .base import Server
from .. import EasyEngineException
from ..util import validate_domain

class Stack(Server):
	name = 'Stack'

	services_stack = [
		'hhvm'
	]