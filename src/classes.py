import discord
from client import bot
import sqlite3

conn = sqlite3.connect('collab.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Parts (
        id INTEGER PRIMARY KEY,
        timestamp_pair TEXT, 
        guild_id INTEGER, 
        collab_title TEXT, 
        part_num INTEGER, 
        msg_id INTEGER, 
        participant_id INTEGER
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Collabs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        owner_id INTEGER,
        channel_id INTEGER,
        guild_id INTEGER
    )''')

conn.commit()

class Part:
    def __init__(self, 
                 timestamp_pair: str,  
                 guild_id: int, 
                 collab_title: str,
                 part_num: int,
                 msg_id: int = None, 
                 participant: discord.Member = None):
        self.timestamp_pair = timestamp_pair
        self.msg_id = msg_id
        self.part_num = part_num
        self.participant = participant
        self.guild_id = guild_id

        if participant:
            participant_id = participant.id
        else:
            participant_id = None

        cursor.execute('''
            INSERT INTO Parts (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id))
        conn.commit()

class Collab:
    def __init__(self, 
                 title: str, 
                 parts: list[Part], 
                 owner: discord.Member, 
                 channel_id: int, 
                 guild_id: int):
        self.title = title
        self.parts = parts
        self.owner = owner
        self.channel_id = channel_id
        self.guild_id = guild_id

        cursor.execute('''
            INSERT INTO Collabs (title, owner_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)''',
            (title, owner.id, channel_id, guild_id))       
        conn.commit()          

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

            cursor.execute('''
                UPDATE Parts
                SET msg_id = ?
                WHERE collab_title = ?
                AND part_num = ?''',
                (part.msg_id, self.title, part.part_num))
            
        conn.commit()

            
        


