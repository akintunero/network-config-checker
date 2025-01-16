from setuptools import setup, find_packages

setup(
    name="network-config-checker",
    version="0.1.0",
    author="Olumayowa Akinkuehinmi",
    author_email="akintunero101@gmail.com",
    description="A tool to check network configurations against security policies.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/akintunero/network-config-checker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "netmiko",
        "napalm",
        "pyyaml",
        "jinja2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "network-config-checker=main:main",
        ],
    },
)
