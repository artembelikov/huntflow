import psycopg2
from faker import Faker
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta

# Загружаем параметры из .env
load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

fake = Faker('en_US')

# Генерация случайной даты в последние 6 месяцев
def random_date_in_last_six_months():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 месяцев назад
    random_date = start_date + timedelta(days=random.randint(0, 180))
    return random_date.strftime('%Y-%m-%d %H:%M:%S')

# Функция для создания кандидата
def create_candidate():
    fio = fake.name()
    location_id = fake.random_int(min=1, max=10)
    resume_link = fake.url()
    status = fake.random_element(elements=('Open', 'Closed'))
    creation_date = random_date_in_last_six_months()
    last_update_date = random_date_in_last_six_months()

    # Если LastUpdateDate < CreationDate, поменяем их местами
    if last_update_date < creation_date:
        creation_date, last_update_date = last_update_date, creation_date

    return (fio, location_id, resume_link, status, creation_date, last_update_date)

# Функция для вставки данных
def insert_candidates(batch_size, num_batches):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    try:
        for _ in range(num_batches):
            candidates = [create_candidate() for _ in range(batch_size)]
            cursor.executemany(
                "INSERT INTO Candidates (FullName, LocationID, ResumeLink, Status, CreationDate, LastUpdateDate) VALUES (%s, %s, %s, %s, %s, %s)",
                candidates
            )
            conn.commit()  # Commit every batch_size records
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Основная функция для выполнения вставок в потоках
def parallel_insertion(total_records, batch_size, num_threads):
    num_batches = total_records // (batch_size * num_threads)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
                executor.submit(insert_candidates, batch_size, num_batches)
            for _ in range(num_threads)
        ]
        for future in futures:
            future.result()  # Wait for all threads to finish

# Параметры вставки
TOTAL_RECORDS = 1000000  # Total number of records
BATCH_SIZE = 10000       # Size of each batch
NUM_THREADS = 4          # Number of threads

if __name__ == "__main__":
    parallel_insertion(TOTAL_RECORDS, BATCH_SIZE, NUM_THREADS)