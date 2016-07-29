import pkg_resources

from gevent import monkey
monkey.patch_all()

__version__ = pkg_resources.get_distribution("populus").version
