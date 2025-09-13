from setuptools import setup

setup(
    name='ntfyer',
    version='1.0.0-alpha',
    install_requires=[
        "click>=8.2.1",
        "httpx>=0.28.1",
        "pendulum>=3.1.0",
        "sqlalchemy>=2.0.43",
    ],
)
