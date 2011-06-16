# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

PACKAGE = 'django_exceptional_middleware'
VERSION = '0.9'

package_data = {
        'exceptional_middleware': [ 'templates/http_responses/*.html' ],
}

setup(
    name=PACKAGE, version=VERSION,
    description="Django middleware to allow generating arbitrary HTTP status codes via exceptions.",
    packages=[ 'exceptional_middleware' ],
    package_data=package_data,
    license='MIT',
    author='James Aylett',
    url = 'http://tartarus.org/james/computers/django/',
)
