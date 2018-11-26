"""CLI for use Devo API from shell command line."""

import sys
import os
import click
from devo.common import Configuration
from devo.api import Client, DevoClientException
from devo.common.data.buffer import Buffer
from ..proccessors import proc_default

# Groups
# ------------------------------------------------------------------------------


@click.group()
def cli():
    """Empty group"""
    pass

# Commands
# ------------------------------------------------------------------------------


@cli.command()
@click.option('--config', '-c', type=click.Path(),
              help='JSON File with configuration, you can put all options here',
              default="~/.devo.json")
@click.option('--url', '-u', help='Endpoint for the api.')
@click.option('--api_key', '--apiKey', '--key', help='Key for the api.')
@click.option('--api_secret', '--apiSecret', '--secret', help='Secret for the api.')
@click.option('--api_token', '--apiToken', '--token', help='Secret for the api.')
@click.option('--query', '-q', help='Query.')
@click.option('--stream/--no-stream',
              help='Flag for make streaming query or full query with start and '
                   'end. Default is true', default=True)
@click.option('--proc', help='if flag exists, dont return raw query reply. In '
                             'compact replies you receive proccessed lines.',
              is_flag=True)
@click.option('--output', help='File path to store query response if not want '
                               'stdout')
@click.option('--format', '-f', default="json/simple/compact",
              help='The output format. Default is json/simple/compact')
@click.option('--from',
              help='From date, and time for the query (YYYY-MM-DD hh:mm:ss). '
                   'For valid formats see lt-common README')
@click.option('--to',
              help='To date, and time for the query (YYYY-MM-DD hh:mm:ss). '
                   'For valid formats see lt-common README')
def query(**kwargs):
    """Perform query by query string"""
    api, config = configure(kwargs)

    if config['query'] is None:
        print_error("Error: Not query provided.", show_help=True)

    buffer = api.query(query=config['query'],
                       dates={"from": config['from'],
                              "to": config['to'] if "to" in config.keys()
                                    else None},
                       format=config['format'],
                       stream=config['stream'])

    process_response(buffer, config)

# Utils
# ------------------------------------------------------------------------------


def identify_response(response, config):
    """
    Identify what type of response are we received from Client API
    :param response: data received from Devo Client API
    :param config: array with launch options
    :return: proccessed line (List or string normally)
    """
    return {
        'json': lambda x, y: proc_default(x) if y else x,
        'json/compact': lambda x, y: x,
        'json/simple': lambda x, y: list(x),
        'json/simple/compact': lambda x, y: list(x)
    }[config['format']](response, config['proc'])


def process_response(response, config):
    """
    Proccess responses from Client API
    :param response: data received from Devo API
    :param config: array with launch options
    :return: None
    """
    if not isinstance(response, Buffer) or not config['stream']:
        response = identify_response(response, config)

    try:
        file_printer = open(config['output'], 'w') if 'output' in config.keys()\
            else None
    except (OSError, IOError) as error:
        print_error("Error: (%s)" % error)

    if isinstance(response, Buffer):
        while True:
            if file_printer is None:
                response.get(click.echo)
            else:
                response.get(file_printer.write)
    else:
        if not isinstance(response, Buffer):
            click.echo(response, file_printer)
        else:
            response.get(click.echo)


def list_to_csv(lst):
    """
    Convert list to string separated by comma
    :param lst: Python list
    :return: string
    """
    return '"' + '","'.join(lst) + '"'


def configure(args):
    """
    Load CLI configuration
    :param args: args from files, launch vars, etc
    :return: Client API Object and Config values in array
    """
    config = Configuration()
    if args.get('config') != "~/.devo.json":
        config.load_json(args.get('config'), 'api')

    config.mix(dict(args))

    if "key" not in args.keys() and "api" not in args.keys() \
            and "token" not in args.keys():
        config.set("key", os.environ.get('DEVO_API_KEY', None))
        config.set("secret", os.environ.get('DEVO_API_SECRET', None))
        if "url" not in args.keys():
            config.set("url", os.environ.get('DEVO_API_URL', None))

    if not config.keys("key") and not config.keys("api") \
            and not config.keys("token") \
            and os.path.exists("~/.devo.json"):
        config.load_default_json('api')

    config.keys('from')
    config.keys('to')

    # Try to compose the api
    api = None
    try:
        api = Client.from_config(config.get())
    except DevoClientException as error:
        print_error(str(error), show_help=True)
    return api, config.get()


def print_error(error, show_help=False, stop=True):
    """Class for print error in shell when exception"""
    click.echo(click.style(error, fg='red'), err=True)
    if show_help:
        click.echo("")
        click.echo(click.get_current_context().get_help())
    if stop:
        sys.exit(1)
