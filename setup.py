# setup.py
from setuptools import setup, find_packages

setup(
    name='AdNetworkBudgetAlert',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'certifi==2023.11.17',
        'charset-normalizer==3.3.2',
        'idna==3.6',
        'requests==2.31.0',
        'urllib3==2.1.0',
    ],
    author='Gin',
    author_email='qjz0202@gmail.com',
    description='A short description of the package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/yourpackagename',
)
