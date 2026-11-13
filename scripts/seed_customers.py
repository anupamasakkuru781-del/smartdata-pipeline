
from app.database import create_connection


def seed_customers():

    # Sample customer master records
    customers = [
        ("CUST001", "Ananya Sharma", "ananya@example.com"),
        ("CUST002", "Rahul Kumar", "rahul@example.com"),
        ("CUST003", "Priya Reddy", "priya@example.com"),
    ]

    connection = create_connection()

    try:
        cursor = connection.cursor()

        # SQL query to insert customer records
        insert_query = """
            INSERT OR IGNORE INTO customers
            (customer_id, customer_name, email)
            VALUES (?, ?, ?)
        """

        cursor.executemany(insert_query, customers)

        connection.commit()

        print("Customer records inserted successfully!")

        # Display all customer records
        result = cursor.execute(
            """
            SELECT customer_id, customer_name, email
            FROM customers
            ORDER BY customer_id
            """
        ).fetchall()

        print("\nCustomer Master Data:")

        for customer in result:
            print(customer)

        print(f"\nTotal customers in database: {len(result)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_customers()
