from client import bot
import discord
import db
from classes import Collab

def reponse_embed(title):
    embed = discord.Embed()
    embed.title = title

    return embed

@bot.tree.command(
    name="make_collab",
    description="Create a new collab"
)
@discord.app_commands.describe(
    timestamps="give start points of each part, serpated by comma and space ex: 0:00, 0:30, 1:00",
    role_allowed_to_take_parts="leave empty for part participatns to only be changable by the host"
)
async def make_collab(
    interaction: discord.Interaction,
    title: str,
    timestamps: str,
    channel: discord.TextChannel,
    role_allowed_to_take_parts: discord.Role = None
):
    await interaction.response.send_message(embed=reponse_embed("Working..."), ephemeral=True)

    title = title.lower()
    same_title = db.title_already_exists(title, interaction.guild.id)

    if same_title:
        await interaction.edit_original_response(embed=reponse_embed("Collab with that title already exists in this server"))
        return

    def format_timestamps(timestamps: list[str]):
        formatted_timestamps = []
        for i in range(len(timestamps) - 1):
            formatted_timestamps.append(f"{timestamps[i]} - {timestamps[i+1]}")
        return ", ".join(formatted_timestamps)
    
    formatted_timestamps = format_timestamps(timestamps.split(", "))

    collab = Collab(title, interaction.user, channel, interaction.guild.id, formatted_timestamps, role_allowed_to_take_parts)
    await collab.send()

    await interaction.edit_original_response(embed=reponse_embed("done"))

@bot.tree.command(
    name="take_part",
    description="Join a collab"
)
async def take_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int
):
    await interaction.response.send_message(embed=reponse_embed("Working..."))

    collab = await db.get_collab_from_guild(collab_title, interaction.guild.id)

    if not collab:
        await interaction.edit_original_response(embed=reponse_embed("Collab not found in this server"))
        return
    
    if collab.role not in interaction.user.roles:
        if collab.owner == interaction.user:
            pass
        else:
            await interaction.edit_original_response(embed=reponse_embed("You do not have the role required to take parts in this collab"))
            return

    part = await db.get_part_from_guild(collab_title, part_num, interaction.guild.id)
    
    if not part:
        await interaction.edit_original_response(embed=reponse_embed("Part not found in this server"))
        return
    
    if part.participant != None:
        await interaction.edit_original_response(embed=reponse_embed("Part already taken"))
        return

    await part.take(interaction.user)
    await interaction.edit_original_response(embed=reponse_embed("done"))

@bot.tree.command(
    name="drop_part",
    description="Leave a collab"
)
async def drop_part(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int,
):
    await interaction.response.send_message(embed=reponse_embed("Working..."))

    collab = await db.get_collab_from_guild(collab_title, interaction.guild.id)

    if not collab:
        await interaction.edit_original_response(embed=reponse_embed("Collab not found in this server"))
        return
    
    if collab.role == None:
        await interaction.edit_original_response(embed=reponse_embed("Only the host can remove participants from this collab"))
        return

    part = await db.get_part_from_guild(collab_title, part_num, interaction.guild.id)
    
    if not part:
        await interaction.edit_original_response(embed=reponse_embed("Part not found in this server"))
        return

    if part.participant != interaction.user:
        await interaction.edit_original_response(embed=reponse_embed("Part is either taken by someone else or is already empty"))
        return

    await part.drop()
    await interaction.edit_original_response(embed=reponse_embed("done"))

@bot.tree.command(
    name="delete_collab",
    description="Delete a collab"
)
async def delete_collab(
    interaction: discord.Interaction,
    collab_title: str
):
    await interaction.response.send_message(embed=reponse_embed("Working..."))

    collab = await db.get_collab_from_guild(collab_title, interaction.guild.id)

    if not collab:
        await interaction.edit_original_response(embed=reponse_embed("Collab not found in this server"))
        return
    
    if collab.owner != interaction.user:
        await interaction.edit_original_response(embed=reponse_embed("You are not the owner of this collab"))
        return
    
    await collab.delete()
    await interaction.edit_original_response(embed=reponse_embed("done"))

@bot.tree.command(
    name="update_part_status",
    description="Update the status of a part"
)
@discord.app_commands.choices(status=[
    discord.app_commands.Choice(name='🚫 No Progress', value=0),
    discord.app_commands.Choice(name='🟨 Progress Shown', value=1),
    discord.app_commands.Choice(name='✅ Completed', value=2),
])
async def update_part_status(
    interaction: discord.Interaction,
    collab_title: str,
    part_num: int,
    status: discord.app_commands.Choice[int]
):
    await interaction.response.send_message(embed=reponse_embed("Working..."))

    collab = await db.get_collab_from_guild(collab_title, interaction.guild.id)

    if not collab:
        await interaction.edit_original_response(embed=reponse_embed("Collab not found in this server"))
        return
    
    if collab.owner != interaction.user:
        await interaction.edit_original_response(embed=reponse_embed("You are not the owner of this collab"))
        return

    part = await db.get_part_from_guild(collab_title, part_num, interaction.guild.id)

    if not part:
        await interaction.edit_original_response(embed=reponse_embed("part_num out of range"))
        return
    
    if part.participant == None:
        await interaction.edit_original_response(embed=reponse_embed("Part is not taken"))
        return

    await part.update_part_satus(status.value)
    await interaction.edit_original_response(embed=reponse_embed("done"))

def collab_title_autocomplete(command_func):
    '''takes in a command function, funcion must have collab_title: str as a parameter
    returns an autocomplete function for that command function
    '''
    @command_func.autocomplete("collab_title")
    async def autocomplete(
        interaction: discord.Interaction,
        current: str
    ) -> list[discord.app_commands.Choice]:
        collab_titles = db.get_collab_titles(interaction.guild.id)

        return [discord.app_commands.Choice(name=title, value=title) for title in collab_titles if current.lower() in title.lower()]
    return autocomplete

collab_title_autocomplete(take_part)
collab_title_autocomplete(drop_part)
collab_title_autocomplete(delete_collab)
collab_title_autocomplete(update_part_status)
    