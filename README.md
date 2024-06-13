# This is the homework README.md
## Install Requirements
```bash
pip install -r requirements.txt
```
## [db] part
This project provides a system to manage leads, including creating, reading, updating, and deleting lead records. It uses Python, asyncio, Beanie ODM, and MongoDB.
### Features
- Populate Data: Populate the database with sample data from a file (default is 'raw/leads.txt').
- Query Leads: Query leads based on various parameters.
- Update Leads: Update lead records by ID.
- Delete Leads: Delete lead records by ID.
### Requirements
- MongoDB up and running at `mongodb://localhost:27017`
- Python 3.8 or higher
### Usage
```bash
python db/lead_management.py --help

# Populate Database
python db/lead_management.py --populate
# or specify the file path if you have a different file
# python db/lead_management.py --populate --file_path <path_to_file> --error_file_path <path_to_error_file>

# Query Leads
python db/lead_management.py --query_params '{"academic_field": "Computer Science"}'

# Update Lead
python db/lead_management.py --update_lead_id <lead_id> --update_data '{"first_name": "Jane"}'

# Delete Lead
python db/lead_management.py --delete_lead_id <lead_id>
```
## [csv] part
This project processes academic field data, filling missing fields using keyword matching, MinHash, and Wikipedia matching.
### Features
- Get Academic Fields from wikipedia https://en.wikipedia.org/wiki/List_of_academic_fields.
- Clean Data: Removes punctuation, digits, and extra spaces from text.
- Fill Missing Fields: Uses different levels of processing to fill missing academic fields.
- Generate Report: Outputs a report of the filling process (report.txt).
- Update CSV: Updates the cleaned CSV file with new tuple values.

### Usage
```bash
# Get Academic Fields from Wikipedia
python csv/wiki_scrape.py

# CSV Processing
python csv/fill_csv.py --help
python csv/fill_csv.py raw/field_of_study_exercise.csv --level 3 --debug
# --level: Level of processing (1: Keyword, 2: Keyword & MinHash, 3: Keyword & MinHash & Wikipedia Keyword).
# --debug: Save intermediate files for debugging.

# Update cleaned CSV
python csv/update_csv.py "BA in Computer Science" "computer science"
```
## [api] part
This project extracts LinkedIn data into an S3 bucket.
### Features
- Extract Data: Fetches data from a mock LinkedIn API response.
- Transform Data: Processes and structures the data (get field of study and company name, size)
- Load Data: Writes the transformed data to an S3 bucket (Used AWS S3 due to its scalability, durability, and cost-effectiveness)
- Retrieve Data: Reads the data back from the S3 bucket.
### Requirements
- AWS credentials set up in `~/.aws/credentials`
- S3 bucket access.
### Usage
```bash
python api/mock.py example@example.com
```