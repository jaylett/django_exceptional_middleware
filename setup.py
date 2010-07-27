# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'django_exceptional_middleware'
VERSION = '0.2'

data_files = [
    (
        'exceptional_middleware/templates/http_responses', [ 'exceptional_middleware/templates/http_responses/default.html' ],
    ),
]

setup(
    name=PACKAGE, version=VERSION,
    description="Django middleware to allow generating arbitrary HTTP status codes via exceptions.",
    packages=[ 'exceptional_middleware' ],
    data_files=data_files,
    license='MIT',
    author='James Aylett',
    url = 'http://tartarus.org/james/computers/django/',
)
