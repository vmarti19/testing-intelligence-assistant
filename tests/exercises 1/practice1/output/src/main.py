import sys
import json
import os

DATABASE_FILE = 'database.json'


def load_database():
    if not os.path.exists(DATABASE_FILE):
        return {}
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_database(database):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(database, f, indent=2)

def create_table(table_name, columns):
    database = load_database()
    if table_name in database:
        print(f"Table '{table_name}' already exists.")
        return
    database[table_name] = {
        'columns': columns,
        'rows': []
    }
    save_database(database)
    print(f"Table '{table_name}' created with columns: {', '.join(columns)}")

def add_record(table_name, record):
    database = load_database()
    if table_name not in database:
        print(f"Table '{table_name}' does not exist.")
        return
    table = database[table_name]
    columns = table['columns']
    
    # Validate that all required columns are provided
    for column in columns:
        if column not in record:
            print(f"Missing required column: {column}")
            return
    
    # Assign a unique ID
    record_id = len(table['rows']) + 1
    record['<id>'] = record_id
    table['rows'].append(record)
    save_database(database)
    print(f"Record added with ID {record_id}")

def read_records(table_name):
    database = load_database()
    if table_name not in database:
        print(f"Table '{table_name}' does not exist.")
        return
    table = database[table_name]
    columns = table['columns']
    rows = table['rows']
    
    if not rows:
        print(f"{table_name}")
        print('-' * len(table_name))
        print(f"| {'ID':^4} | {' | '.join(columns):^} |")
        print(f"|{'-'*4}|{'|'.join(['-'*len(col) for col in columns])}|")
        return

    print(f"{table_name}")
    print('-' * len(table_name))
    print(f"| {'ID':^4} | {' | '.join(columns):^} |")
    print(f"|{'-'*4}|{'|'.join(['-'*len(col) for col in columns])}|")
    
    for row in rows:
        row_values = [str(row[col]) for col in columns]
        print(f"| {row['<id>']:<4} | {' | '.join(row_values):<} |")

def update_record(table_name, record_id, updates):
    database = load_database()
    if table_name not in database:
        print(f"Table '{table_name}' does not exist.")
        return
    table = database[table_name]
    rows = table['rows']
    
    for row in rows:
        if row['<id>'] == record_id:
            for key, value in updates.items():
                row[key] = value
            save_database(database)
            print(f"Record {record_id} in table '{table_name}' updated.")
            return
    print(f"Record {record_id} not found in table '{table_name}'.")

def delete_record(table_name, record_id):
    database = load_database()
    if table_name not in database:
        print(f"Table '{table_name}' does not exist.")
        return
    table = database[table_name]
    rows = table['rows']
    
    for i, row in enumerate(rows):
        if row['<id>'] == record_id:
            del rows[i]
            save_database(database)
            print(f"Record {record_id} in table '{table_name}' deleted.")
            return
    print(f"Record {record_id} not found in table '{table_name}'.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_database.py <command> [arguments]...")
        return

    command = sys.argv[1]

    if command == 'create':
        if len(sys.argv) < 4:
            print("Usage: python simple_database.py create <table_name> <column1> <column2> ...")
            return
        table_name = sys.argv[2]
        columns = sys.argv[3:]
        create_table(table_name, columns)

    elif command == 'add':
        if len(sys.argv) < 4:
            print("Usage: python simple_database.py add <table_name> <column1>=<value1> <column2>=<value2> ...")
            return
        table_name = sys.argv[2]
        record = {}
        for arg in sys.argv[3:]:
            key, value = arg.split('=', 1)
            record[key] = value
        add_record(table_name, record)

    elif command == 'read':
        if len(sys.argv) < 3:
            print("Usage: python simple_database.py read <table_name>")
            return
        table_name = sys.argv[2]
        read_records(table_name)

    elif command == 'update':
        if len(sys.argv) < 5:
            print("Usage: python simple_database.py update <table_name> <id> <column1>=<value1> <column2>=<value2> ...")
            return
        table_name = sys.argv[2]
        record_id = int(sys.argv[3])
        updates = {}
        for arg in sys.argv[4:]:
            key, value = arg.split('=', 1)
            updates[key] = value
        update_record(table_name, record_id, updates)

    elif command == 'delete':
        if len(sys.argv) < 4:
            print("Usage: python simple_database.py delete <table_name> <id>")
            return
        table_name = sys.argv[2]
        record_id = int(sys.argv[3])
        delete_record(table_name, record_id)

    else:
        print("Unknown command. Use 'create', 'add', 'read', 'update', or 'delete'.")

if __name__ == '__main__':
    main()