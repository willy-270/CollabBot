import sqlite3

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
            guild_id INTEGER
        )''')

    conn.commit()

def part_init(timestamp_pair: str, guild_id: int, collab_title: str, part_num: int, msg_id: int, participant_id: int):
    cursor.execute('''
            INSERT INTO Parts (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (timestamp_pair, guild_id, collab_title, part_num, msg_id, participant_id))
    conn.commit()

def collab_init(title: str, owner_id: int, channel_id: int, guild_id: int):
    cursor.execute('''
            INSERT INTO Collabs (title, owner_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)''',
            (title, owner_id, channel_id, guild_id))       
    conn.commit() 

def set_msg_id(msg_id: int, collab_title: str, part_num: int):
    cursor.execute('''
        UPDATE Parts
        SET msg_id = ?
        WHERE collab_title = ?
        AND part_num = ?''',
        (msg_id, collab_title, part_num))
    conn.commit()

def title_already_exists(title: str) -> bool:
    r = cursor.execute('''SELECT * FROM Collabs WHERE title = ?''', (title,)).fetchone()
    return bool(r)

def get_part(collab_title: str, part_num: int):
    return cursor.execute('''
        SELECT * FROM Parts
        WHERE collab_title = ?
        AND part_num = ?
        AND participant_id IS NULL''',
        (collab_title, part_num)).fetchone()

def take_part(participant_id: int, collab_title: str, part_num: int):
    cursor.execute('''
            UPDATE Parts
            SET participant_id = ?
            WHERE collab_title = ?
            AND part_num = ?''',
            (participant_id, collab_title, part_num))
    conn.commit()
    