from setuptools import setup, find_packages

setup(name='jupydbg',
      version='0.1.1',
      description='Cell magic to inspect the stack after an error + Interactive unittest player', 
      url='http://github.com/gcoffin/jupydbg',
      author='Guillaume Coffin',
      author_email='guill.coffin@gmail.com',
      license='GPLv3',
      packages = find_packages(exclude=['build', 'dist','docs','_build']),
      package_data = {
        },
      install_requires = ['six'],
      download_url = 'https://github.com/gcoffin/jupydbg/archive/0.1.tar.gz',
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        ],
      keywords='interactive unittest debug stack'
)
