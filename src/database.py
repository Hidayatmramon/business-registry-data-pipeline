import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def create_table():
    connection = get_connection()
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(500) NOT NULL UNIQUE,
        company_name VARCHAR(255),
        legal_entity_type VARCHAR(255),
        business_number VARCHAR(100),
        sk_number VARCHAR(255),
        country VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

def insert_company(company):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO companies (
        url,
        company_name,
        legal_entity_type,
        business_number,
        sk_number,
        country
    )
    values (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        company_name = VALUES(company_name),
        legal_entity_type = VALUES(legal_entity_type),
        business_number = VALUES(business_number),
        sk_number = VALUES(sk_number),
        country = VALUES(country)
    """

    values = (
        company['url'],
        company('company_name'),
        company('legal_entity_type'),
        company('business_number'),
        company('sk_number'),
        company('country')
    )

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()