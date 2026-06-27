import subprocess
from pathlib import Path

from dockwatch.models import DockerImage


class SbomGenerator:
    """Generates CycloneDX SBOMs using the syft binary."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, image: DockerImage) -> Path:
        output_file = self.output_dir / f"{image.safe_filename}.json"
        command = [
            "syft",
            image.reference,
            "-o",
            f"cyclonedx-json={output_file}",
        ]
        subprocess.run(command, check=True)
        return output_file
