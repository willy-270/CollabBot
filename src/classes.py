import discord
import db

class Part:
    def __init__(self, 
                 timestamp_pair: str,  
                 guild_id: int, 
                 collab_title: str,
                 part_num: int,
                 msg: discord.Message = None,
                 participant: discord.User = None):
        self.timestamp_pair = timestamp_pair
        self.guild_id = guild_id
        self.collab_title = collab_title
        self.part_num = part_num
        self.participant = participant
        self.msg = msg

        db.part_init(timestamp_pair, guild_id, collab_title, part_num, None, None)

    async def take(self, user: discord.User) -> None:
        self.participant = user
        part_embed = self.msg.embeds[0]
        part_embed.description = f"Timestamp: {self.timestamp_pair}\nParticipant: {self.participant.mention}"
        part_embed.set_thumbnail(url=user.avatar.url)
        part_embed.color = discord.Color.green()

        db.take_part(self.participant.id, self.collab_title, self.part_num)

        await self.msg.edit(embed=part_embed) 

class Collab:
    def __init__(self, 
                 title: str, 
                 owner: discord.Member, 
                 channel: discord.TextChannel, 
                 guild_id: int,
                 timestamp_pairs: str):
        self.title = title
        self.owner = owner
        self.channel = channel
        self.guild_id = guild_id

        timestamps = timestamp_pairs.split(", ")

        parts = []
        part_num = 1
        for timestamp_pair in timestamps:
            part = Part(timestamp_pair, guild_id, title, part_num)
            parts.append(part)
            part_num += 1

        self.parts = parts

        db.collab_init(title, owner.id, channel.id, guild_id)         

    async def send(self, channel: discord.TextChannel):
        title_embed = discord.Embed()
        title_embed.title = self.title
        title_embed.description = f"Owner: {self.owner.mention}"
        await channel.send(embed=title_embed)

        for part in self.parts:
            part_embed = discord.Embed()
            part_embed.title = f"Part {part.part_num}"
            part_embed.description = f"Timestamp: {part.timestamp_pair}"
            if part.participant != None:
                part_embed.description += f"\nParticipant: {part.participant.mention}"
                part_embed.thumbnail = part.participant.avatar_url
                part_embed.color = discord.Color.green()
            else:
                part_embed.description += "\nParticipant: None"

            part_msg = await channel.send(embed=part_embed)
            part.msg_id = part_msg.id

            db.set_msg_id(part_msg.id, self.title, part.part_num)