import os
import versioneer
from setuptools import setup
from setuptools import find_packages

versioneer.versionfile_source = "simple_resizer/_version.py"
versioneer.VCS = "git"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = "django-simple-resizer-"

README = open(os.path.join(os.path.dirname(__file__), "README.md")).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-simple-resizer",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A simple image resizer",
    long_description=README,
    url="https://github.com/zakdoek/django-simple-resizer.git",
    author="Tom Van Damme",
    author_email="t_o_mvandamme@hotmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    install_requires=[
        "Wand==0.4.1",
        "Pillow==2.8.1",
    ],
)
