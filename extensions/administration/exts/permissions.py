__all__ = ("Permissions",)


import asyncio
from AlbertoX3.constants import Config
from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.permission import BasePermission, BasePermissionLevel
from AlbertoX3.settings import RoleSettings
from AlbertoX3.translations import TranslationNamespace, t
from AlbertoX3.utils import get_logger, get_permissions
from naff.client.const import Absent, MISSING
from naff.models.discord.embed import Embed
from naff.models.discord.message import Message
from naff.models.discord.role import Role
from naff.models.naff.application_commands import OptionTypes, SlashCommandOption, slash_command
from naff.models.naff.context import Context, InteractionContext
from naff.models.naff.protocols import Converter
from ..colors import Colors
from ..permission import AdministrationPermission


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.administration


class PermissionLevelConverter(Converter[BasePermissionLevel]):
    async def convert(self, ctx: Context, argument: str) -> Absent[BasePermissionLevel]:
        for level in Config.PERMISSION_LEVELS:  # type: ignore
            if argument.lower() in level.aliases or argument == str(level.level):
                return level
        return MISSING


class Permissions(Extension):
    @staticmethod
    async def p_list_permissions(ctx: InteractionContext, title: str, min_level: BasePermissionLevel) -> Message:
        out: dict[tuple[str, str], list[str]] = {}
        permissions: list[BasePermission] = get_permissions()
        levels = await asyncio.gather(*[permission.resolve() for permission in permissions])
        for permission, level in zip(permissions, levels):
            if min_level.level >= level.level:
                key = (level.level, level.description)
                out.setdefault(key, []).append(f"`{permission.fullname}` - {permission.description}")

        embed = Embed(title=title)
        if not out:
            embed.color = Colors.error
            embed.description = t.p.no_permissions
        else:
            embed.color = Colors.permissions
            for (_, name), lines in sorted(out.items(), reverse=True):
                embed.add_field(name=name, value="\n".join(sorted(lines)))

        return await ctx.send(embeds=[embed])

    @slash_command(
        "permissions",
        sub_cmd_name="list",
        sub_cmd_description="List all permissions",
        options=[
            SlashCommandOption(
                name="min_level",
                type=OptionTypes.STRING,
                required=False,
            ),
        ],
    )
    @AdministrationPermission.p_view_all.check
    async def p_permissions(self, ctx: InteractionContext, min_level: PermissionLevelConverter = MISSING):
        if min_level is MISSING:
            min_level = Config.PERMISSION_DEFAULT_LEVEL

        await self.p_list_permissions(ctx=ctx, title=t.p.title.permissions, min_level=min_level)

    @p_permissions.subcommand(
        sub_cmd_name="own",
        sub_cmd_description="List own permissions",
    )
    @AdministrationPermission.p_view_own.check
    async def p_own(self, ctx: InteractionContext):
        min_level = await Config.PERMISSION_LEVELS.get_permission_level(ctx.author)
        await self.p_list_permissions(ctx=ctx, title=t.p.title.own, min_level=min_level)

    @p_permissions.subcommand(
        sub_cmd_name="levels",
        sub_cmd_description="List all permission levels",
    )
    @AdministrationPermission.p_view_all.check
    async def permissions_permission_levels(self, ctx: InteractionContext):
        embed = Embed(title=t.p.title.levels, color=Colors.permissions)

        for level in reversed(Config.PERMISSION_LEVELS):  # type: ignore
            description = t.p.aliases(aliases=", ".join(f"`{a}`" for a in level.aliases))
            description += "\n" + t.p.level(level=level.level)

            granted_by: list[str] = [f"`{gp}`" for gp in level.guild_permissions]
            for role_name in level.roles:
                role: Role | None = await ctx.guild.fetch_role(await RoleSettings.get(role_name))
                if role is not None:
                    granted_by.append(role.mention)

            if not level.level:
                granted_by = ["@everyone"]

            if granted_by:
                description += f"\n{t.p.granted_by.title}\n" + "\n".join(
                    t.p.granted_by.bullet_point(by=by) for by in granted_by
                )

            embed.add_field(name=level.description, value=description)

        await ctx.send(embeds=[embed])

    @p_permissions.subcommand(
        sub_cmd_name="set",
        sub_cmd_description="Manage permissions",
        options=[
            SlashCommandOption(
                name="permission_name",
                description="The name of the permission",
                type=OptionTypes.STRING,
            ),
            SlashCommandOption(
                name="level",
                description="The new level for the permission",
                type=OptionTypes.STRING,
            ),
        ],
    )
    @AdministrationPermission.p_manage.check
    async def p_set(self, ctx: InteractionContext, permission_name: str, level: PermissionLevelConverter = MISSING):
        level: BasePermissionLevel
        if level is MISSING:
            await ctx.send(t.p.invalid.level(level=ctx.kwargs["level"]))
            return
        for permission in get_permissions():
            if permission.fullname.lower() == permission_name.lower():
                break
        else:
            await ctx.send(t.p.invalid.permission(permission=permission_name))
            return

        max_level = await Config.PERMISSION_LEVELS.get_permission_level(ctx.author)
        if max(level.level, (await permission.resolve()).level) > max_level.level:
            await ctx.send(t.p.to_high_to_manage)
            return

        await permission.set(level)

        embed = Embed(
            title=t.p.title.permissions,
            description=t.p.permission_set(permission=permission.fullname, level=level.description),
            color=Colors.permissions,
        )
        await ctx.send(embeds=[embed])
