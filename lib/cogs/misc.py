from discord.ext.commands import Cog, command, has_permissions, CheckFailure
from ..db import db

class Misc(Cog):

    def __init__(self, shydroid):

        self.shydroid = shydroid

    @command(name="prefix")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):

        if len(new) > 5:
            
            await ctx.send("Prefixes can't be longer than 5 characters !")

        else:

            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix set to {new} !")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):

        if isinstance(exc, CheckFailure):

            await ctx.send("You need the Manage Server permission for it to work !")

def setup(shydroid):

    shydroid.add_cog(Misc(shydroid))