from setuptools import setup, find_packages

classifiers = [
    'Developement Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9.5'
]

setup(
name = 'trading_returns_analysis',
version ='1.0.0',
description = 'trading_returns _analysis modules contains function to analyze a timeseries of trading returns. Such as, cumulative returns monthly returns, etc.',
url= 'https://github.com/Iankfc/trading_returns_analysis',
author='ece',
author_email='odesk5@outlook.com',
license = 'None',
classifiers=classifiers,
keywords='None',
packages=find_packages(),
use_scm_version=True,
include_package_data=True,
setup_requires=['setuptools_scm'],
install_requires=[  'numpy==1.21.1',
                    'trading_direction==1.0.2.dev0+gd8a0b66.d20210830',
                    'scipy==1.7.1',
                    'plotly==5.1.0',
                    'pandas==1.2.5',
                    'asset_price_etl==0.1.dev1+g035dd12.d20210903',
                    'trading_exit_price==1.0.3.dev0+g790298a.d20210904']
)