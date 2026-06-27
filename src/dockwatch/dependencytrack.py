from pathlib import Path

import httpx

from dockwatch.models import DockerImage


class DependencyTrackClient:
    """Minimal Dependency-Track REST API client."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-Api-Key": api_key}

    def find_project_uuid(self, image: DockerImage) -> str | None:
        params = {
            "name": image.project_name,
            "version": image.project_version,
        }
        response = httpx.get(
            f"{self.base_url}/api/v1/project/lookup",
            headers=self.headers,
            params=params,
            timeout=30,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        return data.get("uuid")

    def create_project(self, image: DockerImage) -> str:
        payload = {
            "name": image.project_name,
            "version": image.project_version,
            "classifier": "APPLICATION",
            "active": True,
        }
        response = httpx.put(
            f"{self.base_url}/api/v1/project",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["uuid"]

    def get_or_create_project_uuid(self, image: DockerImage) -> str:
        project_uuid = self.find_project_uuid(image)
        if project_uuid:
            return project_uuid
        return self.create_project(image)

    def upload_bom(self, project_uuid: str, bom_file: Path) -> None:
        with bom_file.open("rb") as file_handle:
            response = httpx.post(
                f"{self.base_url}/api/v1/bom",
                headers=self.headers,
                data={"project": project_uuid},
                files={"bom": (bom_file.name, file_handle, "application/json")},
                timeout=120,
            )
        response.raise_for_status()
