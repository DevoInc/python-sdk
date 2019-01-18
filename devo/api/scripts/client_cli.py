"""CLI for use Devo API from shell command line."""

import sys
import os
import click
from devo.common import Configuration
from devo.api import Client, DevoClientException

# Groups
# ------------------------------------------------------------------------------


@click.group()
def cli():
    """Empty group"""
    pass

# Commands
# ------------------------------------------------------------------------------


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Optional JSON/Yaml File with configuration info.')
@click.option('--env', '-e', help='Use env vars for configuration',
              default=False)
@click.option('--default', '-d', help='Use default file for configuration',
              default=False)
@click.option('--url', '-u', help='Endpoint for the api.')
@click.option('--user', '-user', help='User for the api.')
@click.option('--app_name', '-app_name', help='Application name for the api.')
@click.option('--comment', '-comment', help='Comment for the queries.')
@click.option('--api_key', '--apiKey', '--key', help='Key for the api.')
@click.option('--api_secret', '--apiSecret', '--secret',
              help='Secret for the api.')
@click.option('--api_token', '--apiToken', '--token',
              help='Secret for the api.')
@click.option('--query', '-q', help='Query.')
@click.option('--stream/--no-stream',
              help='Flag for make streaming query or full query with '
              'start and end. Default is true', default=True)
@click.option('--output', help='File path to store query response if not want '
                               'stdout')
@click.option('--response', '-r', default="json/simple/compact",
              help='The output format. Default is json/simple/compact')
@click.option('--from', default=None,
              help='From date, and time for the query (YYYY-MM-DD hh:mm:ss). '
                   'For valid formats see lt-common README')
@click.option('--to', default=None,
              help='To date, and time for the query (YYYY-MM-DD hh:mm:ss). '
                   'For valid formats see lt-common README')
def query(**kwargs):
    """Perform query by query string"""
    api, config = configure(kwargs)

    if config['query'] is None:
        print_error("Error: Not query provided.", show_help=True)

    reponse = api.query(query=config['query'],
                        dates={"from": config['from'],
                               "to": config['to'] if "to" in config.keys()
                                                    else None},
                        response=config['response'],
                        stream=config['stream'])

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
    :return: Client API Object and Config values in array
    """
    config = Configuration()
    try:
        if args.get('config'):
            config.load_config(args.get('config'), 'api')

        if args.get('env'):
            config.set("key", os.environ.get('DEVO_API_KEY', None))
            config.set("secret", os.environ.get('DEVO_API_SECRET', None))
            config.set("url", os.environ.get('DEVO_API_URL', None))
            config.set("user", os.environ.get('DEVO_API_USER', None))
            config.set("comment", os.environ.get('DEVO_API_COMMENT', None))

        if args.get('default'):
            config.load_default_config(section="api")
    finally:
        config.mix(dict(args))
        conf = config.get()

    # Try to compose the api
    api = None
    try:
        api = Client.from_config(conf)
    except DevoClientException as error:
        print_error(str(error), show_help=True)
    return api, conf


def print_error(error, show_help=False, stop=True):
    """Class for print error in shell when exception"""
    click.echo(click.style(error, fg='red'), err=True)
    if show_help:
        click.echo("")
        click.echo(click.get_current_context().get_help())
    if stop:
        sys.exit(1)
