from database import Database

db = Database()


db.execute("""
CREATE TABLE orders(
    id SERIAL PRIMARY KEY,
    amount MONEY NOT NULL,
    currency INT NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT
)
""")
commit()