# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'django_exceptional_middleware'
VERSION = '0.1'

data_files = [
    (
        'exceptional_middleware/templates/http_responses', [ 'exceptional_middleware/templates/http_responses/default.html' ],
    ),
]

setup(
    name=PACKAGE, version=VERSION,
    packages=[ 'exceptional_middleware' ],
    data_files=data_files,
    license='MIT',
    author='James Aylett',
    url = 'http://tartarus.org/james/django/',
)
