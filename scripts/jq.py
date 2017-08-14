#!python

from argparse import ArgumentParser
import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobqueueing.argparse_helpers import \
    add_global_arguments, \
    add_listing_arguments, \
    add_gcadd_arguments, \
    add_execution_environment_arguments, \
    add_generate_climos_arguments, \
    add_pbs_arguments, \
    add_ext_submit_arguments, \
    add_reset_arguments, \
    add_submit_arguments
from jobqueueing.script_helpers import logger

from jobqueueing.gcadd import add_to_generate_climos_queue
from jobqueueing.gcalter_params import updatable_params, \
    update_generate_climos_queue_entries_with_params
from jobqueueing.gclist import list_entries
from jobqueueing.gcreset import reset_generate_climos_queue_entry
from jobqueueing.gcsub import submit_generate_climos_pbs_jobs
from jobqueueing.gcupd_email import \
    update_generate_climos_queue_from_status_email
from jobqueueing.gcupd_qstat import update


def create_session(database):
    dsn = 'sqlite+pysqlite:///{}'.format(database)
    engine = create_engine(dsn)
    return sessionmaker(bind=engine)()


def args_dict(args, names):
    """Return a dict containing arguments selected by name
    from the ``args`` parameter.
    Absent arguments are given the value ``None``.
    """
    return {name: getattr(args, name, None) for name in names}


def add(session, args):
    return add_to_generate_climos_queue(
        session,
        **args_dict(args,
                    '''
                    input_filepath
                    py_venv
                    output_directory
                    convert_longitudes
                    split_vars
                    split_intervals
                    ppn
                    walltime
                    submitted
                    pbs_job_id
                    force
                    '''.split())
    )


def alter_params(session, args):
    return update_generate_climos_queue_entries_with_params(
        session,
        args.input_filepath,
        **args_dict(args, updatable_params)
    )


def list(session, args):
    return list_entries(
        session,
         **args_dict(args, 'input_filepath pbs_job_id status full'.split())
    )


def reset(session, args):
    return reset_generate_climos_queue_entry(
        session, args.input_filepath, args.status)


def submit(session, args):
    return submit_generate_climos_pbs_jobs(session, args.number, args.test_job)


def update_from_email(session, args):
    return update_generate_climos_queue_from_status_email(
        session, '\n'.join(sys.stdin))


def update_with_qstat(session, args):
    return update(session)


if __name__ == '__main__':
    # main (jq) parser
    main_parser = ArgumentParser()
    global_args_group = add_global_arguments(main_parser)

    subparsers = main_parser.add_subparsers()

    # add
    add_parser = subparsers.add_parser(
        'add',
        help='Add a file to the queue for processing with generate_climos'
    )
    add_parser.set_defaults(action=add)
    add_execution_environment_arguments(add_parser)
    add_pbs_arguments(add_parser)
    add_generate_climos_arguments(add_parser)
    add_gcadd_arguments(add_parser)
    add_ext_submit_arguments(add_parser)

    # alter-params
    alter_params_parser = subparsers.add_parser(
        'alter-params',
        help='''
    Update entries with generate_climos params and PBS params (but not status).
    Updated entry must be in status NEW.
    WARNING: ANY entry that partially matches the input filename is updated.'''
    )
    alter_params_parser.set_defaults(action=alter_params)
    add_execution_environment_arguments(alter_params_parser, required=False)
    add_pbs_arguments(alter_params_parser, ppn_default=None, walltime_default=None)
    add_generate_climos_arguments(alter_params_parser, o_required=False, flag_default=None)

    # list
    list_parser = subparsers.add_parser(
        'list',
        help='List entries in generate_climos queue'
    )
    list_parser.set_defaults(action=list)
    add_listing_arguments(list_parser)

    # reset
    reset_parser = subparsers.add_parser(
        'reset',
        help='Reset the status of a queue entry'
    )
    reset_parser.set_defaults(action=reset)
    add_reset_arguments(reset_parser)

    # submit
    submit_parser = subparsers.add_parser(
        'submit',
        help='Reset the status of a queue entry'
    )
    submit_parser.set_defaults(action=submit)
    add_submit_arguments(submit_parser)

    # update-email
    update_email_parser = subparsers.add_parser(
        'update-email',
        help='Update generate_climos queue using PBS status email'
    )
    update_email_parser.set_defaults(action=update_from_email)

    # update-qstat
    update_qstat_parser = subparsers.add_parser(
        'update-qstat',
        help='Update generate_climos queue using PBS qstat'
    )
    update_qstat_parser.set_defaults(action=update_with_qstat)

    # Parse args and dispatch to action handler
    args = main_parser.parse_args()
    logger.setLevel(getattr(logging, args.loglevel))
    session = create_session(args.database)
    exit_status = args.action(session, args)
    sys.exit(exit_status)
