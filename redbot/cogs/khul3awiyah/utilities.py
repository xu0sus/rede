"""Core user-facing utility commands for Khul3awiyah.

This cog intentionally contains only deterministic, local features.  It uses
Red's command framework and translation system rather than introducing a
parallel command/router layer.
"""

from __future__ import annotations

import ast
import math
import datetime as dt
import operator
import random
from typing import Final

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import escape

_ = Translator("Khul3awiyahUtilities", __file__)


_MAX_EXPRESSION_LENGTH: Final[int] = 200
_MAX_RANDOM_RANGE: Final[int] = 10**12
_MAX_OPTIONS: Final[int] = 50
_MAX_POWER: Final[int] = 1000


class _SafeCalculator(ast.NodeVisitor):
    """Evaluate a deliberately small arithmetic expression safely."""

    _BINOPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _UNARYOPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def visit_Expression(self, node: ast.Expression) -> int | float:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> int | float:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("invalid constant")
        if not math_is_finite(node.value):
            raise ValueError("non-finite number")
        return node.value

    def visit_BinOp(self, node: ast.BinOp) -> int | float:
        operation = self._BINOPS.get(type(node.op))
        if operation is None:
            raise ValueError("unsupported operator")
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > _MAX_POWER:
                raise ValueError("power too large")
        result = operation(left, right)
        if not math_is_finite(result):
            raise ValueError("non-finite result")
        return result

    def visit_UnaryOp(self, node: ast.UnaryOp) -> int | float:
        operation = self._UNARYOPS.get(type(node.op))
        if operation is None:
            raise ValueError("unsupported operator")
        result = operation(self.visit(node.operand))
        if not math_is_finite(result):
            raise ValueError("non-finite result")
        return result

    def generic_visit(self, node: ast.AST) -> int | float:
        raise ValueError("unsupported expression")


def math_is_finite(value: int | float) -> bool:
    if isinstance(value, int):
        return abs(value) <= 10**100
    return math.isfinite(value)


def _calculate(expression: str) -> int | float:
    if not expression or len(expression) > _MAX_EXPRESSION_LENGTH:
        raise ValueError("invalid expression")
    tree = ast.parse(expression, mode="eval")
    return _SafeCalculator().visit(tree)


