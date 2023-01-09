__all__ = ("Maintenance",)


from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.settings import RoleSettings
from AlbertoX3.translations import TranslationNamespace, t
from AlbertoX3.utils import get_logger, role_is_manageable
from naff.models.discord.guild import Guild
from naff.models.discord.user import Member
from naff.models.naff.application_commands import slash_command
from naff.models.naff.context import InteractionContext
from .db import MaintenanceRolesModel, MaintenanceUsersModel
from .permission import MaintenancePermission


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.maintenance


class Maintenance(Extension):
    @slash_command(
        name="maintenance",
        sub_cmd_name="enter",
        sub_cmd_description="Enter maintenance",
    )
    @MaintenancePermission.manage.check
    async def maintenance(self, ctx: InteractionContext):
        # ToDo: check whether or not a maintenance is already happening
        # collect roles
        msg = await ctx.send(t.enter.checklist.collecting_roles)
        guild: Guild = ctx.guild
        users: dict[Member, int] = {member: 0 for member in guild.members}
        for i, role in enumerate(guild.roles):
            await MaintenanceRolesModel.add(id=i, role=role.id)
            for member in role.members:
                users[member] += 1 << i

        # remove roles
        await msg.edit(content=t.enter.checklist.removing_roles)
        maintenance_role = await RoleSettings.get("maintenance")
        for user, roles in users.items():
            await MaintenanceUsersModel.add(user=user.id, roles=roles, guild=guild.id)

            new_roles = {r.id for r in user.roles if not role_is_manageable(r)}
            new_roles.add(maintenance_role)
            await user.edit(roles=new_roles, reason="Maintenance starts!")

        # done
        await msg.edit(content=t.enter.checklist.done)

    @maintenance.subcommand(
        sub_cmd_name="exit",
        sub_cmd_description="Exit maintenance",
    )
    @MaintenancePermission.manage.check
    async def exit(self, ctx: InteractionContext):  # noqa A003
        # ToDo: check whether or not a maintenance is happening
        # grant roles
        msg = await ctx.send(t.exit.checklist.granting_roles)
        maintenance_role = await RoleSettings.get("maintenance")
        for member in ctx.guild.members:
            if (m_member := await MaintenanceUsersModel.get(member.id)) is None:
                continue

            new_roles = {
                r.id for r in await m_member.get_discord_roles(self.bot) if role_is_manageable(r) or r in member.roles
            }
            new_roles.discard(maintenance_role)
            await member.edit(roles=new_roles, reason="Maintenance is over!")

        # clear database
        await msg.edit(content=t.exit.checklist.clearing_database)
        await MaintenanceRolesModel.clear()
        await MaintenanceUsersModel.clear()

        # done
        await msg.edit(content=t.exit.checklist.done)
