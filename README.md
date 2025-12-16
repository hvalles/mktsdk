# MKTSDK
MarketSync SDK for API Consume and software integration  
- Data is delivered by JSON and REST Calls, all those call are internally handled by SDK and converted into Python dictionaries

The main purpose of this projects is present an application that involves and consumes APIs from MarketSync, so you may understand some steps in order to integrate your own Legacy/ERP software with these APIs

You are going to need access to MarketSync platform in order to get your credentials for access and consume API Calls.

Please consult the next guide [https://github.com/hvalles/marketsync/blob/master/links/keys.md] for moren information about obtaining credentials for API Consume.

# AUTH
This module makes all signatures for calling each end point, you need access from MarketSync users, that would be used as the caller one.

# CONTROLLER
sdk.py it's the componente that contais all logic for calling rest operations  
each control contais it's own endpoint and if needed another functions for complementary data

# MODEL
All models are consistents with all structures expected by all REST Apis, when templates does not represent columns names for clarity, those columns are aliased with expected ones.

# PARSER
This module would transform answers from Rest APis into models, according to each column names, and mapping them.

# About example app
Example app is an GUI interface for upload MarketSync Templates about   
-- Product Master  
-- Product Price  
-- Stock  
-- Kits  

Application would create a data folder and will place inside it all errors, and data stored in database.  

Database in use is SQLITE3 and it's name is data/file.db.  

There is a file named data/markets.txt, and contais all marketplaces recognized for this app at the moment of this build.

Please do not alter header of templates, as they are needed for identify all columns, in the case of master product's template, you may download each file by Category of product as their attributes may vary among them.

# Module excelfile 
This module would process each row of template file and returns a model with all columns matched according modules's fields.

# Warning
Credentials are going to be stored in plain text inside a ".env" file, in the same folder as the exe file.

# How to install

Just clone or download project  

Open a windows command shell and change your current directory to cloned | unzipped one  

Create a environment in the corresponding folder  

- python -m venv venv  

Activate environment  

For Windows  
- venv\Scripts\activate 

For Linux, Mac  
- source venv/bin/activate 

Install required libraries  
- pip install -r freeze.txt

Run it  
- python app.py

Create standalone executable
pip install pyinstaller
pyinstaller --onefile app.py

# Related Projects
MarketSync API [https://github.com/hvalles/marketsync]  
Marketswync PlayGround [https://sandbox.marketsync.mx/playground/index]

# Platform
MarketSync Platform [https://web.marketsync.mx/]

# Templates 
MarketSync Templates [https://web.marketsync.mx/descargas]
