import typer
import uvicorn
from .main import app  # Import your FastAPI app

cli = typer.Typer()

@cli.command()
def run(
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """Start the FastAPI web server."""
    uvicorn.run(app, host=host, port=port, reload=False)

if __name__ == "__main__":
    cli()