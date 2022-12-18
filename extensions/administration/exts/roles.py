__all__ = ("Roles",)


from AlbertoX3 import RoleSettings, get_logger, Extension, t, TranslationNamespace, Config
from naff import (
    Permissions,
    Role,
    Embed,
    InteractionContext,
    SlashCommandOption,
    OptionTypes,
    slash_command,
)
from ..colors import Colors
from ..permission import AdministrationPermission


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.administration


class Roles(Extension):
    @slash_command(
        "roles",
        sub_cmd_name="config",
        sub_cmd_description="Configure roles",
        options=[
            SlashCommandOption(
                name="config",
                description="The configuration to set",
                type=OptionTypes.STRING,
            ),
            SlashCommandOption(
                name="new_role",
                description="The new role for the configuration",
                type=OptionTypes.ROLE,
            ),
        ],
    )
    @AdministrationPermission.r_config_write.check
    async def r_config(self, ctx: InteractionContext, config: str, new_role: Role):
        for name, (title,) in Config.ROLES.items():
            if name == config or title.lower() == config.lower():
                break
        else:
            await ctx.send(t.r.invalid.config(config=config))
            return

        await RoleSettings.set(name=name, role_id=new_role.id)
        await ctx.send(t.r.config_set(config=name, role=new_role.mention))

    @r_config.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List roles",
    )
    @AdministrationPermission.r_config_read.check
    async def r_list(self, ctx: InteractionContext):
        embed = Embed(title=t.r.title, color=Colors.roles)
        for name, (title,) in Config.ROLES.items():
            role = await ctx.guild.fetch_role(await RoleSettings.get(name))
            val = role.mention if role is not None else t.r.missing.role
            embed.add_field(name=title, value=val, inline=True)
        await ctx.send(embeds=[embed])

    @r_config.subcommand(
        sub_cmd_name="clone",
        sub_cmd_description="Clones a existing role",
        options=[
            SlashCommandOption(
                name="role",
                description="The role to clone",
                type=OptionTypes.ROLE,
            ),
        ],
    )
    @AdministrationPermission.r_roles_clone.check
    async def r_clone(self, ctx: InteractionContext, role: Role):
        cloneable_permissions: int = role.permissions.value & ctx.guild.me.guild_permissions.value
        missing_permissions: str = "\n".join(
            t.r.missing.permission.value(permission=permission.name)
            for permission in Permissions(role.permissions.value & ~ctx.guild.me.guild_permissions.value)
            if permission.name != "NONE"
        )

        role = await ctx.guild.create_role(
            name=role.name,
            permissions=Permissions(cloneable_permissions),  # type: ignore
            color=role.color,
            hoist=role.hoist,
            mentionable=role.mentionable,
            icon=role.icon,
        )

        description = t.r.created(role=role.mention)
        if missing := missing_permissions:
            description += f"\n\n{t.r.missing.permission.title(cnt=len(missing.splitlines()))}\n{missing}"

        embed = Embed(title=t.r.title, description=description, color=Colors.roles)
        await ctx.send(embeds=[embed])
