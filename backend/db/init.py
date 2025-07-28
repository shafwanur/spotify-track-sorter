from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@db:5432/spotify")

def init_db(): 
    '''
    For now, creates the initial required tables. 
    '''
    with engine.connect() as conn:
        query = text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE, 
                password VARCHAR(255)
            );
        """) # IMPORTANT: username is email. 
        conn.execute(query)
        conn.commit()

        print("Success: DB initialized.")
