import logging
import time

import typer

from dockwatch.config import get_settings
from dockwatch.dependencytrack import DependencyTrackClient
from dockwatch.docker_client import DockerClient
from dockwatch.sbom import SbomGenerator
from dockwatch.state import StateStore

app = typer.Typer(help="Docker image SBOM scanner for Dependency-Track.")


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def scan_once() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    docker_client = DockerClient()
    state = StateStore(settings.state_db_path)
    sbom_generator = SbomGenerator(settings.output_dir)
    dependencytrack = DependencyTrackClient(
        base_url=settings.dependencytrack_base_url,
        api_key=settings.dependencytrack_api_key,
    )

    images = docker_client.list_images()
    logging.info("Discovered %s Docker images", len(images))

    for image in images:
        if state.has_current_image(image):
            logging.info("Skipping unchanged image: %s", image.reference)
            continue

        logging.info("Processing image: %s", image.reference)
        project_uuid = state.get_project_uuid(image)
        if not project_uuid:
            project_uuid = dependencytrack.get_or_create_project_uuid(image)
            logging.info("Using Dependency-Track project UUID: %s", project_uuid)

        bom_file = sbom_generator.generate(image)
        dependencytrack.upload_bom(project_uuid, bom_file)
        state.save_image(image, project_uuid)
        logging.info("Uploaded SBOM for %s", image.reference)


@app.command()
def run_once() -> None:
    """Run a single scan and exit."""

    scan_once()


@app.command()
def run() -> None:
    """Run scans continuously based on SCAN_INTERVAL_SECONDS."""

    settings = get_settings()
    configure_logging(settings.log_level)

    while True:
        try:
            scan_once()
        except Exception:
            logging.exception("Scan failed")
        logging.info("Sleeping for %s seconds", settings.scan_interval_seconds)
        time.sleep(settings.scan_interval_seconds)


if __name__ == "__main__":
    app()
