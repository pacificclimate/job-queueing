from setuptools import setup


__version__ = (0, 2, 2)

setup(
    name='jobqueueing',
    description='PCIC PBS job queueing support tools',
    version='.'.join(str(d) for d in __version__),
    author='Rod Glover',
    author_email='rglover@uvic.ca',
    url='https://github.com/pacificclimate/jobqueueing',
    packages=['jobqueueing'],
    keywords='PBS job queue',
    zip_safe=True,
    install_requires='''
        alembic
        PyYAML
    '''.split(),
    scripts='''
        scripts/jq
    '''.split(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]

)