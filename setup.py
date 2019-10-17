from setuptools import setup
from setuptools import find_packages
import re


with open('requirements.txt') as f:
    requirements = [l.strip() for l in f]

with open('dependency_links.txt') as f:
    dependency_links = [l.strip() for l in f]

# # filter non-standard requirements
# reqexp = re.compile(r"[^\w><=\.\s-]")
# nonstandard = list(filter(reqexp.search, requirements))
# requirements = list(filter(lambda w: not(reqexp.search(w)), requirements))

# if nonstandard:
#     if sys.argv[1] != "clean":
#         print("Non-standard requirements found. These will have to installed manually. The non-standard requirements are:")
#         print(nonstandard)

with open("README.md", "r") as f:
    long_description = f.read()

with open("LICENSE", "r") as f:
    license_text = f.read()

version = None
versionRegex = re.compile(r"\d+[.]\d+[.]\d+[^\s]*")
with open("CHANGELOG.md", "r") as f:
    for line in f:
        versionMatch = versionRegex.match(line)
        if versionMatch:
            version = versionMatch.group()
            break


setup(
    name='knowl',
    version=version or "0.0.1",
    # use_scm_version=True,
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
    # setup_requires=['setuptools_scm'],
    packages=find_packages(exclude=["tests", "data"]),
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
