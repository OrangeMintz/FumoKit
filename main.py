import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import Button, View


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def game(ctx, *, args: str  ):
    try:        
        await ctx.message.delete()
        
        # Only allow command in #bot-commands
        if ctx.channel.id != 1256421833884958800:
            await ctx.send("Please use this command in <#1256421833884958800> only.")
            return
        
        parts  = [arg.strip('"')for arg in args.split('"') if arg.strip() and arg !=' ']
        if len(parts) !=7:
            await ctx.send("Please format your command like:\n`!game \"Game Title\" \"Description\" \"Version\" \"Size\" \"Release Date\" \"Link\" \"Image URL\"`")
            
            return
        title, desc, vers, size, date, link, image_url = parts
        embed = discord.Embed(title=title, description=desc, url=link, color=discord.Color.random())
        embed.set_thumbnail(url=image_url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.add_field(name=":tools: Version", value=vers, inline=True)
        embed.add_field(name=":floppy_disk: Size", value=size, inline=True)
        embed.add_field(name=":date: Release Date", value=date, inline=True)
        view = View()
        custom_emoji = bot.get_emoji(1144807049297924116)  
        button = Button(label="Download", style=discord.ButtonStyle.link, url=link, emoji=custom_emoji)
        view.add_item(button)
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Game submitted by {ctx.author.display_name}")
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await ctx.send(f"Something went wrong {e}")
        
bot.run(token, log_handler=handler, log_level=logging.DEBUG)