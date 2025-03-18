import typer
import uvicorn
from .main import app  # Import your FastAPI app

cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@cli.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """Start the FastAPI web server."""
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    cli()
