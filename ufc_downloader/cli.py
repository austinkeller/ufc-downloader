import sys
import logging
import click
from .importer import import_downloads as import_downloads_func
from .indexer import update_index

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--loglevel",
    default="INFO",
    help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
def cli(loglevel):
    logging.basicConfig(
        level=getattr(logging, loglevel.upper(), None),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.command()
@click.option(
    "--force",
    is_flag=True,
    help="Force re-indexing of events even if they are already up-to-date.",
)
@click.option(
    "--freshness_days",
    default=7,
    type=int,
    help="Specify the freshness level for the events to be indexed in days.",
)
def index_events(force, freshness_days):
    click.echo(
        f"Indexing events with force={force} and freshness_days={freshness_days}..."
    )
    if update_index(force_update=force, freshness_days=freshness_days):
        logger.info("Events successfully updated.")
        sys.exit(0)
    else:
        logger.error("Failed to update events.")
        sys.exit(1)


@click.command()
@click.option("--interactive", is_flag=True, help="Run in interactive mode.")
def import_downloads(interactive):
    click.echo("Importing downloads...")
    if import_downloads_func(interactive=interactive):
        logger.info("Downloads successfully imported.")
        sys.exit(0)
    else:
        logger.error("Failed to import downloads.")
        sys.exit(1)


cli.add_command(index_events)
cli.add_command(import_downloads)

if __name__ == "__main__":
    cli()
