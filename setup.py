from setuptools import setup
from setuptools import find_packages


with open('requirements.txt') as f:
    requirements = [l.strip() for l in f]

with open('dependency_links.txt') as f:
    dependency_links = [l.strip() for l in f]

test_requirements = [
    'pytest', 'coverage', 'pytest-cov', 'pyyaml', "codecov"
]

with open("README.md", "r") as f:
    long_description = f.read()

with open("LICENSE", "r") as f:
    license_text = f.read()

setup(
    name='knowl',
    use_scm_version=True,
    description='Knowledge Ontology-based OOP language',
    long_description=long_description,
    author='Imitation Learning Group CIIRC CVUT',
    maintainer_email='radoslav.skoviera@cvut.cz',
    url='',
    download_url='',
    license=license_text,
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ]
)
