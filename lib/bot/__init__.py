from discord import Embed, File, Intents, DMChannel
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import Context, when_mentioned_or, command, has_permissions
from discord.errors import HTTPException, Forbidden
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from ..db import db
from glob import glob
from asyncio import sleep

OWNER = [519486695029211154]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

def get_prefix(shydroid, message):

    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(shydroid, message)

class Bot(BotBase):

    def __init__(self):

        self.scheduler = AsyncIOScheduler()
        self.ready = False

        db.autosave(self.scheduler)

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER, intents=Intents.all())

    def setup(self):

        for cog in COGS:

            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded !")

        print("setup complete")

    def run(self):

        print("Running setup...")
        self.setup()
        
        with open("./lib/bot/token.0", "r", encoding="utf-8") as token_file:

            self.TOKEN = token_file.read()
        
        print("Running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):

        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None:

            if self.ready:

                await self.invoke(ctx)

            else:

                await ctx.send("I'm not ready to receive commands, please wait a few seconds.")

    async def on_connect(self):

        print("Bot connected !")

    async def on_disconnect(self):

        print("Bot disconnected !")

    async def on_error(self, err, *args, **kwargs):

        if err == "on_command_error":

            await args[0].send("A command error has been detected !")

        raise

    async def on_command_error(self, ctx, exc):
        
        if isinstance(exc, CommandNotFound):

            await ctx.send("The command you tried to use doesn't exist !")
        
        elif isinstance(exc, BadArgument):

            await ctx.send("You passed a wrong argument in the function !")

        elif isinstance(exc, MissingRequiredArgument):

            await ctx.send("An argument is missing !")

        elif isinstance(exc, CommandOnCooldown):

            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown, please wait {exc.retry_after:,.2f} seconds before retrying it.")

        elif hasattr(exc, "original"):

            if isinstance(exc.original, HTTPException):

                await ctx.send("Unable to send a message longer than 2000 characters !")

            elif isinstance(exc.original, Forbidden):

                await ctx.send("I don't have permission to do that.")

            else:

                raise exc.original

        else:

            raise exc

    async def on_ready(self):
        
        if not self.ready:
            
            self.scheduler.start()
            self.guild = self.get_guild(284374806546350091)

            channel = self.get_channel(832914794611736617)
            # await channel.send("Shydroid is online :3")

            # embed = Embed(title="Now online", description="Shydroid is now online.", colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True), ("Another field", "next to the other one", True), ("Third", "inline=False", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_footer(text="footer")
            # embed.set_author(name="ShinTwiz", icon_url=self.guild.icon_url)
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            # await channel.send(embed=embed)

            # await channel.send(file=File("./data/images/KG.jpg"))
            self.ready = True
            print("Bot is ready !")

        else:

            print("Bot reconnected !")

    async def on_message(self, message):

        if not message.author.bot:

            if isinstance(message.channel, DMChannel):

                await message.author.send(message.content)

            else:
                
                await self.process_commands(message)

shydroid = Bot()