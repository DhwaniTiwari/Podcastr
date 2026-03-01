import sqlite3

def check_users():
    try:
        conn = sqlite3.connect('podcastr.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, podcasts_used, subscription_plan FROM users")
        rows = cursor.fetchall()
        
        print(f"{'ID':<5} | {'Email':<30} | {'Used':<5} | {'Plan'}")
        print("-" * 60)
        
        for row in rows:
             print(f"{row[0]:<5} | {row[1]:<30} | {row[2]:<5} | {row[3]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_users()
