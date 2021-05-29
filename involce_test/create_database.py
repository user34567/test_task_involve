from database import get_conn


def create():
    try:
        conn = get_conn()
    except Exception as e:
        print(e)

    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE orders(
        id SERIAL PRIMARY KEY,
        amount MONEY NOT NULL,
        currency INT NOT NULL,
        date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    )
    """)
    conn.commit()


create()