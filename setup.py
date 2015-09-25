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
                        'pylsl>=1.10.4',
                        'colorama>=0.3.3'],
      entry_points={"console_scripts":
                    ["lslgraph = lslgraph.lslgraph:run_from_cli",
                     "lslscan = lslgraph.lslscan:scan_ui"]})
