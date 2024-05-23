import sqlite3
from client import bot
import discord
from classes import Part, Collab

conn = sqlite3.connect('collab.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Parts (
            id INTEGER PRIMARY KEY,
            timestamp_pair TEXT, 
            guild_id INTEGER, 
            collab_title TEXT, 
            part_num INTEGER, 
            msg_id INTEGER, 
            participant_id INTEGER,
            prog_status INTEGER
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Collabs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            owner_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER,
            timestamp_pairs TEXT,
            title_msg_id INTEGER,
            role_id INTEGER
        )''')

    conn.commit()

parts_table = {
    "id": 0,
    "timestamp_pair": 1,
    "guild_id": 2,
    "collab_title": 3,
    "part_num": 4,
    "msg_id": 5,
    "participant_id": 6,
    "prog_status": 7
}

collabs_table = {
    "id": 0,
    "title": 1,
    "owner_id": 2,
    "channel_id": 3,
    "guild_id": 4,
    "timestamp_pairs": 5,
    "title_msg_id": 6,
    "role_id": 7
}

def part_init(part: Part):
    if part.msg:
        msg_id = part.msg.id
    else:
        msg_id = None

    if part.participant:
        participant_id = part.participant.id
    else:
        participant_id = None

    cursor.execute('''
            INSERT INTO Parts (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id, prog_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (part.timestamp_pair, part.guild_id, part.collab_title, part.part_num, msg_id, participant_id, part.prog_status))
    conn.commit()

def collab_init(collab: Collab):
    cursor.execute('''
            INSERT INTO Collabs (title, owner_id, channel_id, guild_id, timestamp_pairs, role_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (collab.title, collab.owner.id, collab.channel.id, collab.guild_id, collab.timestamp_pairs, collab.role.id if collab.role else None))       
    conn.commit() 

def set_title_msg_id(collab: Collab):
    cursor.execute('''UPDATE Collabs
                      SET title_msg_id = ?
                      WHERE title = ?
                      AND guild_id = ?''',
                      (collab.title_msg.id, collab.title, collab.guild_id))
    conn.commit()

def set_part_msg_id(part: Part):
    cursor.execute('''
        UPDATE Parts
        SET msg_id = ?
        WHERE collab_title = ?
        AND part_num = ?
        AND guild_id = ?''',
        (part.msg.id, part.collab_title, part.part_num, part.guild_id))
    conn.commit()

async def get_part_from_guild(collab_title: str, part_num: int, guild_id: int) -> Part | None:
    part_r = cursor.execute('''
        SELECT * FROM Parts
        WHERE collab_title = ?
        AND part_num = ?
        AND guild_id = ?''',
        (collab_title, part_num, guild_id)).fetchone()
    
    if not part_r:
        return None
    
    collab_r = cursor.execute('''
        SELECT * from Collabs
        WHERE title = ?
        AND guild_id = ?''',
        (collab_title, guild_id)).fetchone()
    
    if not collab_r:
        return None
    
    channel_id = collab_r[collabs_table["channel_id"]]
        
    if not part_r[parts_table["participant_id"]]:
        participant = None
    else:
        participant = await bot.fetch_user(part_r[parts_table["participant_id"]])

    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(part_r[parts_table["msg_id"]])
    
    return Part(part_r[parts_table["timestamp_pair"]], 
                part_r[parts_table["guild_id"]], 
                part_r[parts_table["collab_title"]], 
                part_r[parts_table["part_num"]], 
                message, 
                participant)

async def get_collab_from_guild(collab_title: str, guild_id: int) -> Collab | None:
    collab_r = cursor.execute('''
        SELECT * from Collabs
        WHERE title = ?
        AND guild_id = ?''',
        (collab_title, guild_id)).fetchone()
    
    if not collab_r:
        return None
    
    channel_id = collab_r[collabs_table["channel_id"]]
    channel = bot.get_channel(channel_id)

    parts = []
    timestamps = collab_r[collabs_table["timestamp_pairs"]].split(", ")

    for timestamp_pair in timestamps:
        part = await get_part_from_guild(collab_title, len(parts) + 1, guild_id)
        parts.append(part)

    guild = bot.get_guild(guild_id)
    
    collab = Collab(collab_r[collabs_table["title"]], 
                    await bot.fetch_user(collab_r[collabs_table["owner_id"]]), 
                    channel, 
                    collab_r[collabs_table["guild_id"]],
                    collab_r[collabs_table["timestamp_pairs"]],
                    guild.get_role(collab_r[collabs_table["role_id"]]) if collab_r[collabs_table["role_id"]] else None)
    collab.parts = parts
    collab.title_msg = await channel.fetch_message(collab_r[collabs_table["title_msg_id"]])

    return collab
    
def update_part_participant(part: Part) -> None:
    if part.participant:
        participant_id = part.participant.id
    else:
        participant_id = None
    cursor.execute('''UPDATE Parts
                      SET participant_id = ?
                      WHERE collab_title = ?
                      AND part_num = ?
                      AND guild_id = ?''',
                      (participant_id, part.collab_title, part.part_num, part.guild_id))
    conn.commit()

    update_part_status(part)

def part_already_exists(part: Part) -> bool:
    return bool(cursor.execute('''SELECT * FROM Parts
                               WHERE collab_title = ?
                               AND part_num = ?
                               AND guild_id = ?''', 
                               (part.collab_title, part.part_num, part.guild_id,)).fetchone())

def collab_already_exists(collab: Collab) -> bool:
    return bool(cursor.execute('''SELECT * FROM Collabs
                               WHERE title = ?
                               AND guild_id = ?''', 
                               (collab.title, collab.guild_id,)).fetchone())

def title_already_exists(title: str, guild_id: int) -> bool:
    return bool(cursor.execute('''SELECT * FROM Collabs 
                               WHERE title = ?
                               AND guild_id = ?''', 
                               (title, guild_id,)).fetchone())

def get_collab_owner_id(collab_title: str, guild_id: int) -> int | None:
    r = cursor.execute('''SELECT owner_id FROM Collabs
                          WHERE title = ?
                          AND guild_id = ?''',
                          (collab_title, guild_id)).fetchone()
    if r:
        return r[0]
    else:
        return None

def delete_collab(collab: Collab) -> None:
    cursor.execute('''DELETE FROM Collabs
                      WHERE title = ?
                      AND guild_id = ?''',
                      (collab.title, collab.guild_id))
    cursor.execute('''DELETE FROM Parts
                      WHERE collab_title = ?
                      AND guild_id = ?''',
                      (collab.title, collab.guild_id))
    conn.commit()

def get_collab_titles(guild_id: int) -> list[str]:
    return [title[0] for title in cursor.execute('''
        SELECT title FROM Collabs
        WHERE guild_id = ?''',
        (guild_id,)).fetchall()]

def update_part_status(part: Part) -> None:
    cursor.execute('''UPDATE Parts
                      SET prog_status = ?
                      WHERE collab_title = ?
                      AND part_num = ?
                      AND guild_id = ?''',
                      (part.prog_status, part.collab_title, part.part_num, part.guild_id))
    conn.commit()
