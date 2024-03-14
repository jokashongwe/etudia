from distutils.core import setup
setup(
   name='Etudia',
   author='Jonathan Kashongwe',
   description='Etudia AI Bot',
   version='0.1',
   packages=['backend', 'bot', 'backend.model', 'backend.classes'],
   install_requires=['wheel', 'bar', 'greek'],
   license='MIT',
   author_email='jokashongwe@gmail.com',
   long_description=open('README.txt').read(),
)