Important folders and files:
SSA_agent - contains all the files for this project, anything outside of this is mainly just fairllm code
    SSA_agent.py - code for the main agent. loops through sources in the database, analyzes them, and puts all pairs into the pair database.
    ac_pair_storage_tool.py - fairLLM tool which the agent calls upon to input pairs into the database. Has a list of current accepted actors and concepts which need to reflect the actors and concepts currently in the database.
    translation.py - contains translate() function called in SSA_agent.py when the source is marked with chinese. Uses a local model trained on chinese to english translation.
SSA_agent/concept_db - contains all database files and supporting files
    pair.db - default name for the sql database containing sources, actors, concepts, and pairs
    schema.sql - schema for the database, used to initialize
    init_db.py - initializes the database, should be able to be called twice without breaking an existing database
    coocurrence.py - creates a two mode coocurrence matrix from the pairs stored in the database. 
    coocurrence.csv - output from coocurrence.py, can be fed into visone for graphing
SSA_agent/source_collection - it's what it sounds lie, contains the code to collect sources from online and input them into the database
    source_collection.py - the main source collection code.
    rss_collection.py - depricated



SSA workflow:

1. Ensure you have a database file created, pair.db is the default name. Running cencept_db/init_db.py will create a database set up with some preselected actors and concepts which can be changed by editing the concept_db/schema.sql file. 

2. populate your database with sources. Source collection is automated using the source_collection/source_collection.py script, which populates the pair.db by default, database filepath can be changed with the global at the top of the file.

3. Run the agent "SSA_agent.py" to gather actor-concept pairings. The agent defaults to gpt 4.1 using the openai api. An API key needs to be added to the .env file in the project root directory. The LLM can be changed by changing the LLM using FairLLM adapters. Pairs are also stored in the database, and are tagged with the source they came from.

4. graph output. Right now the code is set up for Visone, which is a standalone java executable found from stca.guide. A two mode adjacency matrix can be built using the concept_db/coocurrence.py file. The actor and concept lists in that file must match the actor and concept lists represented in the database. 