from client import bot
import discord
import db
from classes import Collab

@bot.tree.command(
    name="make_collab",
    description="Create a new collab"
)
@discord.app_commands.describe(
    timestamps="seperate by comma & space, ex: 0:00-0:10, 0:10-0:20, and so on",
)
async def make_collab(
    interaction: discord.Interaction,
    title: str,
    timestamps: str,
    channel: discord.TextChannel
):
    same_title = db.title_already_exists(title)

    if same_title:
        await interaction.response.send_message("Collab with that title already exists")
        return

    collab = Collab(title, interaction.user, channel, interaction.guild.id, timestamps)
    await collab.send(channel)

    await interaction.response.send_message("done", ephemeral=True)

    
@bot.tree.command(
    name="take_part",
    description="Join a collab"
)
async def take_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int,
):
    part = await db.get_part(collab_title, part_num, interaction.guild.id)
    
    if not part:
        await interaction.response.send_message("Part not found")
        return
    
    if part.participant != None:
        await interaction.response.send_message("Part already taken")
        return

    await part.take(interaction.user)
    await interaction.response.send_message("done", ephemeral=True)