"""Games cog."""
from typing import Literal

from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n

from .logic import Choice, Result, parse_choice, play_rps, random_opponent

__all__ = ("Games", "UNIQUE_ID")

UNIQUE_ID = 0x4B48474D
TEST_GUILD_ID = 1536836645125496864
_ = Translator("Games", __file__)


@cog_i18n(_)
class Games(commands.Cog):
    """Play games and keep game statistics."""

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=UNIQUE_ID, force_registration=True)
        self.config.register_member(games=0, wins=0, losses=0, draws=0)

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """Delete stored game statistics when Discord deletes a user."""
        if requester != "discord_deleted_user":
            return
        await self.config.user_from_id(user_id).clear()

    @commands.group(name="لعبة", invoke_without_command=True)
    @commands.guild_only()
    async def game(self, ctx: commands.Context) -> None:
        """Play a game or view available games."""
        if ctx.guild is None or ctx.guild.id != TEST_GUILD_ID:
            return
        await ctx.send(_("الألعاب المتاحة: `حجر_ورقة_مقص` (حجر، ورقة، مقص)."))

    @game.command(name="حجر_ورقة_مقص")
    async def game_rps(self, ctx: commands.Context, choice: str) -> None:
        """Play a round of rock-paper-scissors against the bot."""
        if ctx.guild is None or ctx.guild.id != TEST_GUILD_ID:
            return
        player = parse_choice(choice)
        if player is None:
            await ctx.send(_("اختر `حجر` أو `ورقة` أو `مقص`."))
            return

        opponent = random_opponent()
        result = play_rps(player, opponent)
        stats = self.config.member(ctx.author)
        await stats.games.set(await stats.games() + 1)

        if result is Result.WIN:
            await stats.wins.set(await stats.wins() + 1)
            outcome = _("فزت! 🎉")
        elif result is Result.LOSS:
            await stats.losses.set(await stats.losses() + 1)
            outcome = _("خسرت هذه الجولة.")
        else:
            await stats.draws.set(await stats.draws() + 1)
            outcome = _("تعادلنا.")

        labels = {
            Choice.ROCK: _("حجر"),
            Choice.PAPER: _("ورقة"),
            Choice.SCISSORS: _("مقص"),
        }
        await ctx.send(
            _("اخترت **{player}** واخترتُ لك **{opponent}**.\n{outcome}").format(
                player=labels[player], opponent=labels[opponent], outcome=outcome
            )
        )

    @game.command(name="إحصائيات")
    async def game_stats(self, ctx: commands.Context) -> None:
        """Show your game statistics."""
        if ctx.guild is None or ctx.guild.id != TEST_GUILD_ID:
            return
        stats = await self.config.member(ctx.author).all()
        await ctx.send(
            _(
                "الألعاب: **{games}**\n"
                "الفوز: **{wins}**\n"
                "الخسارة: **{losses}**\n"
                "التعادل: **{draws}**"
            ).format(**stats)
        )
