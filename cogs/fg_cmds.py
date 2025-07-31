import discord
from discord.ext import commands
from discord import app_commands
from api.fitgirl_api import FitGirlAPI
from datetime import datetime, timezone


class FitGirlCommands(commands.Cog):
    def __init__(self, bot):
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
                embed.add_field(name=f"> {release['title']}", value="", inline=True)   
            
            user = await self.bot.fetch_user(505809822239948806)
            embed.set_footer(text=f'Data scraped by {user.display_name}', icon_url=user.display_avatar.url) 
            embed.timestamp = now

            await interaction.response.send_message(embed=embed, ephemeral=False)
                  
        except Exception as e:
            await interaction.response.send_message(f'Something went wrong {e}', ephemeral=True)
            
            
    @app_commands.command(name="fg_new_release", description="Get new releases from FitGirl Repacks")
    async def fg_new_release(self, interaction: discord.Interaction):
        try:
            fitgirl = FitGirlAPI()
            data = fitgirl.new_release()

            if data['status'] != 'success' or not data['new_releases']:
                await interaction.response.send_message("No new releases found today.", ephemeral=False)
                return
            embeds = []
            user = await self.bot.fetch_user(505809822239948806)
            for release in data['new_releases']:
                embed = discord.Embed(
                    title=release['title'],
                    url=release['link'],
                    color=discord.Color.blue()
                )
                embed.set_author(name=release.get('company', 'Unknown Publisher'))

                if release['image_url']:
                    embed.set_thumbnail(url=release['image_url'])
                    embed.set_image(url=release['image_url'])
                embed.add_field(name="🌐 Languages", value=release.get('languages', 'N/A'), inline=True)
                embed.add_field(name="💾 Original Size", value=release.get('original_size', 'N/A'), inline=True)
                embed.add_field(name="📦 Repack Size", value=release.get('repack_size', 'N/A'), inline=True)
                try:
                    post_date = datetime.fromisoformat(release["date"]).date()
                    formatted_date = post_date.strftime("%B %d, %Y")  # e.g., "July 31, 2025"
                except Exception:
                    formatted_date = "Unknown date"
                embed.set_footer(text=f"Scraped by {user.display_name} • {formatted_date}", icon_url=user.display_avatar.url)

                embeds.append(embed)

            for embed in embeds:
                await interaction.channel.send(embed=embed)

            # await interaction.response.send_message("✅ Sent today's new releases!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Something went wrong: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(FitGirlCommands(bot))
        
        