from database import get_conn

conn = get_conn()


conn.cursor().execute("""
CREATE TABLE orders(
    id SERIAL PRIMARY KEY,
    amount MONEY NOT NULL,
    currency INT NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT
)
""")
commit()