@cog_i18n(_)
class Khul3awiyahUtilities(commands.Cog):
    """First batch of local, general-purpose Khul3awiyah commands."""

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot = bot

    async def red_delete_data_for_user(self, **kwargs) -> None:
        """This cog stores no user data."""
        return

    @commands.command(name="نرد")
    async def dice(self, ctx: commands.Context, sides: int = 6) -> None:
        """ارمِ نردًا بعدد أوجه تحدده."""
        if not 2 <= sides <= 100:
            await ctx.send(_("عدد أوجه النرد يجب أن يكون بين 2 و100."))
            return
        await ctx.send(_("🎲 النتيجة: **{result}** من {sides}.").format(
            result=random.randint(1, sides), sides=sides
        ))

    @commands.command(name="عملة")
    async def coin(self, ctx: commands.Context) -> None:
        """اقلب عملة عشوائية."""
        result = random.choice((_("وجه"), _("كتابة")))
        await ctx.send(_("🪙 النتيجة: **{result}**.").format(result=result))

    @commands.command(name="اختيار")
    async def choose(self, ctx: commands.Context, *choices: str) -> None:
        """اختر عشوائيًا من خيارين إلى خمسين خيارًا."""
        choices = tuple(choice for choice in choices if choice.strip())
        if not 2 <= len(choices) <= _MAX_OPTIONS:
            await ctx.send(_("أرسل من خيارين إلى {maximum} خيارًا. استخدم علامات الاقتباس للخيار الذي يحتوي على مسافات.").format(
                maximum=_MAX_OPTIONS
            ))
            return
        selected = random.choice(choices)
        await ctx.send(_("🎯 الاختيار: **{choice}**.").format(
            choice=escape(selected, mass_mentions=True)
        ))

    @commands.command(name="قرعة")
    async def draw(self, ctx: commands.Context, *entries: str) -> None:
        """اسحب فائزًا عشوائيًا من قائمة المشاركين."""
        entries = tuple(entry for entry in entries if entry.strip())
        if not 2 <= len(entries) <= _MAX_OPTIONS:
            await ctx.send(_("أرسل من مشاركين اثنين إلى {maximum} مشاركًا.").format(
                maximum=_MAX_OPTIONS
            ))
            return
        winner = random.choice(entries)
        await ctx.send(_("🏆 الفائز: **{winner}**.").format(
            winner=escape(winner, mass_mentions=True)
        ))

    @commands.command(name="عشوائي")
    async def random_number(self, ctx: commands.Context, minimum: int = 1, maximum: int = 100) -> None:
        """ولّد رقمًا عشوائيًا ضمن نطاق محدد."""
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        if maximum - minimum > _MAX_RANDOM_RANGE:
            await ctx.send(_("النطاق كبير جدًا. الحد الأقصى هو {maximum}.").format(
                maximum=_MAX_RANDOM_RANGE
            ))
            return
        await ctx.send(_("🔢 الرقم العشوائي: **{result}**.").format(
            result=random.randint(minimum, maximum)
        ))

    @commands.command(name="حظوظ")
    async def luck(self, ctx: commands.Context) -> None:
        """اعرض نسبة حظ عشوائية لليوم."""
        score = random.randint(1, 100)
        if score >= 90:
            state = _("ممتازة جدًا")
        elif score >= 70:
            state = _("ممتازة")
        elif score >= 50:
            state = _("جيدة")
        elif score >= 30:
            state = _("متوسطة")
        else:
            state = _("منخفضة")
        await ctx.send(_("🍀 نسبة حظك اليوم: **{score}%** — {state}.").format(
            score=score, state=state
        ))

    @commands.command(name="قرار")
    async def decision(self, ctx: commands.Context, *choices: str) -> None:
        """اتخذ قرارًا عشوائيًا بين الخيارات التي تقدمها."""
        choices = tuple(choice for choice in choices if choice.strip())
        if not 2 <= len(choices) <= _MAX_OPTIONS:
            await ctx.send(_("أرسل من خيارين إلى {maximum} خيارات.").format(
                maximum=_MAX_OPTIONS
            ))
            return
        await ctx.send(_("🧭 القرار: **{choice}**.").format(
            choice=escape(random.choice(choices), mass_mentions=True)
        ))

    @commands.command(name="ترتيب")
    async def shuffle(self, ctx: commands.Context, *entries: str) -> None:
        """رتّب مجموعة من العناصر ترتيبًا عشوائيًا."""
        entries = [entry for entry in entries if entry.strip()]
        if not 2 <= len(entries) <= _MAX_OPTIONS:
            await ctx.send(_("أرسل من عنصرين إلى {maximum} عنصرًا.").format(
                maximum=_MAX_OPTIONS
            ))
            return
        random.shuffle(entries)
        lines = "\n".join(
            f"**{index}.** {escape(entry, mass_mentions=True)}"
            for index, entry in enumerate(entries, start=1)
        )
        await ctx.send(_("🎲 الترتيب العشوائي:\n{entries}").format(entries=lines))

    @commands.command(name="نسبة")
    async def percentage(self, ctx: commands.Context, percent: float, number: float) -> None:
        """احسب نسبة مئوية من رقم."""
        if not all(abs(value) <= 10**12 for value in (percent, number)):
            await ctx.send(_("القيم كبيرة جدًا لهذا الأمر."))
            return
        result = percent * number / 100
        await ctx.send(_("📊 {percent}% من {number} = **{result:g}**.").format(
            percent=percent, number=number, result=result
        ))

    @commands.command(name="احسب")
    async def calculate(self, ctx: commands.Context, *, expression: str) -> None:
        """احسب تعبيرًا رياضيًا بسيطًا دون تنفيذ كود."""
        try:
            result = _calculate(expression)
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            await ctx.send(_("التعبير غير صالح أو يحتوي على عملية غير مسموحة."))
            return
        await ctx.send(_("🧮 النتيجة: **{result}**.").format(result=result))

    @commands.command(name="وقت")
    async def current_time(self, ctx: commands.Context) -> None:
        """اعرض الوقت الحالي وفق المنطقة الزمنية لجهاز المستخدم."""
        timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
        await ctx.send(_("🕒 الوقت الحالي: <t:{timestamp}:F>\n<t:{timestamp}:R>").format(
            timestamp=timestamp
        ))

    @commands.command(name="تاريخ")
    async def current_date(self, ctx: commands.Context) -> None:
        """اعرض التاريخ الحالي وفق المنطقة الزمنية لجهاز المستخدم."""
        timestamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
        await ctx.send(_("📅 التاريخ الحالي: <t:{timestamp}:D>.").format(
            timestamp=timestamp
        ))
