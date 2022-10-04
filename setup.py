from setuptools import setup, find_packages

setup(
    name='j2py',
    version='0.3.3.6',
    license='gpl-3.0',
    author="Alberto Brandolini",
    author_email='brando1411@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ArcticBlueOrange/jupyterconverter',
    keywords='j2py jupyter-converter notebook',
    description='CLI and GUI Utility for converting jupyter notebooks.',
    long_description='''CLI and GUI Utility for converting jupyter notebooks.
    I made this script because I wasn't satisfied with the current solutions.
    This allows to easily create multi-cell ipynb notebooks from python files and, vice-versa, to create super-clean python scripts from highly commented notebooks.
    It has a GUI mode when opened with no arguments, while the CLI mode can accept multiple inputs and outputs at the same time, making it usable by another script.
    It's currently tested on Windows, if you have any problems on Linux please let me know.''',
)
