from redbot.cogs.khul3awiyah.access import command_surface, user_has_privileged_access


def test_command_surface_general_prefix() -> None:
    assert command_surface("-") == "general"


def test_command_surface_privileged_prefix() -> None:
    assert command_surface("!") == "privileged"


def test_command_surface_rejects_unsupported_prefix() -> None:
    assert command_surface("$") is None


def test_owner_does_not_get_implicit_privileged_access() -> None:
    assert not user_has_privileged_access(author_id=10, allowed_ids=set())


def test_explicit_privileged_access_is_allowed() -> None:
    assert user_has_privileged_access(author_id=10, allowed_ids={10})


def test_privileged_access_is_user_scoped() -> None:
    assert not user_has_privileged_access(author_id=11, allowed_ids={10})
