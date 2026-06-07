import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'devices.db')

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_states (
            id TEXT PRIMARY KEY,
            state TEXT NOT NULL
        )
    ''')

    # Default devices based on the current configuration
    default_devices = [
        "light1", "light2", "light3", "hallfan",
        "r1light1", "r1light2", "r1fan",
        "r2light1", "r2light2", "r2fan"
    ]

    # Insert default states if they don't exist
    for device_id in default_devices:
        cursor.execute('''
            INSERT OR IGNORE INTO device_states (id, state)
            VALUES (?, ?)
        ''', (device_id, "OFF"))

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_all_states():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, state FROM device_states')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert list of tuples to a dictionary
    return {row[0]: row[1] for row in rows}

def update_device_state(device_id, state):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE device_states
        SET state = ?
        WHERE id = ?
    ''', (state, device_id))
    
    rowcount = cursor.rowcount
    conn.commit()
    conn.close()
    return rowcount > 0

if __name__ == '__main__':
    init_db()
