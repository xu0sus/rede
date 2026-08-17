from redbot.core.bot import Red

from .access import Khul3awiyahAccess
from .utilities import Khul3awiyahUtilities


async def setup(bot: Red) -> None:
    await bot.add_cog(Khul3awiyahAccess(bot))
    await bot.add_cog(Khul3awiyahUtilities(bot))
