from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

@dataclass(frozen=True, slots=True)
class RouteConfig:
    frontend_dir: Path
    reserved_names: set[str]


@lru_cache(maxsize=1)
def get_app_config() -> RouteConfig:
    return RouteConfig(
        frontend_dir=Path(__file__).parents[1] / "frontend" / "dist",
        reserved_names={"baskets", "assets"}
    )