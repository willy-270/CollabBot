import client   
import commands
from db import create_tables

if __name__ == "__main__":
    create_tables()
    client.run()    