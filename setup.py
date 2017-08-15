from setuptools import setup


__version__ = (0, 1, 0)

setup(
    name='jq',
    description='PCIC PBS job queueing support tools',
    version='.'.join(str(d) for d in __version__),
    author='Rod Glover',
    author_email='rglover@uvic.ca',
    url='https://github.com/pacificclimate/jobqueueing',
    keywords='PBS job queue',
    zip_safe=True,
    install_requires='''
        alembic
        PyYAML
    '''.split(),
    scripts='''
        scripts/gcadd.py
        scripts/gcalter-params.py
        scripts/gclist.py
        scripts/gcreset.py
        scripts/gcsub.py
        scripts/gcupd-email.py
        scripts/gcupd-qstat.py
    '''.split(),
    classifiers='''
        Development Status :: 4 - Beta,
        Environment :: Console,
        Intended Audience :: Developers,
        Intended Audience :: Science/Research,
        License :: OSI Approved :: GNU General Public License v3 (GPLv3)
        Operating System :: OS Independent,
        Programming Language :: Python :: 2.7,
        Programming Language :: Python :: 3.5,
        Programming Language :: Python :: 3.6,
        Topic :: Scientific/Engineering,
        Topic :: Database,
        Topic :: Software Development :: Libraries :: Python Modules
    '''.split()

)