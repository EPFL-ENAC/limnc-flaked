import typer
import uvicorn
from pathlib import Path
from .main import app  # Import your FastAPI app
from .services.config import config_service

cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@cli.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
    config: str = typer.Option(
        None, help="Path to the configuration file (optional)"),
):
    """Start the FastAPI web server."""
    if config:
        config_service.load_config(Path(config))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    cli()
