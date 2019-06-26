# -*- coding: utf-8 -*-
"""CLI for use Devo Sender from shell command line."""

import sys
try:
    import click
except ImportError as import_error:
    print(str(import_error), "- Use 'pip install click' or install this "
                             "package with [click] option")
    sys.exit(1)

import os
from devo.common import Configuration
from ..lookup import Lookup
from ..data import Sender, DevoSenderException
from devo.__version__ import __version__
# Groups
# ------------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option('--version', "-v", is_flag=True, default=False)
def cli(version):
    """ Initialize click """
    pkg_dir =  os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
    ))
    click.echo("devo-sdk {!s} from {!s} (python {!s})".format(__version__,
                                                              pkg_dir,
                                                              sys.version[:3]))


# Commands
# ------------------------------------------------------------------------------
@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Optional JSON/Yaml File with configuration info.')
@click.option('--address', '-a', help='Devo relay address')
@click.option('--port', '-p', help='Devo relay address port')
@click.option('--key', help='Devo user key cert file.')
@click.option('--cert', help='Devo user cert file.')
@click.option('--chain', help='Devo chain.crt file.')
@click.option('--multiline/--no-multiline', help='Flag for multiline (With '
                                                 'break-line in msg). '
                                                 'Default False', default=False)
@click.option('--type', help='Connection type: SSL or TCP', default="SSL")
@click.option('--tag', '-t', help='Tag / Table to which the data will be sent '
                                  'in Devo.', default="test.drop.ltsender")
@click.option('--line', '-l',
              help='For shipments of only one line, '
                   'the text you want to send.', default="David Hasselhoff")
@click.option('--file', '-f', help='The file that you want to send to Devo,'
                                   ' which will be sent line by line.',
              default="")
@click.option('--header', '-h', help='This option is used to indicate if the'
                                     ' file has headers or not, not to send '
                                     'them.', default=False)
@click.option('--raw', is_flag=True, help='Send raw events from a '
                                          'file when using --file')
@click.option('--debug/--no-debug', help='For testing purposes', default=False)
def data(**kwargs):
    """Send data to devo"""
    config = configure(kwargs)
    sended = 0
    try:
        con = Sender(config=config)
        if config['file']:
            if not os.path.isfile(config['file']):
                print_error(str("File not exist"))
                return
            if config['multiline']:
                with open(config['file'], 'r') as file:
                    content = file.read()
                    if not config['raw']:
                        sended += con.send(tag=config['tag'], msg=content,
                                           multiline=config['multiline'])
                    else:
                        sended += con.send_raw(content,
                                               multiline=config['multiline'])
            else:
                with open(config['file']) as file:
                    if config['header']:
                        next(file)
                    for line in file:
                        if config['raw']:
                            sended += con.send_raw(line)
                        else:
                            sended += con.send(tag=config['tag'], msg=line)
        else:
            sended += con.send(tag=config['tag'], msg=config['line'])

        con.close()
        if config.get("debug", False):
            click.echo("Sended: %s" % str(sended))
    except DevoSenderException as error:
        print_error(str(error))
        if config.get('debug', False):
            raise DevoSenderException(str(error))
        exit()
    except Exception as error:
        print_error(str(error))


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Optional JSON/Yaml File with configuration info.')
@click.option('--env', '-e', help='Use env vars for configuration',
              default=False)
@click.option('--default', '-d', help='Use default file for configuration',
              default=False)
@click.option('--url', '--address', '-a', help='Devo relay address')
@click.option('--port', '-p', default=443, help='Devo relay address port')
@click.option('--key', help='Devo user key cert file.')
@click.option('--cert', help='Devo user cert file.')
@click.option('--chain', help='Devo chain.crt file.')
@click.option('--type', help='Connection type: SSL or TCP', default="SSL")
@click.option('--name', '-n', help='Name for Lookup.')
@click.option('--file', '-f', help='The file that you want to send to Devo,'
                                   ' which will be sent line by line.')
@click.option('--lkey', '-lk', help='Name of the column that contains the '
                                    'Lookup key. It has to be the exact name '
                                    'that appears in the header.')
@click.option('--delimiter', '-d', help='CSV Delimiter char.', default=",")
@click.option('--quotechar', '-qc', help='CSV Quote char.', default='"')
@click.option('--debug/--no-debug', help='For testing purposes', default=False)
def lookup(**kwargs):
    """Send csv lookups to devo"""
    config = configure_lookup(kwargs)
    con = Sender(config=config)
    lookup = Lookup(name=config['name'], historic_tag=None, con=con)

    with open(config['file']) as file:
        line = file.readline()

        lookup.send_csv(config['file'], delimiter=config['delimiter'],
                         quotechar=config['quotechar'],
                         headers=line.rstrip().split(config['delimiter']),
                         key=config['lkey'])


def configure(args):
    """ Configuration of Sender CLI """
    return init_conf(args)


def init_conf(args):
    """ Generic configuration of CLI, from config file and cli arguments """
    config = Configuration()
    try:
        if args.get('config'):
            config.load_config(args.get('config'), 'sender')

        if args.get('env'):
            config.set("address",
                       os.environ.get('DEVO_SENDER_ADDRESS',
                                      os.environ.get('DEVO_SENDER_URL', None)))
            config.set("port", os.environ.get('DEVO_SENDER_PORT', None))
            config.set("key", os.environ.get('DEVO_SENDER_KEY', None))
            config.set("cert", os.environ.get('DEVO_SENDER_CERT', None))
            config.set("chain", os.environ.get('DEVO_SENDER_CHAIN', None))

        if args.get('default'):
            config.load_default_config(section="sender")
    finally:
        config.mix(dict(args))
        return config


def configure_lookup(args):
    """ Configuration of Lookup for CLI """
    config = init_conf(args)
    if args.get('config'):
        config.load_config(args.get('config'), 'lookup')
    if "url" in config.keys():
        config.set("address", config.get("url"))

    return config


def print_error(error, show_help=False):
    """Class for print error in shell when exception"""
    if show_help:
        click.echo("")
        click.echo(click.get_current_context().get_help())
    click.echo(click.style(error, fg='red'), err=True)