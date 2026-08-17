"""Khul3awiyah command access policy."""

from typing import Literal

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("Khul3awiyah", __file__)

UNIQUE_ID = 0x4B484143

CommandSurface = Literal["general", "privileged"]

# Core Red cogs whose administrative/user-management commands are exposed
# through Khul3awiyah's privileged `!` interface.
PRIVATE_COGS = frozenset(
    {
        "Mod",
        "Mutes",
        "Warnings",
        "Admin",
        "Cleanup",
        "Filter",
        "Permissions",
        "ModLog",
    }
)

# Public-facing cogs use the public `-` interface.
PUBLIC_COGS = frozenset({"General", "Games", "Khul3awiyah Utilities"})

# These commands are the owner-only control plane for the privileged policy.
ACCESS_COMMANDS = frozenset({"صلاحية_منح", "صلاحية_سحب", "صلاحيات"})


def command_surface(prefix: str) -> CommandSurface | None:
    """Return Khul3awiyah's surface for a supported prefix.

    ``-`` is the general surface. ``!`` is the privileged surface.
    Other prefixes are intentionally outside the Foundation policy.
    """
    if prefix == "-":
        return "general"
    if prefix == "!":
        return "privileged"
    return None


def user_has_privileged_access(*, author_id: int, allowed_ids: set[int]) -> bool:
    """Return whether a user has explicit Khul3awiyah privileged access.

    Server ownership is deliberately not an implicit bypass. The owner grants
    access explicitly through the Khul3awiyah control-plane commands.
    """
    return author_id in allowed_ids


@cog_i18n(_)
class Khul3awiyahAccess(commands.Cog):
    """Enforce Khul3awiyah's `!`/`-` command boundary and private access list."""

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(self, identifier=UNIQUE_ID, force_registration=True)
        self.config.register_guild(private_users=[])

    async def cog_load(self) -> None:
        self.bot.add_check(self._prefix_and_access_check, call_once=False)

    async def cog_unload(self) -> None:
        self.bot.remove_check(self._prefix_and_access_check, call_once=False)

    async def _prefix_and_access_check(self, ctx: commands.Context) -> bool:
        """Apply the project-wide prefix and privileged-access policy."""
        command = ctx.command
        if command is None:
            return True

        command_name = str(getattr(command, "qualified_name", ""))
        cog_name = str(getattr(command, "cog_name", ""))
        surface = command_surface(ctx.prefix)

        # Permission-management commands form the owner-only control plane.
        # They must remain on the privileged prefix and never grant themselves
        # access through the normal privileged-user list.
        if command_name in ACCESS_COMMANDS:
            if ctx.guild is None or surface != "privileged":
                return False
            if ctx.guild.owner_id != ctx.author.id:
                raise commands.CheckFailure(
                    _("Only the server owner can manage Khul3awiyah command access.")
                )
            return True

        # Unsupported prefixes are outside Khul3awiyah's command surface.
        if surface is None:
            return False

        if surface == "general":
            # Only explicitly public cogs may use the general `-` surface.
            return cog_name in PUBLIC_COGS

        # `!` is always the privileged surface. Discord Administrator and
        # server ownership are not automatic bypasses.
        if ctx.guild is None:
            raise commands.CheckFailure(
                _("Khul3awiyah privileged commands are only available in servers.")
            )

        allowed = set(await self.config.guild(ctx.guild).private_users())
        if not user_has_privileged_access(
            author_id=ctx.author.id,
            allowed_ids=allowed,
        ):
            raise commands.CheckFailure(
                _("You do not have Khul3awiyah permission to use this command.")
            )
        return True

    @commands.command(name="صلاحية_منح")
    @commands.guild_only()
    async def grant_private_access(self, ctx: commands.Context, member: discord.Member) -> None:
        """Grant a member access to Khul3awiyah's private `!` commands."""
        if ctx.guild.owner_id != ctx.author.id:
            raise commands.CheckFailure(_("Only the server owner can manage Khul3awiyah command access."))
        async with self.config.guild(ctx.guild).private_users() as users:
            if member.id not in users:
                users.append(member.id)
        await ctx.send(_("Granted Khul3awiyah private-command access to {member}.").format(member=member.mention))

    @commands.command(name="صلاحية_سحب")
    @commands.guild_only()
    async def revoke_private_access(self, ctx: commands.Context, member: discord.Member) -> None:
        """Revoke a member's access to Khul3awiyah's private `!` commands."""
        if ctx.guild.owner_id != ctx.author.id:
            raise commands.CheckFailure(_("Only the server owner can manage Khul3awiyah command access."))
        async with self.config.guild(ctx.guild).private_users() as users:
            try:
                users.remove(member.id)
            except ValueError:
                pass
        await ctx.send(_("Revoked Khul3awiyah private-command access from {member}.").format(member=member.mention))

    @commands.command(name="صلاحيات")
    @commands.guild_only()
    async def list_private_access(self, ctx: commands.Context) -> None:
        """List members explicitly allowed to use private Khul3awiyah commands."""
        if ctx.guild.owner_id != ctx.author.id:
            raise commands.CheckFailure(_("Only the server owner can manage Khul3awiyah command access."))
        user_ids = await self.config.guild(ctx.guild).private_users()
        members = [ctx.guild.get_member(user_id) for user_id in user_ids]
        members = [member for member in members if member is not None]
        if not members:
            await ctx.send(_("No members currently have explicit private-command access."))
            return
        await ctx.send(
            _("Members with private-command access:\n{members}").format(
                members="\n".join(f"- {member.mention}" for member in members)
            )
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """Remove deleted users from every guild access list."""
        if requester != "discord_deleted_user":
            return
        for guild_id in await self.config.all_guilds():
            guild = self.config.guild_from_id(guild_id)
            async with guild.private_users() as users:
                if user_id in users:
                    users.remove(user_id)
