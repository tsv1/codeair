from enum import IntEnum, StrEnum

__all__ = ["GitLabAccessLevel", "ProjectVisibility"]


class GitLabAccessLevel(IntEnum):
    GUEST = 10
    REPORTER = 20
    DEVELOPER = 30
    MAINTAINER = 40
    OWNER = 50


class ProjectVisibility(StrEnum):
    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC = "public"
