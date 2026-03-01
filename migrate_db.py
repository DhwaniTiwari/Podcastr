import sqlite3

conn = sqlite3.connect('podcastr.db')
cursor = conn.cursor()

try:
    # Try adding full_name if not exists
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
        print("Column 'full_name' added.")
    except:
        pass

    # Try adding views if not exists
    try:
        cursor.execute("ALTER TABLE podcasts ADD COLUMN views INTEGER DEFAULT 0")
        print("Column 'views' added.")
    except:
        pass
        
    # Create Playlist Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR NOT NULL,
        user_id INTEGER REFERENCES users(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_podcast (
        playlist_id INTEGER REFERENCES playlists(id) ON DELETE CASCADE,
        podcast_id INTEGER REFERENCES podcasts(id) ON DELETE CASCADE
    )
    """)
    print("Playlist tables created.")

except Exception as e:
    print(f"Migration Error: {e}")

conn.commit()
conn.close()
