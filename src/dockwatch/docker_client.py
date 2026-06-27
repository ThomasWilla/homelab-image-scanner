import docker

from dockwatch.models import DockerImage


class DockerClient:
    """Thin wrapper around the Docker SDK."""

    def __init__(self) -> None:
        self._client = docker.from_env()

    def list_images(self) -> list[DockerImage]:
        images: list[DockerImage] = []
        for image in self._client.images.list():
            image_id = image.id
            for tag in image.tags:
                if not tag or tag.startswith("<none>"):
                    continue
                repository, version = tag.rsplit(":", maxsplit=1)
                images.append(
                    DockerImage(
                        image_id=image_id,
                        repository=repository,
                        tag=version,
                    )
                )
        return sorted(images, key=lambda item: item.reference)
