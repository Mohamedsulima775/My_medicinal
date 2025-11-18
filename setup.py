from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in my_medicinal/__init__.py
from my_medicinal import __version__ as version

setup(
	name="my_medicinal",
	version=version,
	description="enhancing pharmaceutical care services",
	author="mohammedsuliman",
	author_email="mohamedsuliman923@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
