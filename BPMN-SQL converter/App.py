import os, parser_to_json, DatabaseManager, DataProcessor, config, json, time
class App:

    output_files = []
    path_bpmn = "./bpmn"
    last_modified_times = {}

    db_manager = DatabaseManager.DatabaseManager(
        host=config.HOST,
        database=config.DATABASE,
        user=config.USER,
        password=config.PASSWORD
    )

    def __init__(self):
        self.output_files = os.listdir(self.path_bpmn)

        for file in self.output_files:
            if os.path.splitext(file)[1] == '.bpmn':
                self.last_modified_times[file] = os.path.getmtime(f"{self.path_bpmn}/{file}")

    def check_for_new_or_modified(self):
        for file in os.listdir(self.path_bpmn):
            if os.path.splitext(file)[1] == '.bpmn':
                if file not in self.output_files:

                    print(f"Новый файл: {file}")
                    self.output_files.append(file)
                    self.last_modified_times[file] = os.path.getmtime(f"{self.path_bpmn}/{file}")
                    self.process_file(file)
                else:

                    current_mtime = os.path.getmtime(f"{self.path_bpmn}/{file}")
                    if current_mtime > self.last_modified_times[file]:
                        print(f"Изменен файл: {file}")
                        self.last_modified_times[file] = current_mtime
                        self.process_file(file)

    def process_file(self, file):
        parser_to_json.parser_to_json(f"{self.path_bpmn}/{os.path.splitext(os.path.basename(file))[0]}.bpmn",
                                   f"./json/{os.path.splitext(os.path.basename(file))[0]}.json")

        with open(f"./json/{os.path.splitext(os.path.basename(file))[0]}.json", 'r') as f:
            data = json.load(f)

        processor = DataProcessor.DataProcessor(self.db_manager)
        processor.process_data(data)

    def run(self):
        while True:
            self.check_for_new_or_modified()
            time.sleep(1)
