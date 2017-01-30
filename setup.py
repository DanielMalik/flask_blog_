from setuptools import setup

setup(
    name='app',
    packages=['bloog'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)