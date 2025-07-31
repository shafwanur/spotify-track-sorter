from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@db:5432/spotify")


def init_db():
    """
    For now, creates the initial required tables.
    """
    with engine.connect() as conn:
        # Create users table
        query = text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE, 
                password VARCHAR(255)
            );
        """)  # IMPORTANT: username is email.
        conn.execute(query)

        # Create refresh_tokens table
        refresh_token_query = text("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY REFERENCES users(id),
                spotify_user_id TEXT NULL,
                refresh_token TEXT
            );
        """)
        conn.execute(refresh_token_query)
        conn.commit()

        print("Success: DB initialized.")
