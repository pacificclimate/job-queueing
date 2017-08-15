==========================
PCIC PBS Job Queueing Tool
==========================

Purpose
=======

The PCIC PBS Job Queueing tool (hereafter, JQ) is a command-line tool for managing and recording the
submission of jobs to the PCIC compute nodes via PBS.

PBS (``qsub`` et al.) is a third-party tool that manages queueing and running of jobs on the PCIC compute nodes.
Even alone, PBS is very useful, but we have some additional requirements that are not directly met by it:

- Submit similar jobs (scripts) repeatedly with varying parameters (e.g, files to be processed).
- Record the fact and outcome of each such job permanently.

The solution is centered on a database that manages and records submissions to the PBS queue.
Since adding something to the database does not have to cause it to be submitted immediately
(nor is that necessarily desirable), JQ is effectively a "queue for a queue" in addition to its
function as a record-keeping service.

Installation
============

First, clone the project repository from github::

    $ git clone git@github.com:pacificclimate/jobqueueing.git

As usual, it is best to install JQ in a Python virtual environment::

    $ cd jobqueueing
    $ python3 -m venv venv
    $ venv/bin/activate
    (venv) $ pip install --upgrade pip
    (venv) $ pip install .

This installs the ``jq.py`` command-line script. Verify installation by running::

    (venv) $ jq.py --help

Configuration
=============

There's little to configure in JQ, just a couple of environment variables and those all optional:

- ``GCQ_DATABASE``: The Job Queueing database to run against. There are at present two standard databases
  set up on the gluster storage nodes.
  The location of these databases may change in future (but will remain on gluster).

  - ``/storage/data/projects/comp_support/climate_exporer_data_prep/climatological_means/jobqueue-prod.sqlite``
  - ``/storage/data/projects/comp_support/climate_exporer_data_prep/climatological_means/jobqueue-test.sqlite``

  The test database (``jobqueue-test.sqlite``) is exclusively for testing JQ, and should not be used for
  normal operations.

- ``GCQ_PY_VENV``: The Python virtual environment in which to run *the script submitted to PBS*.
  (This is *not* the same as the virtual environment you are running JQ from!)

  There is a predefined environment suitable for JQ jobs at
  ``/storage/data/projects/comp_support/climate_exporer_data_prep/climatological_means/venv``
  which should be used in most cases.

In short, your JQ configuration should normally be::

    $ export GCQ_DATABASE=/storage/data/projects/comp_support/climate_exporer_data_prep/climatological_means/jobqueue-prod.sqlite
    $ export GCQ_PY_VENV=/storage/data/projects/comp_support/climate_exporer_data_prep/climatological_means/venv

Usage
=====

JQ commands are all of the form::

    jq.py [<global options>] <action> [<action options>]

To find out what the options and actions are, run::

    (venv) $ jq.py -h

To find out the options for specific actions, run::

    (venv) $ jq.py <action> -h

Actions overview
----------------

The actions available are, in alphabetical order:

- ``add``: Add a file to the queue for processing with generate_climos
- ``alter-params``: Update entries with generate_climos params and PBS params (but not status). 
  Updated entry must be in status NEW. 
  WARNING: ANY entry that partially matches the input filename is updated.
- ``list``: List entries in generate_climos queue
- ``reset``: Reset the status of a queue entry
- ``submit``: Dequeue one or more generate_climos queue entries with NEW status,
  and submit a PBS job for each, updating the queue entries accordingly.
- ``update-email``: Update generate_climos queue using PBS status email
- ``update-qstat``: Update generate_climos queue using PBS qstat

JQ workflow
===========

This section describes the workflow for JQ. It describes the various states defined for JQ entries, and
the actions that cause transitions from one state to another. The general format is

<JQ STATE>
    description

    *Action*: Something that causes transition to --> <JQ STATE>

The JQ workflow is:

[no queue entry]
    *Action*: Add to queue (``jq add``)
        --> new JQ entry with status NEW

NEW
    Job exists in JQ but has not been submitted to PBS.

    *Action*: Submit (``jq submit``)
        --> SUBMITTED

SUBMITTED
    Job has been submitted to PBS. Actual state of PBS job is unknown.
    The JQ state can be updated to reflect the PBS state by manual actions, see below.

    Now there is also a PBS status for the job, but it is not updated dynamically in JQ.

    *Action*: Update status while PBS job is running (``jq update-email`` or ``jq update-qstat``)
        --> RUNNING
    *Action*: Update status after PBS job has terminated with success (``jq update-email`` or ``jq update-qstat``)
        --> SUCCESS
    *Action*: Update status after PBS job has terminated with error (``jq update-email`` or ``jq update-qstat``)
        --> ERROR

RUNNING
    Job has been submitted to PBS, and PBS job is known to be running.

    *Action*: Update status after PBS job has terminated with success (``jq update-email`` or ``jq update-qstat``)
        --> SUCCESS
    *Action*: Update status after PBS job has terminated with error (``jq update-email`` or ``jq update-qstat``)
        --> ERROR

SUCCESS
    Job has been submitted to PBS, and  PBS job completed normally.

ERROR
    Job has been submitted to PBS, and PBS job errored.