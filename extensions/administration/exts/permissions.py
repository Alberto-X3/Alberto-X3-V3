__all__ = ("Permissions",)


import asyncio
from AlbertoX3 import (
    RoleSettings,
    get_logger,
    get_permissions,
    Extension,
    t,
    TranslationNamespace,
    Config,
    BasePermissionLevel,
    BasePermission,
)
from naff import (
    Absent,
    MISSING,
    InteractionContext,
    Role,
    slash_command,
    SlashCommandOption,
    OptionTypes,
    Converter,
    Context,
    Embed,
    Message,
)
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
            SlashCommandOption(name="min_level", type=OptionTypes.STRING, min_length=1, required=False),
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

    # manage
