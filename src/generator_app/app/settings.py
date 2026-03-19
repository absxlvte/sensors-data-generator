from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppSettings:
    app_name: str = "Generator New Generation"
    organization_name: str = "Local"
    default_export_dir: Path = Path.cwd()
