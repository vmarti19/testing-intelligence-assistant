# Test Plan for Simple Database Manager

## Overview
This test plan outlines the steps to test the `simple_database.py` script that fulfills the requirements for a simple database manager. The script allows users to perform basic database operations like create, read, update, and delete using a JSON file as the database.

## Test Environment
- Python 3.x
- JSON file (`db/test_database.json`) as the database
- Command line interface (CLI)

## Test Cases

### 1. Create a New Table
**Objective**: Verify that the script can create a new table with the specified columns.
**Steps**:
1. Run the command: `python simple_database.py db/test_database.json create UsersTable name age`
2. Check the `db/test_database.json` file to ensure the table `UsersTable` is created with columns `name` and `age`.
**Expected Result**:
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

### 2. Add a New Record
**Objective**: Verify that the script can add a new record to the table.
**Steps**:
1. Run the command: `python simple_database.py db/test_database.json add UsersTable name=John age=30`
2. Check the `db/test_database.json` file to ensure the record is added.
**Expected Result**:
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

### 3. Read All Records
**Objective**: Verify that the script can read all records from the table and display them in the console.
**Steps**:
1. Run the command: `python simple_database.py db/test_database.json read UsersTable`
2. Check the console output to ensure the records are displayed in the expected format.
**Expected Result**:
```
UsersTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | John   | 30    |
```

### 4. Update an Existing Record
**Objective**: Verify that the script can update an existing record in the table.
**Steps**:
1. Run the command: `python simple_database.py db/test_database.json add UsersTable name=Alice age=25`
2. Run the command: `python simple_database.py db/test_database.json update UsersTable 1 age=35`
3. Check the `db/test_database.json` file to ensure the record is updated.
**Expected Result**:
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

### 5. Delete a Record
**Objective**: Verify that the script can delete a record from the table.
**Steps**:
1. Run the command: `python simple_database.py db/test_database.json delete UsersTable 1`
2. Check the `db/test_database.json` file to ensure the record is deleted.
**Expected Result**:
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

## Conclusion
These test cases ensure that the `simple_database.py` script functions correctly according to the specified requirements. Each test case should be executed in sequence to validate the script's behavior under different scenarios.