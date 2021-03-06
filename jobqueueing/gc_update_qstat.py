#!python
"""
Update the status of entries in generate climos queue using `qstat`.

`qstat` is called for each submitted job in the queue, and the result is used to
update the queue entry for that job.
"""

import re
from subprocess import Popen, PIPE

from dateutil import parser as dateparser
import yaml

from jobqueueing.script_helpers import logger
from jobqueueing import GenerateClimosQueueEntry


def qstat_to_yaml(string):
    """Convert the output of `qstat -f -1` to a YAML-compliant string so it
    can easily be parsed. """
    job_id_re = re.compile(r'^Job Id: (.*)$', re.MULTILINE)
    string = job_id_re.sub(r'-\n    pbs_job_id: \1', string)
    key_val_re = re.compile(r' = ', re.MULTILINE)
    string = key_val_re.sub(r': ', string)
    return string


def update_from_qstat_item(session, entry, qstat_item):
    """
    Update the status of entries in generate climos queue from output of a
    'qstat` command for a single PBS job.

    :param session: database session
    :param entry: queue entry to be updated
    :param qstat_item: dict encoding the output of a 'qstat` command for a
        single PBS job
    :return: None
    """
    logger.info('Updating {}'.format(entry.pbs_job_id))
    start_time = qstat_item.get('start_time', None)
    if start_time and entry.status == 'SUBMITTED':
        logger.info('Sub -> Run')
        entry.status = 'RUNNING'
        entry.started_time = dateparser.parse(start_time)

    comp_time = qstat_item.get('comp_time', None)
    if comp_time and entry.status == 'RUNNING':
        logger.info('Run -> Succ')
        entry.status = 'SUCCESS'
        entry.completed_time = dateparser.parse(comp_time)
        entry.completion_message = \
            yaml.dump(qstat_item, default_flow_style=False)

    session.commit()


def update(session):
    """
    Update the status of entries in generate climos queue using `qstat`.

    :param session: database session
    :return: None
    """
    entries = (
        session.query(GenerateClimosQueueEntry)
        .filter(GenerateClimosQueueEntry.status.in_(['SUBMITTED', 'RUNNING']))
        .all()
    )
    for entry in entries:
        qstat = Popen(['qstat', '-f', '-1', entry.pbs_job_id], stdout=PIPE)
        stdout, stderr = qstat.communicate()
        qstat_item = yaml.load(qstat_to_yaml(stdout.decode('utf-8')))[0]
        update_from_qstat_item(session, entry, qstat_item)

