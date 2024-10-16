import config, datetime

class DataProcessor:
    def __init__(self, db_manager):
        """Инициализация класса."""
        self.db_manager = db_manager
        self.parent_table_name = config.PARENT_TABLE_NAME

    def process_data(self, data):
        """Обработка данных из JSON-файла."""

        tables = self.db_manager.get_existing_tables()

        # Обработка родительской записи
        parent_id = self.process_parent_record(data[0])

        # Обработка дочерних записей
        for item in data[1:]:
            self.process_item(item, tables, parent_id)

        self.db_manager.commit()

    def process_parent_record(self, parent_data):
        """Обработка родительской записи."""

        parent_id = parent_data.get("collaboration_id", "NAME UNDEFINDED")
        name = parent_data.get("operation_name", "NAME UNDEFINDED")

        # Проверка, существует ли родительская запись
        if parent_id in self.db_manager.get_column_data(self.parent_table_name, "id"):
            # Удаление данных для существующей родительской записи
            self.db_manager.delete_data_for_parent(parent_id)
        else:
            # Вставка новой родительской записи
            self.db_manager.insert_data(self.parent_table_name, [("id", parent_id), ("name", name)])

        return parent_id

    def process_item(self, item, tables, parent_id):
        """Обработка дочерней записи."""

        operation_name = item.get("name", "").lower()
        local_id = item.get("id", "").lower()

        if operation_name[0] not in config.ALPHABET:
            print(f"Ошибка в создании таблицы: {operation_name}, первый символ не может быть: {operation_name[0]}")

        elif operation_name == 'true' or operation_name == 'false':
            print(f"Ошибка в создании таблицы: {operation_name}, не может называться: {operation_name}")

        else:
            # Создание таблицы, если она не существует
            if operation_name not in tables:

                self.db_manager.create_table(operation_name, [("parent_id", "varchar"), ("local_id", "varchar PRIMARY KEY")])
                tables.append(operation_name)


            # Вставка данных в таблицу
            self.db_manager.insert_data(operation_name, [("parent_id", parent_id), ("local_id", local_id)])

            # Обработка входных параметров
            self.process_input_parameters(item, operation_name, local_id)

    def process_input_parameters(self, item, operation_name, local_id):
        """Обработка входных параметров."""

        columns = self.db_manager.get_table_columns(operation_name)

        for parameter in item.get("input_parameters", []):
            parameter_name = parameter["name"].lower()
            parameter_value = self.check_type(parameter.get("value") or 0)
            sql_type = self.get_current_type(parameter_value)

            # Добавление столбца, если он не существует
            if parameter_name not in columns:
                self.db_manager.execute(f"ALTER TABLE {operation_name} ADD {parameter_name} {sql_type}")
                columns.append(parameter_name)

            # Обновление значения столбца
            self.db_manager.update_data(operation_name, [(parameter_name, parameter_value)], f"local_id = '{local_id}'")

    def get_current_type(self, data):
        """Переводим Python type в SQL type"""
        type_ = type(data)
        types = {
            int: "INTEGER",
            float: "FLOAT",
            str: "VARCHAR",
            bool: "BOOLEAN",
            datetime.datetime: "DATETIME",
            datetime.date: "DATE"
        }
        return types.get(type_)

    def check_type(self, text):
        """Преобразовываем str в возможно другой тип данных"""
        try:
            int(text)
            return int(text)
        except ValueError:
            try:
                float(text)
                return float(text)
            except ValueError:
                return str(text)
