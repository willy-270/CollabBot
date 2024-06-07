from db import create_tables
import client   

if __name__ == "__main__":
    import commands
    import on_delete
    
    create_tables()
    client.run()