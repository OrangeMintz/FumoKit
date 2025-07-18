import discord
from discord.ext import commands
from discord.ui import Button, View

class AllBotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # INSTANCE, interchangeable
        self.gaming_channel = [1256421833884958800, 903261559181160478, 1255987489907277896]

    @commands.command()
    async def game(self, ctx, *, args: str):
        try:
            await ctx.message.delete()

            if ctx.channel.id not in self.gaming_channel:
                await ctx.send("Please use this command only in <#1256421833884958800> or <#903261559181160478> or <#1255987489907277896> only.")
                return

            parts = [arg.strip('"') for arg in args.split('"') if arg.strip() and arg != ' ']
            if len(parts) != 7:
                await ctx.send("Please format your command like:\n`!game \"Title\" \"Description\" \"Version\" \"Size\" \"Date\" \"Link\" \"Image URL\"`")
                return

            title, desc, vers, size, date, link, image_url = parts
            embed = discord.Embed(title=title, description=desc, url=link, color=discord.Color.random())
            embed.set_thumbnail(url=image_url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar or ctx.author.default_avatar.url)
            embed.add_field(name=":tools: Version", value=vers, inline=True)
            embed.add_field(name=":floppy_disk: Size", value=size, inline=True)
            embed.add_field(name=":date: Release Date", value=date, inline=True)

            view = View()
            emoji = self.bot.get_emoji(1144807049297924116)
            button = Button(label="Download", style=discord.ButtonStyle.link, url=link, emoji=emoji)
            view.add_item(button)

            embed.set_image(url=image_url)
            embed.set_footer(text=f"Game submitted by {ctx.author.display_name}")
            embed.timestamp = ctx.message.created_at

            games_channel = self.bot.get_channel(1255987489907277896)
            if games_channel:
                await games_channel.send(embed=embed, view=view)
                await ctx.send(f"{ctx.author.display_name} posted a game at <#1255987489907277896>")
            else:
                await ctx.send("Games channel not found.")

        except Exception as e:
            await ctx.send(f"Something went wrong: {e}")
    
async def setup(bot):
    await bot.add_cog(AllBotCommands(bot))