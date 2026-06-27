from dataclasses import dataclass


@dataclass(frozen=True)
class DockerImage:
    """Normalized Docker image metadata."""

    image_id: str
    repository: str
    tag: str

    @property
    def reference(self) -> str:
        return f"{self.repository}:{self.tag}"

    @property
    def project_name(self) -> str:
        return self.repository.rsplit("/", maxsplit=1)[-1]

    @property
    def project_version(self) -> str:
        return self.tag

    @property
    def safe_filename(self) -> str:
        return self.reference.replace("/", "_").replace(":", "_")
