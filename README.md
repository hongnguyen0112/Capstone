1. Required resources:
Python
Java 11+
Rasa
TypeDB

2. Run TypeDB server
open the terminal
cd to typedb folder
./typedb server
NOTE: Don't close the terminal for further step, if not, it will turn off the server

3. Create new database
open new terminal
cd to typedb
./typedb console
database create local 

3. Load schema to the database
from your typedb console terminal
transaction local schema write
source 'path to the schema' (.tql) file
commit

4. Load the data to your local database
cd to knowledge_base
python migrate.py

5. Run rasa server
open the new terminal
rasa run actions

6. Run rasa console
open new ter
