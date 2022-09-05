from setuptools import setup, find_packages

setup(
    name='j2py',
    version='0.3',
    license='gpl-3.0',
    author="Alberto Brandolini",
    author_email='brando1411@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ArcticBlueOrange/jupyterconverter',
    keywords='j2py jupyter-converter',
    # install_requires=[ 'pathlib', ],
)
