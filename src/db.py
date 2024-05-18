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
            participant_id INTEGER
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Collabs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            owner_id INTEGER,
            channel_id INTEGER,
            guild_id INTEGER,
            timestamp_pairs TEXT,
            title_msg_id INTEGER
        )''')

    conn.commit()

parts_table = {
    "id": 0,
    "timestamp_pair": 1,
    "guild_id": 2,
    "collab_title": 3,
    "part_num": 4,
    "msg_id": 5,
    "participant_id": 6
}

collabs_table = {
    "id": 0,
    "title": 1,
    "owner_id": 2,
    "channel_id": 3,
    "guild_id": 4,
    "timestamp_pairs": 5,
    "title_msg_id": 6
}

def part_init(timestamp_pair: str, guild_id: int, collab_title: str, part_num: int, msg: discord.Message, participant: discord.User):
    if msg:
        msg_id = msg.id
    else:
        msg_id = None

    if participant:
        participant_id = participant.id
    else:
        participant_id = None

    cursor.execute('''
            INSERT INTO Parts (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id))
    conn.commit()

def collab_init(title: str, owner_id: int, channel_id: int, guild_id: int, timestamp_pairs: str):
    cursor.execute('''
            INSERT INTO Collabs (title, owner_id, channel_id, guild_id, timestamp_pairs)
            VALUES (?, ?, ?, ?, ?)''',
            (title, owner_id, channel_id, guild_id, timestamp_pairs))       
    conn.commit() 

def set_title_msg_id(msg_id: int, collab_title: str, guild_id: int):
    cursor.execute('''UPDATE Collabs
                      SET title_msg_id = ?
                      WHERE title = ?
                      AND guild_id = ?''',
                      (msg_id, collab_title, guild_id))
    conn.commit()

def set_part_msg_id(msg_id: int, collab_title: str, part_num: int, guild_id: int):
    cursor.execute('''
        UPDATE Parts
        SET msg_id = ?
        WHERE collab_title = ?
        AND part_num = ?
        AND guild_id = ?''',
        (msg_id, collab_title, part_num, guild_id))
    conn.commit()

async def get_part_from_server(collab_title: str, part_num: int, guild_id: int) -> Part | None:
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

async def get_collab_from_server(collab_title: str, guild_id: int) -> Collab | None:
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
        part = await get_part_from_server(collab_title, len(parts) + 1, guild_id)
        parts.append(part)

    
    collab = Collab(collab_r[collabs_table["title"]], 
                    await bot.fetch_user(collab_r[collabs_table["owner_id"]]), 
                    channel, 
                    collab_r[collabs_table["guild_id"]],
                    collab_r[collabs_table["timestamp_pairs"]])
    collab.parts = parts
    collab.title_msg = await channel.fetch_message(collab_r[collabs_table["title_msg_id"]])

    return collab
    
def update_part_participant(participant_id: int | None, collab_title: str, part_num: int, guild_id) -> None:
    cursor.execute('''UPDATE Parts
                      SET participant_id = ?
                      WHERE collab_title = ?
                      AND part_num = ?
                      AND guild_id = ?''',
                      (participant_id, collab_title, part_num, guild_id))
    conn.commit()

def part_already_exists(collab_title: str, part_num: int, guild_id: int) -> bool:
    return bool(cursor.execute('''SELECT * FROM Parts
                               WHERE collab_title = ?
                               AND part_num = ?
                               AND guild_id = ?''', 
                               (collab_title, part_num, guild_id,)).fetchone())

def collab_already_exists(collab_title: str, guild_id: int) -> bool:
    return bool(cursor.execute('''SELECT * FROM Collabs
                               WHERE title = ?
                               AND guild_id = ?''', 
                               (collab_title, guild_id,)).fetchone())

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

def delete_collab(collab_title: str, guild_id: int) -> None:
    cursor.execute('''DELETE FROM Collabs
                      WHERE title = ?
                      AND guild_id = ?''',
                      (collab_title, guild_id))
    cursor.execute('''DELETE FROM Parts
                      WHERE collab_title = ?
                      AND guild_id = ?''',
                      (collab_title, guild_id))
    conn.commit()

def get_collab_titles(guild_id: int) -> list[str]:
    return [title[0] for title in cursor.execute('''
        SELECT title FROM Collabs
        WHERE guild_id = ?''',
        (guild_id,)).fetchall()]
