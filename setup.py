from setuptools import setup
from codecs import open
from daowalletsdk import SDK_VERSION


with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='daowalletsdk',
    description='B2B SDK for DAOWallet API',
    long_description=readme,
    long_description_content_type='text/markdown',
    version=SDK_VERSION,
    packages=['daowalletsdk'],
    url='URL on homepage',
    project_urls={
        'Documentation': 'Link on docs',
        'Source': 'link on repo',
    },
    license='MIT',

    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: SDK',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    keywords='daowallet cryptocurrency development',

    author='Anton',
    author_email='grand.toxa@gmail.com',

    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=['requests'],
    test_suite="tests",
    platforms=['any'],
)
