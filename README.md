# CW Template

Build using Flask, see https://flask.palletsprojects.com/en/2.2.x/

## Build Instruction

  1. (Optional) Create a new virtual env
     ```python -m venv env```

	 Remember to activate the Env when you go to use it
	 
	 ```
	 source env/bin/activate
	 ```
     
  2. Install Requirements
  
     ```
	 pip install -r REQUIREMENTS.txt
	 ```
	
  3. Run
  
     ```
	 flask --app app/ --debug run
	 ```

The site should now be visible on 127.0.0.1:5000

## Inital DB

Database Schema can be found in ```schema.db```

You can initialise a testing db by visiting ```127.0.0.1:5000/initdb```



	 

## Files

Some Supporting files

  - schema.sql
  
    Basic database schema to get you started
	
	You can build this by visiting the ```/initdb``` url

