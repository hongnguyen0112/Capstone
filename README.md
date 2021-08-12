NOTE: Keep all terminals open to maintain all operations. Open a new terminal for other activities.

1. Required resources: Python (3.6 -> 3.8), Java 11+, Rasa, TypeDB

2. Run TypeDB server:
   - Open the terminal  
   - Navigate to directory where Typedb is located
   - Start server
   ```
   ./typedb server
    ```

3. Create new database:
   - Open new terminal
   - Navigate to directory where Typedb is located
   - Start console
   ```
   ./typedb console
   ```
   - Create a new database ("local" is database name)
   ```
   database create local
   ```
   

4. Load schema to the database:  
In your Typedb Console terminal, use the following commands
   - Start a new schema transaction 
     ```commandline
     transaction local schema write
     ```
   - Load schema from tql file
     ```commandline
     source ./path/schema/file.tql
     ```  
   - commit
     ```commandline
     commit  
     ```  

5. Load the data to your local database:
   - Open a new terminal
   - Navigate to knowledge_base folder
   - Migrate data to the server
     ```commandline
     python migrate.py
     ```
   

7. Run rasa server
   - Open the new terminal
     ```commandline
     rasa run actions
     ```

8. Run rasa in shell mode
   - Open new terminal
      ```commandline
      rasa shell
      ```