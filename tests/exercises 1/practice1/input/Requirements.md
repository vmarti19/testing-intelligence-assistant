# Simple Database Manager

This simple script program coded in Python should will allow the user to perform simple
database actions like create, read, update and delete. The database will be a simple
JSON file.

## Features

- Create a new table.
- Add a new record.
- Read all records.
- Update an existing record.
- Delete a record.

## JSON File Structure

The JSON file should have the following structure:

```json
{
  "TABLE_NAME": {
    "columns": [
      "name",
      "email"
    ],
    "rows": [
      {
        "<id>": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      {
        "<id>": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
      }
    ]
  }
}
```

Where:

- **TABLE_NAME** will be the name of the table. It could be any valid string.
- **columns** will contain the name of each column in the table.
- **rows** will contain an array of objects, where each object represents a row in the table.

Each row has an internal **<id>** that will be assigned by the script and should be unique for each row.
This **<id>** will be used to identify the row when updating or deleting.

## Requirements

All the actions will be executed as a single shot directly from the command line. The user should
not have to interact with the script itself.

The commands to execute each feature will be:

- **Create a new table**: `python simple_database.py create <table_name> <column1> <column2> ...`
- **Create a new record**: `python simple_database.py add <table_name> <column1>=<value1> <column2>=<value2> ...`
- **Read all records**: `python simple_database.py read <table_name>`
- **Update an existing record**: `python simple_database.py update <table_name> <id> <column1>=<value1> <column2>=<value2> ...`
- **Delete a record**: `python simple_database.py delete <table_name> <id>`

## Example

`python simple_database.py create UsersTable name age`

Will create the following table:

```json
{
  "UsersTable": {
    "columns": [
      "name",
      "age"
    ],
    "rows": []
  }
}
```

`python simple_database.py read UsersTable`

Will print to the console:

```
UserTable
---------
|  ID  |  name | age |
|------|-------|-----|
```

`python simple_database.py add UsersTable name=John age=30`

This will update the database with:

```json
{
  "UsersTable": {
    "columns": [
      "name",
      "age"
    ],
    "rows": [
    {
        "<id>": 1,
        "name": "John",
        "age": "30"
      }
    ]
  }
}
```

`python simple_database.py read UsersTable`

Will print to the console:

```
UserTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | John   | 30    |
```

`python simple_database.py add UsersTable name=Alice age=25`
`python simple_database.py update UsersTable 1 age=35`

This will update the database with:

```json
{
  "UsersTable": {
    "columns": [
      "name",
      "age"
    ],
    "rows": [
      {
        "<id>": 1,
        "name": "John",
        "age": "35"
      },
        {
        "<id>": 2,
        "name": "Alice",
        "age": "25"
      }
    ]
  }
}
```

`python simple_database.py read UsersTable`

Will print to the console:

```
UserTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | John   | 35    |
| 2    | Alice  | 25    |
```

`python simple_database.py delete UsersTable 1`

This will update the database with:

```json
{
  "UsersTable": {
    "columns": [
      "name",
      "age"
    ],
    "rows": [
      {
        "<id>": 1,
        "name": "Alice",
        "age": "25"
      }
    ]
  }
}
```

`python simple_database.py read UsersTable`

Will print to the console:

```
UserTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | Alice  | 25    |
```
