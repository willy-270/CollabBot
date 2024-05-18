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

        if not db.part_already_exists(collab_title, part_num, guild_id):
            db.part_init(timestamp_pair, guild_id, collab_title, part_num, msg, participant)

    def make_part_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = f"Part {self.part_num}"
        embed.description = f"Timestamp: {self.timestamp_pair}"
        if self.participant != None:
            embed.description += f"\nParticipant: {self.participant.mention}"
            embed.set_thumbnail(url=self.participant.avatar.url)
            embed.color = discord.Color.green()
        else:
            embed.description += "\nParticipant: None"
        
        return embed

    async def take(self, user: discord.User) -> None:
        self.participant = user
        part_embed = self.make_part_embed()

        db.update_part_participant(user.id, self.collab_title, self.part_num, self.guild_id)

        await self.msg.edit(embed=part_embed) 

    async def drop(self) -> None:
        self.participant = None
        part_embed = self.make_part_embed()

        db.update_part_participant(None, self.collab_title, self.part_num, self.guild_id)

        await self.msg.edit(embed=part_embed)

    async def delete_msg(self) -> None:
        await self.msg.delete()

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
        self.timestamp_pairs = timestamp_pairs
        self.tite_msg = None

        timestamps = timestamp_pairs.split(", ")

        parts = []
        part_num = 1
        for timestamp_pair in timestamps:
            part = Part(timestamp_pair, guild_id, title, part_num)
            parts.append(part)
            part_num += 1

        self.parts = parts

        if not db.title_already_exists(title, guild_id):
            db.collab_init(title, owner.id, channel.id, guild_id, timestamp_pairs)

    def make_collab_title_embed(self) -> discord.Embed:
        embed = discord.Embed()
        embed.title = self.title
        embed.description = f"Owner: {self.owner.mention}"

        return embed         

    async def send(self):
        title_embed = self.make_collab_title_embed()
        self.title_msg = await self.channel.send(embed=title_embed)
        db.set_title_msg_id(self.title_msg.id, self.title, self.guild_id)

        for part in self.parts:
            part_embed = part.make_part_embed()

            part_msg = await self.channel.send(embed=part_embed)
            part.msg_id = part_msg.id

            db.set_part_msg_id(part_msg.id, self.title, part.part_num, self.guild_id)

    async def delete(self):
        for part in self.parts:
            await part.delete_msg()
        await self.title_msg.delete()
        db.delete_collab(self.title, self.guild_id)



