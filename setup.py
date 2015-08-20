from setuptools import setup

setup(name='lslgraph',
      version='0.0.1',
      description='Real-time graphing tool for lab streaming layer streams.',
      author='Jari Torniainen, Brain Work Research Center at the Finnish Institute of Occupational Health',
      author_email='jari.torniainen@ttl.fi',
      url='https://github.com/jtorniainen/lslgraph',
      license='MIT',
      packages=['lslgraph'],
      package_dir={'lslgraph': 'lslgraph'},
      include_package_data=False,
      install_requires=['pyqtgraph>=0.9.10',
                        'PyZMQ>=14.3.1',
                        'Waitress>=0.8.9',
                        'pylsl>=1.10.4'],
      entry_points={"console_scripts":
                    ["lslgraph = lslgraph:run_from_cli"]})
