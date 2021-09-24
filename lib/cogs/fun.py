from discord.ext.commands import Cog
from discord.ext.commands import command, cooldown, BucketType
from discord.errors import HTTPException
from aiohttp import request
from typing import Optional

class Fun(Cog):

    def __init__(self, shydroid):

        self.shydroid = shydroid

    @command(name="hi", aliases=["yo"], hidden=False)
    @cooldown(1, 20, BucketType.user)
    async def hi(self, ctx, number: Optional[int]=1):
        
        await ctx.send(f"Hi {ctx.author.mention} !\n" * int(number))

    # @hi.error
    # async def error_hi(self, ctx, exc):

    #     if isinstance(exc.original, HTTPException):

    #         await ctx.send("Message was over 2000 characters !")

    @command(name="fact")
    @cooldown(3, 60, BucketType.guild)
    async def panda_fact(self, ctx):

        url = "https://some-random-api.ml/facts/panda"

        async with request("GET", url) as response:

            if response.status == 200:

                data = await response.json()

                await ctx.send(data["fact"])

            else:

                await ctx.send("Unable to reach the site !")

"""

Fun commands ideas :

    - 8ball
    - Tails or Heads
    - Casino
    - Memes / Images / Reddit
    - Minigames
    - Web Browsing (ytb...)

"""

def setup(shydroid):

    shydroid.add_cog(Fun(shydroid))