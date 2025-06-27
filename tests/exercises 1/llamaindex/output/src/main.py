import json
import sys
import os
import uuid

def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_database.py <database_path> <command> [args...]")
        return

    database_path = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]

    # Ensure the directory exists
    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    # Load the database
    if os.path.exists(database_path):
        with open(database_path, 'r') as f:
            database = json.load(f)
    else:
        database = {}

    if command == 'create':
        if len(args) < 2:
            print("Usage: python simple_database.py <database_path> create <table_name> <column1> <column2> ...")
            return
        table_name = args[0]
        columns = args[1:]
        if table_name in database:
            print(f"Table '{table_name}' already exists.")
            return
        database[table_name] = {
            "columns": columns,
            "rows": []
        }
        with open(database_path, 'w') as f:
            json.dump(database, f, indent=2)
        print(f"Table '{table_name}' created successfully.")
    elif command == 'add':
        if len(args) < 2:
            print("Usage: python simple_database.py <database_path> add <table_name> <column1>=<value1> <column2>=<value2> ...")
            return
        table_name = args[0]
        if table_name not in database:
            print(f"Table '{table_name}' does not exist.")
            return
        row = {}
        for arg in args[1:]:
            if '=' in arg:
                column, value = arg.split('=', 1)
                row[column] = value
        row["<id>"] = str(uuid.uuid4())
        database[table_name]["rows"].append(row)
        with open(database_path, 'w') as f:
            json.dump(database, f, indent=2)
        print(f"Record added to '{table_name}' table.")
    elif command == 'read':
        if len(args) < 1:
            print("Usage: python simple_database.py <database_path> read <table_name>")
            return
        table_name = args[0]
        if table_name not in database:
            print(f"Table '{table_name}' does not exist.")
            return
        table = database[table_name]
        print(f"{table_name}")
        print("---------")
        print(f"|  ID  |  {'  |  '.join(table['columns'])}  |")
        print("|------|" + "-------|" * len(table['columns']))
        for row in table['rows']:
            row_data = [str(row.get(col, '')) for col in table['columns']]
            print(f"| {row['<id>']}  |  {'  |  '.join(row_data)}  |")
    elif command == 'update':
        if len(args) < 2:
            print("Usage: python simple_database.py <database_path> update <table_name> <id> <column1>=<value1> <column2>=<value2> ...")
            return
        table_name = args[0]
        row_id = args[1]
        if table_name not in database:
            print(f"Table '{table_name}' does not exist.")
            return
        table = database[table_name]
        row = None
        for r in table['rows']:
            if r['<id>'] == row_id:
                row = r
                break
        if not row:
            print(f"Record with ID '{row_id}' not found in '{table_name}' table.")
            return
        for arg in args[2:]:
            if '=' in arg:
                column, value = arg.split('=', 1)
                row[column] = value
        with open(database_path, 'w') as f:
            json.dump(database, f, indent=2)
        print(f"Record updated in '{table_name}' table.")
    elif command == 'delete':
        if len(args) < 2:
            print("Usage: python simple_database.py <database_path> delete <table_name> <id>")
            return
        table_name = args[0]
        row_id = args[1]
        if table_name not in database:
            print(f"Table '{table_name}' does not exist.")
            return
        table = database[table_name]
        new_rows = [r for r in table['rows'] if r['<id>'] != row_id]
        table['rows'] = new_rows
        with open(database_path, 'w') as f:
            json.dump(database, f, indent=2)
        print(f"Record deleted from '{table_name}' table.")
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
