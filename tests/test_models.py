from dockwatch.models import DockerImage


def test_docker_image_reference_and_project_name() -> None:
    image = DockerImage(
        image_id="sha256:123",
        repository="ghcr.io/example/app",
        tag="latest",
    )

    assert image.reference == "ghcr.io/example/app:latest"
    assert image.project_name == "app"
    assert image.project_version == "latest"
    assert image.safe_filename == "ghcr.io_example_app_latest"
