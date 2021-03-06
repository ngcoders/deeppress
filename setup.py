import setuptools

setuptools.setup(
    name="deeppress",
    version="0.0.1",
    author="Gopal Lal",
    author_email="gopal@baseapp.com",
    description="Image classification and object detection. Train models in a easy way.",
    url="https://baseapp.com",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'deeppress = deeppress.main'
        ]
    }
)