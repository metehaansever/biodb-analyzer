from setuptools import setup, find_packages

setup(
    name="biodb-analyzer",
    version="0.1.0",
    description="BioDB Analyzer - Tool for analyzing bioinformatics databases",
    author="Metehan Sever",
    author_email="metehaansever@gmail.com",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={'': ['*.json']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'biodb-analyzer=biodb_analyzer.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    install_requires=[
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'sqlalchemy>=2.0.0',
        'plotly>=5.15.0',
        'scipy>=1.10.0',
        'statsmodels>=0.14.0',
        'python-dotenv>=1.0.0',
        'click>=8.1.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
