import psycopg2, config

class DatabaseManager:

    def __init__(self, host, database, user, password):
        """Инициализация класса."""
        print("Инициализация класса")
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        """Закрытие курсора и подключения при удалении объекта."""
        self.cur.close()
        self.conn.close()

    def execute(self, query, params=None):
        """Выполнение SQL-запроса."""
        if params:
            self.cur.executemany(query, params)
        else:
            self.cur.execute(query)
        return self.cur

    def fetchone(self):
        """Получение одной строки из результата запроса."""
        return self.cur.fetchone()

    def fetchall(self):
        """Получение всех строк из результата запроса."""
        return self.cur.fetchall()

    def commit(self):
        """Сохранение изменений в базе данных."""
        self.conn.commit()

    def create_table(self, table_name, columns):
        """Создание новой таблицы."""
        column_definitions = ", ".join(f"{name} {type_}" for name, type_ in columns)
        query = f"CREATE TABLE {table_name} ({column_definitions})"
        self.execute(query)

    def insert_data(self, table_name, data):
        """Вставка данных в таблицу."""

        columns = ", ".join([item[0] for item in data])
        placeholders = ", ".join(["%s" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = [tuple([item[1] for item in data])]
        self.execute(query, values)

    def get_table_columns(self, table_name):
        """Получение списка столбцов в таблице."""
        query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
        return [column[0].lower() for column in self.execute(query).fetchall()]

    def update_data(self, table_name, data, condition):
        """Обновление данных в таблице."""
        if type(data[0][1]) == int:
            query = f"UPDATE {table_name} SET {data[0][0]} = {data[0][1]} WHERE {condition}"
        else:
            query = f"UPDATE {table_name} SET {data[0][0]} = '{data[0][1]}' WHERE {condition}"
        self.execute(query)

    def get_column_data(self, table_name, column_name):
        """Возвращает все элементы заданного столбца в заданной таблице."""
        query = f"SELECT {column_name} FROM {table_name}"
        self.execute(query)
        return [row[0] for row in self.fetchall()]

    def delete_column_data(self, table_name, parent_id):
        """Удаляет все элементы заданной таблицы по parent_id."""
        query = f"DELETE FROM {table_name} WHERE parent_id='{parent_id}'"
        self.execute(query)

    def delete_data_for_parent(self, parent_id):
        """Удаление данных для существующей родительской записи."""
        tables = self.get_existing_tables()
        for table in tables:
            if table != config.PARENT_TABLE_NAME:
                self.delete_column_data(table, parent_id)

    def get_existing_tables(self):
        """Получение списка существующих таблиц."""
        self.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return [table[0].lower() for table in self.fetchall()]
