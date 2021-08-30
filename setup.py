from setuptools import setup
from setuptools import find_packages
import os

setup_dir = (os.path.dirname(os.path.realpath(__file__)))

with open(os.path.join(setup_dir, 'requirements.txt')) as f:
    requirements = [l.strip() for l in f]

with open(os.path.join(setup_dir, 'dependency_links.txt')) as f:
    dependency_links = [l.strip() for l in f]

test_requirements = [
    'pytest', 'coverage', 'pytest-cov', 'pyyaml', "codecov", "sqlite3"
]

with open(os.path.join(setup_dir, "README.md"), "r") as f:
    long_description = f.read()

setup(
    name='knowl',
    use_scm_version=False,
    description='Knowledge Ontology-based OOP language',
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Imitation Learning Group CIIRC CVUT',
    maintainer_email='radoslav.skoviera@cvut.cz',
    url='',
    download_url='',
    license='Mozilla Public License Version 2.0',
    install_requires=requirements,
    dependency_links=dependency_links,
    package_dir={'': "src"},
    include_package_data=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages("src", exclude=["tests", "data"]),
    extras_require={
        "test": test_requirements
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"
    ]
)
