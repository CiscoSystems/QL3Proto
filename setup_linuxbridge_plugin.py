try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import version

import sys

Name = 'quantum-linuxbridge-plugin'
ProjecUrl = ""
Version = version.get_git_version()
License = 'Apache License 2.0'
Author = 'Cisco Systems Inc.'
AuthorEmail = 'snaiksat@cisco.com'
Maintainer = 'Netstack Community'
Summary = 'Linux Bridge plugin for Quantum'
ShortDescription = Summary
Description = Summary

requires = [
    'quantum-common',
    'quantum-server',
    'python-configobj>=4.7.2',
    'bridge-utils>=1.4',
]

EagerResources = [
    'quantum',
]

ProjectScripts = [
]

PackageData = {
}

# If we're installing server-wide, use an aboslute path for config
# if not, use a relative path
config_path = '/etc/quantum/plugins/linuxbridge'
relative_locations = ['--user', '--virtualenv', '--venv']
if [x for x in relative_locations if x in sys.argv]:
    config_path = 'etc/quantum/plugins/linuxbridge'

DataFiles = [
    (config_path,
    ['etc/quantum/plugins/linuxbridge/linuxbridge_plugin.ini',
     'linuxbridge_quantum_etc/quantum/plugins/linuxbridge/agent.ini'])
]

setup(
    name=Name,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    install_requires=requires,
    include_package_data=True,
    packages=["quantum.plugins.linuxbridge"],
    package_data=PackageData,
    data_files=DataFiles,
    eager_resources=EagerResources,
)
