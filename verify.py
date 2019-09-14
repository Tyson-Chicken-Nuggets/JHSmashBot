import asyncio
import json
import discord
from discord.ext import commands
from canvasapi import Canvas

_VERIFY = 0 #placeholder id
_VERIFIED = 0 #placeholder id

API_URL = open('keys/url.txt', 'r').read()
API_KEY = open('keys/key.txt','r').read()

canvas = Canvas(API_URL, API_KEY)

course = canvas.get_course(4201)
users = course.get_users(enrollment_type=['student'])

class Verify:
	def __init__(self, bot):
		self.bot = bot

    def in_verify(ctx):
        return ctx.channel == _VERIFY

    @commands.command()
    @commands.check(in_verify)
    async def verify(self, ctx, canvas_id):
        club_member = canvas.get_user(canvas_id, 'login_id')
        if club_member in users:
            profile = club_member.get_profile
            await self.bot.change_nickname(ctx.message.author, profile['name'])
            await ctx.message.author.add_roles(ctx.guild.get_role(_VERIFIED))
            await ctx.message.author.send('You are now verified as {0}'.format(profile['name']))
        else:
            await ctx.channel.send(
                """
                Please make sure you send the proper login id.
                
                Format:
                `email@jesuittampa.org`
                """)
            

def setup(bot):
	bot.add_cog(Verify(bot))