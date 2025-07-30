import discord
from discord.ext import commands
from discord import app_commands
from api.fitgirl_api import FitGirlAPI
from datetime import datetime, timezone


class FitGirlCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @app_commands.command(name="fg_upcoming_release", description="Get upcoming releases from FitGirl Repacks")
    async def fg_upcoming_release(self, interaction: discord.Interaction):
        try:
            fitgirl = FitGirlAPI()
            data  = fitgirl.upcoming_release()
            
            now = datetime.now(timezone.utc)
            
            if data['status'] != 'success' or not data['upcoming_releases']:
                await interaction.response.send_message('No upcoming releases found')
                return
            
            embed = discord.Embed(title=f'Upcoming Releases - {now.strftime("%B %d, %Y")}', color=discord.Color.green())
            
            for release in data['upcoming_releases']:
                embed.add_field(name=f"• {release['title']}", value="", inline=False)   
            
            user = await self.bot.fetch_user(505809822239948806)
            embed.set_footer(text=f'Data scraped by {user.display_name}', icon_url=user.display_avatar.url) 
            embed.timestamp = now

            await interaction.response.send_message(embed=embed, ephemeral=False)
                  
        except Exception as e:
            await interaction.response.send_message(f'Something went wrong {e}', ephemeral=True)

async def setup(bot):
    await bot.add_cog(FitGirlCommands(bot))
        
        