import discord
import asyncio
from discord.ext import commands

_BLUE = 0x0060a9

class EmbedHelp(commands.HelpFormatter):
	def shorten(self,text):
		return text #dirty hack, but...
	async def format(self):
		"""Handles the actual behaviour involved with formatting.
		To change the behaviour, this method should be overridden.
		Returns
		--------
		list
		A paginated output of the help command.
		"""
		self._paginator = commands.Paginator(prefix = '', suffix = '')

		# we need a padding of ~80 or so

		description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

		if description:
			# <description> portion
			self._paginator.add_line(description, empty=True)

		if isinstance(self.command, commands.Command):
			# <signature portion>
			signature = self.get_command_signature()
			self._paginator.add_line(signature, empty=True)

			# <long doc> section
			if self.command.help:
				self._paginator.add_line(self.command.help, empty=True)

			# end it here if it's just a regular command
			if not self.has_subcommands():
				self._paginator.close_page()
				return self._paginator.pages

		max_width = self.max_name_size

		def category(tup):
			cog = tup[1].cog_name
			# we insert the zero width space there to give it approximate
			# last place sorting position.
			return '**' + cog + ':' + '**' if cog is not None else '\u200b**No Category:**'

		filtered = await self.filter_command_list()
		if self.is_bot():
			data = sorted(filtered, key=category)
			for category, cmds in itertools.groupby(data, key=category):
				# there simply is no prettier way of doing this.
				cmds = sorted(cmds)
				if len(cmds) > 0:
					self._paginator.add_line(category)

				self._add_subcommands_to_page(max_width, cmds)
		else:
			filtered = sorted(filtered)
			if filtered:
				self._paginator.add_line('Commands:')
				self._add_subcommands_to_page(max_width, filtered)

		# add the ending note
		self._paginator.add_line()
		ending_note = self.get_ending_note()
		self._paginator.add_line(ending_note)
		return self._paginator.pages

bot = commands.Bot(command_prefix='.', )
bot.formatter = EmbedHelp()
bot.remove_command("help")
@bot.event
async def on_ready(self):
    print('Logged on as {0.name} ({0.id})'.format(bot.user))

@bot.event
async def on_message(message):
	await bot.process_commands(message)

startup_extensions = [
    # 'logging',
    # 'moderation',
    'verify'
]

if __name__ == '__main__':
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
			print(f'Loaded extension {extension}.')
		except Exception as e:
			print(f'Failed to load extension {extension}.')
			print(e)

@bot.command(name='load', hidden=True)
@commands.has_permissions(administrator=True)
async def cog_load(ctx, *, cog: str):
	"""loads a module."""
	bot.load_extension(cog)
	await ctx.send(f'Loaded the `{cog}` cog')
	print(f'Loaded extenstion {cog}')

@bot.command(name='unload', hidden=True)
@commands.has_permissions(administrator=True)
async def cog_unload(ctx, *, cog: str):
	"""unloads a module."""
	bot.unload_extension(cog)
	await ctx.send(f'Unloaded the `{cog}` cog')
	print(f'Unloaded extension {cog}')

@bot.command(name='reload', hidden=True)
@commands.has_permissions(administrator=True)
async def cog_reload(ctx, *, cog: str):
	"""reloads a module."""
	bot.unload_extension(cog)
	bot.load_extension(cog)
	await ctx.send(f'Reloaded the `{cog}` cog')
	print(f'Reloaded extension {cog}')
    
@bot.command(name='help')
async def help(ctx, *cmds : str):
	"""shows this message."""
	bot = ctx.bot
	destination = ctx.message.author if bot.pm_help else ctx.message.channel

	def repl(obj):
		return _mentions_transforms.get(obj.group(0), '')

	# help by itself just lists our own commands.
	if len(cmds) == 0:
		pages = await bot.formatter.format_help_for(ctx, bot)
	elif len(cmds) == 1:
		# try to see if it is a cog name
		name = _mention_pattern.sub(repl, cmds[0])
		command = None
		if name in bot.cogs:
			command = bot.cogs[name]
		else:
			command = bot.all_commands.get(name)
			if command is None:
				await destination.send(bot.command_not_found.format(name))
				return

		pages = await bot.formatter.format_help_for(ctx, command)
	else:
		name = _mention_pattern.sub(repl, cmds[0])
		command = bot.all_commands.get(name)
		if command is None:
			await destination.send(bot.command_not_found.format(name))
			return

		for key in cmds[1:]:
			try:
				key = commands._mention_pattern.sub(repl, key)
				command = command.all_commands.get(key)
				if command is None:
					await destination.send(bot.command_not_found.format(key))
					return
			except AttributeError:
				await destination.send(bot.command_has_no_subcommands.format(command, key))
				return

		pages = await bot.formatter.format_help_for(ctx, command)

	if bot.pm_help is None:
		characters = sum(map(lambda l: len(l), pages))
		# modify destination based on length of pages.
		if characters > 1000:
			destination = ctx.message.author

	for page in pages:
		em = discord.Embed(title = (", ".join(cmds) if len(cmds) != 0 else "Help"), description = page, colour=_BLUE)
		em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
		await destination.send(embed = em)

bot.run(open('keys/token.txt','r').read())