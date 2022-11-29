"""Set up cloudstats python module cli scripts."""

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="multijuju",
    # use_scm_version={"local_scheme": "node-and-date"},
    version="1.0",
    description="collects and exports juju machine status metrics",
    long_description=readme,
    author="Canonical BootStack DevOps Centres",
    url="https://github.com/canonical/multijuju",
    license=license,
    packages=["multijuju"],
    package_data={"multijuju": ["config_default.yaml"]},
    entry_points={
        "console_scripts": [
            "multijuju=multijuju.cli:main",
        ]
    },
    # setup_requires=["setuptools_scm"],
)
