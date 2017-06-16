from setuptools import setup
import sys

setup(
    name='PyTattle',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A library for automated user stats and error reporting.',
    url='https://github.com/biologyguy/PyTattle',
    author='Steve Bond, John Didion',
    author_email='<steve email>, john.didion@nih.gov',
    license='MIT',
    packages = ['pytattle'],
    tests_require = ['pytest', 'pytest-cov'],
    extras_require = {
        'github' : ['github3']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'License :: Public Domain',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.6',
    ]
)
