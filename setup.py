from setuptools import setup, find_packages

setup(
    name = 'particle',
    version = '0.0.7',
    description = "",
    long_description = "",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    keywords = 'analytics, data science, social media',
    author = 'Brian Abelson',
    author_email = 'brianabelson@gmail.com',
    url = 'http://github.com/abelsonlive/particle',
    license = 'MIT',
    packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages = [],
    include_package_data = False,
    zip_safe = False,
    install_requires = [
        "PyYAML >= 3.10",
        "charade >= 1.0.3",
        "feedparser >= 5.1.3",
        "python-dateutil >= 1.5",
        "pytz >= 2012d",
        "readability-lxml >= 0.3.0.2",
        "cssselect >= 0.9.1",
        "redis >= 2.8.0",
        "selenium >= 2.39.0",
        "thready >= 0.1.2",
        "tweepy >= 2.1",
        "facepy >= 0.8.4",
        "boilerpipe >= 1.2.0.0",
        "Flask >= 0.10.1"
    ],
    tests_require = [],
        entry_points = {
          'console_scripts': [
                'particle = particle:cli', 
          ]
        }
)
