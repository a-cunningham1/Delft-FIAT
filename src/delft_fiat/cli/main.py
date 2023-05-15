from delft_fiat.log import Log
from delft_fiat.main import FIAT
from delft_fiat.version import __version__
from delft_fiat.cli.util import Path, file_path_check

import click


@click.group(
    options_metavar="<options>",
    subcommand_metavar="<command>",
)
@click.version_option(__version__, message=f"Delft-FIAT v{__version__}")
@click.pass_context
def main(ctx):
    if ctx.obj is None:
        ctx.obj = {}


_cfg = click.argument(
    "cfg",
    metavar="<cfg>",
    type=str,
    callback=file_path_check,
)

_verbose = click.option("-v", "--verbose", count=True, help="Increase verbosity")


@main.command(
    short_help="Information concerning Delft-FIAT",
    options_metavar="<options>",
)
@click.pass_context
def info(
    ctx,
):
    pass


@main.command(
    short_help="Run Delft-FIAT via a settings file",
    options_metavar="<options>",
)
@_cfg
@_verbose
@click.pass_context
def run(
    ctx,
    cfg,
    verbose,
):
    """
    \b
    <cfg>  Configurations file (toml) containing the settings for the FIAT model
    """
    model = FIAT(cfg)
    print(verbose)
    model.run()


if __name__ == "__main__":
    main()
