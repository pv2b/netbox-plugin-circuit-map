from setuptools import setup, find_packages

version = '0.0.1'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='netbox-plugin-circuit-map',
    version=version,
    description='A simple circuit map with filter criteria',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author='Per von Zweigbergk',
    author_email='pvz@pvz.pp.se',
    url='https://github.com/pv2b/netbox-plugin-circuit-map',
    download_url='https://github.com/drygdryg/netbox-plugin-circuit-map/archive/v{}.zip'.format(version),
    python_requires='>3.10',
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
