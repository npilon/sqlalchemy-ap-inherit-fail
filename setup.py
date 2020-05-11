import setuptools

setuptools.setup(
    name="sqlalchemy-ap-inherit-fail",
    version="0.0.1",
    author="Nicholas Pilon",
    author_email="npilon@gmail.com",
    description="Minimal example to reproduce an SQLAlchemy bug",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/npilon/sqlalchemy-ap-inherit-fail",
    packages=setuptools.find_packages("./src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["sqlalchemy==1.3.16"],
    entry_points={
        "console_scripts": [
            "sqlalchemy_ap_inherit_fail = sqlalchemy_ap_inherit_fail:main",
        ]
    },
)
