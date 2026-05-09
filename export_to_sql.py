import sqlite3

# Connect to the correct SQLite database located in the instance folder
con = sqlite3.connect('instance/database.db')

# Open a new file to save the SQL dump
with open('database_dump.sql', 'w') as f:
    # Iterate over the dump and write it to the file
    for line in con.iterdump():
        f.write('%s\n' % line)

print("Successfully exported 'database.db' to 'database_dump.sql'. You can now open this file in any text editor!")
