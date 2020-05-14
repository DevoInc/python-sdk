#!/usr/bin/env python3
"""CLI for use Devo API from shell command line."""
import os
import click
import sys
from devo.common import Configuration
from devo.api.client import Client, DevoClientException, ERROR_MSGS
from devo.__version__ import __version__

# Groups
# ------------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option('--version', "-v", is_flag=True, default=False)
def cli(version):
    """ Initialize click """
    if version:
        pkg_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..",
        ))
        click.echo("devo-sdk {!s} from {!s} (python {!s})"
                   .format(__version__, pkg_dir, sys.version[:3]))

# Commands
# ------------------------------------------------------------------------------


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Optional JSON/Yaml File with configuration info.')
@click.option('--env', '-e', help='Use env vars for configuration',
              default=False)
@click.option('--default', '-d', help='Use default file for configuration',
              default=False)
@click.option('--address', '-a', help='Endpoint for the api.')
@click.option('--user', help='User for the api.')
@click.option('--app_name', help='Application name for the api.')
@click.option('--comment', help='Comment for the queries.')
@click.option('--key', help='Key for the api.')
@click.option('--secret', help='Secret for the api.')
@click.option('--token', help='Secret for the api.')
@click.option('--jwt', help='JWT auth for the api.')
@click.option('--query', '-q', help='Query.', default="")
@click.option('--stream/--no-stream',
              help='Flag for make streaming query or full query with '
              'start and end. Default is true', default=True)
@click.option('--output', help='File path to store query response if not want '
                               'stdout')
@click.option('--response', '-r', default="json/simple/compact",
              help='The output format. Default is json/simple/compact')
@click.option('--from',
              help='From date. For valid formats see API README.'
                   ' Default if now - 1 hour')
@click.option('--to',
              help='To date. For valid formats see API README')
@click.option('--timeZone',
              help='Timezone info. For valid formats see API README')
@click.option('--verify', type=bool, help='Verify certificates')
@click.option('--debug/--no-debug', help='For testing purposes', default=False)
def query(**kwargs):
    """Perform query by query string"""
    api, config = configure(kwargs)

    if config is None:
        print_error("Error in config", show_help=True)
        if config['debug']:
            return
        exit()

    if not config['query']:
        print_error(ERROR_MSGS['no_query'], show_help=True)
        if config['debug']:
            return
        exit()

    dates = {}
    if "to" in config.keys():
        dates["from"] = config['from']
    if "to" in config.keys():
        dates["to"] = config['to']
    if "timeZone" in config.keys():
        dates['timeZone'] = config['timeZone']

    reponse = api.query(query=config['query'], dates=dates)

    process_response(reponse, config)


def process_response(response, config):
    """
    process responses from Client API
    :param response: data received from Devo API
    :param config: array with launch options
    :return: None
    """
    try:
        file_printer = open(config['output'], 'w')\
         if 'output' in config.keys() else None
    except (OSError, IOError) as error:
        print_error("Error: (%s)" % error)

    if not Client.stream_available(config['response']):
        config['stream'] = False

    printer = line_printer(file_printer)
    if config['stream']:
        for item in response:
            printer(item)
    else:
        printer(response)


def line_printer(file_printer):
    if file_printer is None:
        return lambda line: click.echo(line)
    return lambda line: file_printer.write(line)


def configure(args):
    """
    Load CLI configuration
    :param args: args from files, launch vars, etc
    :return: Clien  t API Object and Config values in array
    """
    config = Configuration()
    try:
        if args.get('config'):
            config.load_config(args.get('config'), 'api')

        if args.get('env'):
            config.set("key", os.environ.get('DEVO_API_KEY', None))
            config.set("secret", os.environ.get('DEVO_API_SECRET', None))
            config.set("token", os.environ.get('DEVO_API_TOKEN', None))
            config.set("jwt", os.environ.get('DEVO_API_JWT', None))
            config.set("address", os.environ.get('DEVO_API_ADDRESS', None))
            config.set("user", os.environ.get('DEVO_API_USER', None))
            config.set("comment", os.environ.get('DEVO_API_COMMENT', None))
            config.set("retries", os.environ.get('DEVO_API_RETRIES', None))
            config.set("timeout", os.environ.get('DEVO_API_TIMEOUT', None))

        if args.get('default'):
            config.load_default_config(section="api")
    except Exception as error:
        print_error(str(error), show_help=True)
    finally:
        config.mix(dict(args))

    # Try to compose the api
    try:
        api = Client(config=config)
    except DevoClientException as error:
        print_error(str(error), show_help=True)
        if isinstance(error, DevoClientException):
            raise DevoClientException(error.args[0])
        else:
            raise DevoClientException(str(error.args[0]))

    return api, config


def print_error(error, show_help=False):
    """Class for print error in shell when exception"""
    if show_help:
        click.echo("")
        click.echo(click.get_current_context().get_help())
    click.echo(click.style(error, fg='red'), err=True)
