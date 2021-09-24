from discord.ext.commands import Cog, command, has_permissions, bot_has_permissions, Greedy, CheckFailure
from discord import Embed, Member
from discord.utils import get
from ..db import db
from datetime import datetime, timedelta
from typing import Optional
from asyncio import sleep
import random
from better_profanity import profanity
from re import search

profanity.load_censor_words_from_file("./data/profanity.txt")

class Mod(Cog):

    def __init__(self, shydroid):

        self.shydroid = shydroid
        self.watchlist = []

    def save_watchlist(self):

        for elem in self.watchlist:

            db.execute("INSERT INTO reactions VALUES (?, ?, ?)", elem['message_id'], elem['emoji_id'], elem['role_name'])

    @Cog.listener()
    async def on_ready(self):

        self.output = self.shydroid.get_channel(832914794611736617)
        self.mute_role = get(self.shydroid.get_guild(284374806546350091).roles, name="Muted")

    @Cog.listener()
    async def on_member_join(self, member):

        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
        self.welcome_channel = self.shydroid.get_channel(832914794611736617)
        await self.welcome_channel.send(f"Welcome to **{member.guild.name}** {member.mention} !")
        try:
            await member.send("Yo")

        except Forbidden:
            pass

        await member.add_roles(member.guild.get_role(832688048008462366)) # or member.edit(roles=list_of_roles)

    @Cog.listener()
    async def on_member_remove(self, member):

        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
        self.welcome_channel = self.shydroid.get_channel(832914794611736617)
        await self.welcome_channel.send(f"Sayonara {member.display_name} !")

    @Cog.listener()
    async def on_user_update(self, before, after):

        if before.avatar_url != after.avatar_url:

            embed = Embed(title="Avatar change", description=f"{after.display_name} changed its profile picture !", timestamp=datetime.utcnow())
            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)
            await self.output.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):

        if before.display_name != after.display_name:

            await self.output.send(f"{before.display_name} changed to {after.display_name} !")

    @Cog.listener()
    async def on_message_edit(self, before, after):

        if not after.author.bot:

            if before.content != after.content:

                await self.output.send("Message edited")

    @Cog.listener()
    async def on_message_delete(self, message):

        ...

    @command(name="userInfo", aliases=["info"])
    async def user_info(self, ctx, member: Optional[Member]):

        member = member or ctx.author

        embed = Embed(title=f"Info about {member.display_name}" + " [BOT]" if member.bot else "",
                      colour=member.colour,
                      timestamp=datetime.utcnow())
        
        fields = [("Name", member.name, False),
                  ("Top role", member.top_role.mention, False),
                  ("Status", str(member.status), False),
                  ("Account created on", member.created_at.strftime("%d/%m/%Y"), False),
                  ("Joined the server on", member.joined_at.strftime("%d/%m/%Y"), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @command(name="serverInfo", aliases=["guildInfo"])
    async def server_info(self, ctx):

        embed = Embed(title=f"{ctx.guild.name} server information",
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())
        
        fields = [("Name", ctx.guild.name, False),
                  ("Owner", ctx.guild.owner.mention, False),
                  ("Server created on", ctx.guild.created_at.strftime("%d/%m/%Y"), False),
                  ("Members (including Bots)", f"{len(ctx.guild.members)} ({len(list(filter(lambda m: m.bot, ctx.guild.members)))})", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=embed)

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick(self, ctx, targets: Greedy[Member], *, reason: Optional[str]="Because I want."):
        """Allows the moderators to kick annoying people"""

        if not targets:

            await ctx.send("You need to specify one or more members to kick !")

        else:

            for target in targets:

                if ctx.author.top_role.position > target.top_role.position:

                    await target.kick(reason=reason)
                    await ctx.send(f"{ctx.author.name} just kicked {target.name} ! /:kissing_heart:")

                else:

                    await ctx.send(f"{ctx.author.name} can't kick {target.name} (Hierarchy issue).")

    @kick.error
    async def kick_error(self, ctx, exc):

        if isinstance(exc, CheckFailure):

            await ctx.send("You don't have permission to do that !")

    @command(name="clear", aliases=["clearMessages"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], number: Optional[int]=1):

        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < number < 20:

            with ctx.channel.typing():

                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=number, check=_check)
                await ctx.send(f"Deleted {len(deleted):,} messages !", delete_after=5)
        
        else:

            await ctx.send("Please enter a number between 0 and 20.")

    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute(self, ctx, member: Member, length: Optional[int], *, reason: Optional[str]="Please shut up :D"):

        print("Mute func")

        if not self.mute_role in member.roles:

            print("Muted not in roles")

            if ctx.guild.me.top_role.position > member.top_role.position:

                print("Position check")

                role_ids = ""
                for role in member.roles:
                    role_ids += str(role.id) + ","
                role_ids = role_ids[:-1]
                print(role_ids)
                end_time = datetime.utcnow() + timedelta(seconds=length) if length else None
                print(end_time)

                db.execute("INSERT INTO mutes VALUES (?, ?, ?)", member.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

                print(role_ids)
                print(member.roles)
                print(self.mute_role, self.mute_role.id)
                await member.edit(roles=[self.mute_role])
                print(member.roles)

                await ctx.send(f"User {member.name} has been muted by {ctx.author.name} for the next {length} seconds !")

            else:

                await ctx.send(f"{member.name} couldn't be muted.")

        else:

            await ctx.send(f"{member.name} is already muted...")

        print(length, not length)
        await sleep(length if length else 10)
        await self.unmute(self.output, member)

    @mute.error
    async def mute_error(self, ctx, exc):

        if isinstance(exc, CheckFailure):

            await ctx.send("You don't have permission to do that !")

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute(self, ctx, member: Member):

        if self.mute_role in member.roles:

            role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", member.id)
            print(role_ids)
            roles = [ctx.guild.get_role(int(id)) for id in role_ids.split(",") if len(id)]

            db.execute("DELETE FROM mutes WHERE UserID = ?", member.id)

            await member.edit(roles=roles)

            await ctx.send(f"{member.name} has been unmuted.")

    @command(name="addMessage")
    async def add_reaction_role(self, ctx, message_id, emoji_id, *, role_name):

        self.watchlist.append({"message_id": int(message_id), "emoji_id": int(emoji_id), "role_name": role_name})
        await ctx.send(f"Done !")
        await ctx.send(self.watchlist)
        self.save_watchlist(ctx)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):

        print("REACTION !")

        print(payload.channel_id, payload.emoji, payload.event_type, payload.guild_id, payload.member, payload.message_id, payload.user_id, "\n\n")
        
        member = payload.member
        guild = self.shydroid.get_guild(payload.guild_id)
        channel = self.shydroid.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for data in self.watchlist:

            if payload.message_id == data["message_id"]:

                if payload.emoji.id == data["emoji_id"]:

                    print("EMOJI FOUND", payload.emoji)

                    role = get(guild.roles, name=data["role_name"])

                    print("ROLE FOUND", role)

                    if role in payload.member.roles:

                        await channel.send(f"{member.name} already has the role {role} !")

                    else:

                        await member.add_roles(role)

                        print("ROLE ADDED")

                        await self.output.send(f"{member.name} just got the role {role} !")

                    await message.remove_reaction(payload.emoji, member)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        ...

    @Cog.listener()
    async def on_message(self, message):

        if not message.author.bot:
            if profanity.contains_profanity(message.content):
                await message.channel.send("You used a very bad word !!!")

    @command(name="censor")
    @has_permissions(manage_guild=True)
    async def add_censor_word(self, ctx, *, words):

        with open("./data/profanity.txt", a) as f:
            f.write("".join([f"{word}\n" for word in words]))

        await ctx.send("Action completed.")

def setup(shydroid):

    shydroid.add_cog(Mod(shydroid))