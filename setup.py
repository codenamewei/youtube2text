from setuptools import find_packages
from setuptools import setup

setup(
    name='youtube2text',
    version='0.0.1',
    install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'numpy', 
        # Recommend not to fix the versions 
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/codenamewei/youtube2text',
    license='MIT',
    author='Your NAME',
    author_email='your@email.com',
    description='Your main project'
)