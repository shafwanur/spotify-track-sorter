# backend/db/init_db.py
from sqlalchemy import create_engine, text
import time

def init_db():
    engine = create_engine("postgresql://postgres:postgres@db:5432/spotify")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS identity (
                id SERIAL PRIMARY KEY,
                _name VARCHAR(100),
                surname VARCHAR(100)
            );
        """))
        conn.execute(text("""
            INSERT INTO identity (_name, surname)
            VALUES ('Michel', 'Palefrois'), ('Renaud', 'Bertop')
            ON CONFLICT DO NOTHING;
        """))
        conn.commit()
        print("DB initialized.")
