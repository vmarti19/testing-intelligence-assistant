# Test Plan for Simple Database Manager

## Overview
This test plan outlines the test cases for the `simple_database.py` script, which implements a simple database manager using a JSON file. The script supports creating, reading, updating, and deleting records in a table.

## Test Cases

### 1. Create a New Table
**Command:**
```bash
python simple_database.py create UsersTable name age
```
**Expected JSON Content:**
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
**Expected Output:**
- The JSON file should be created with the specified table and columns.
- The `rows` array should be empty.

### 2. Read All Records from an Empty Table
**Command:**
```bash
python simple_database.py read UsersTable
```
**Expected Output:**
```
UsersTable
---------
|  ID  |  name | age |
|------|-------|-----|
```
**Expected JSON Content:**
- The JSON file should remain unchanged.

### 3. Add a New Record
**Command:**
```bash
python simple_database.py add UsersTable name=John age=30
```
**Expected JSON Content:**
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
**Expected Output:**
- The JSON file should be updated with the new record.
- The `<id>` should be 1.

### 4. Read All Records After Adding a Record
**Command:**
```bash
python simple_database.py read UsersTable
```
**Expected Output:**
```
UsersTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | John   | 30    |
```
**Expected JSON Content:**
- The JSON file should remain unchanged.

### 5. Add Another Record
**Command:**
```bash
python simple_database.py add UsersTable name=Alice age=25
```
**Expected JSON Content:**
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
**Expected Output:**
- The JSON file should be updated with the new record.
- The `<id>` should be 2.

### 6. Update an Existing Record
**Command:**
```bash
python simple_database.py update UsersTable 1 age=35
```
**Expected JSON Content:**
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
**Expected Output:**
- The JSON file should be updated with the new value for the specified record.

### 7. Read All Records After Updating a Record
**Command:**
```bash
python simple_database.py read UsersTable
```
**Expected Output:**
```
UsersTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 1    | John   | 35    |
| 2    | Alice  | 25    |
```
**Expected JSON Content:**
- The JSON file should remain unchanged.

### 8. Delete a Record
**Command:**
```bash
python simple_database.py delete UsersTable 1
```
**Expected JSON Content:**
```json
{
  "UsersTable": {
    "columns": [
      "name",
      "age"
    ],
    "rows": [
      {
        "<id>": 2,
        "name": "Alice",
        "age": "25"
      }
    ]
  }
}
```
**Expected Output:**
- The JSON file should be updated with the specified record removed.

### 9. Read All Records After Deleting a Record
**Command:**
```bash
python simple_database.py read UsersTable
```
**Expected Output:**
```
UsersTable
---------
|  ID  |  name  |  age  |
|------|--------|-------|
| 2    | Alice  | 25    |
```
**Expected JSON Content:**
- The JSON file should remain unchanged.

## Conclusion
This test plan covers all the required features of the `simple_database.py` script. Each test case is designed to verify the correct behavior of the script under different scenarios.