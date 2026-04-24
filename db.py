import psycopg2

conn = psycopg2.connect(
    dbname="snake",
    user="postgres",
    password="Sondy_667",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()


def save_game(username, score, level):
    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    res = cur.fetchone()

    if res:
        player_id = res[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id",
            (username,)
        )
        player_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """, (player_id, score, level))

    conn.commit()


def get_best(username):
    cur.execute("""
        SELECT MAX(score)
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        WHERE username=%s
    """, (username,))
    res = cur.fetchone()
    return res[0] if res[0] else 0


def get_top():
    cur.execute("""
        SELECT username, score, level_reached
        FROM game_sessions
        JOIN players ON players.id = game_sessions.player_id
        ORDER BY score DESC
        LIMIT 10
    """)
    return cur.fetchall()