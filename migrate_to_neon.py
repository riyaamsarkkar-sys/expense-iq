import sqlite3
from sqlalchemy import create_engine, text

# PASTE YOUR NEON URL HERE
NEON_URL = "postgresql://neondb_owner:npg_iVd7N8beFvqL@ep-red-hill-aokll548-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Connect to SQLite
sqlite_conn = sqlite3.connect("practice1.db")
sqlite_cur = sqlite_conn.cursor()

# Connect to Neon
engine = create_engine(NEON_URL)

with engine.begin() as conn:

    # Clear existing data
    conn.execute(text('DELETE FROM prac'))
    conn.execute(text('DELETE FROM "user"'))

    # Import users
    users = sqlite_cur.execute(
        "SELECT id, username, email, password FROM user"
    ).fetchall()

    for user in users:
        conn.execute(
            text("""
                INSERT INTO "user"
                (id, username, email, password)
                VALUES (:id, :username, :email, :password)
            """),
            {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "password": user[3]
            }
        )

    # Import expenses
    expenses = sqlite_cur.execute(
        """
        SELECT sno, Title, Category, Amount,
               Description, expense_date, user_id
        FROM prac
        """
    ).fetchall()

    for exp in expenses:
        conn.execute(
            text("""
                INSERT INTO prac
                (sno, "Title", "Category", "Amount",
                 "Description", expense_date, user_id)
                VALUES
                (:sno, :title, :category, :amount,
                 :description, :expense_date, :user_id)
            """),
            {
                "sno": exp[0],
                "title": exp[1],
                "category": exp[2],
                "amount": exp[3],
                "description": exp[4],
                "expense_date": exp[5],
                "user_id": exp[6]
            }
        )

print("Migration completed successfully!")