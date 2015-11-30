from setuptools import setup

setup(
    name="fdanalytics",
    version="0.1",
    description="Flaredown analytics API",
    url="",
    author="Flaredown",
    author_email="colin@fathom.digital",
    license="",
    packages=["fdanalytics"],
    install_requires=[
        "flask",
        "flask_heroku",
        "flask_restful",
        "flask_testing",
        "flask_pymongo"
    ],
    test_suite="nose.collector",
    tests_require=["nose"],
    zip_safe=False,
)
