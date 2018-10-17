from setuptools import find_packages, setup

DESC = 'Yet Another Specification Inference Tool.'

setup(
    name='yasit',
    version='0.0.0',
    description=DESC,
    url='http://github.com/mvcisback/yasit',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'attr',
        'funcy',
        'networkx'
    ],
    packages=find_packages(),
)
