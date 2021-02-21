import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name = 'ziaplot',
    version = '0.1b1',
    description = 'Draw light-weight plots, graphs, and charts',
    author = 'Collin J. Delker',
    author_email = 'ziaplot@collindelker.com',
    url = 'https://ziaplot.readthedocs.io/',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        'Source': 'https://bitbucket.org/cdelker/ziaplot',
    },
    python_requires='>=3.7',
    packages=setuptools.find_packages(),
    keywords = ['plot', 'chart', 'graph', 'smith chart', 'bar', 'pie'],
    install_requires=[],
    extras_require={'cairo':  ['cairosvg']},
    classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: End Users/Desktop',
    ],
)
