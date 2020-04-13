# Spectrum to Discourse Migration

If you're looking for help migrating your Spectrum data into Discourse, look no further.

## Setup and installation

These scripts are just a bunch of Python files configured to run from the command line and take CSV files as arguments. We've included a `virtualenv` with all of the dependencies pre-installed. If you want to install them yourself, you'll need:

- Python 3+
- `pandas`
- `requests`

The rest of the libraries we're using (`json`, `sys`, `time`) should all be included with Python by default. 

To run files, activate the virtualenv with `source bin/activate` and then run `python file_name arguments`.

> The `utils.py` file is where your Discourse API Key sits. You'll need to replace `YOUR_API_TOKEN` with, well, your API token.

## Organization

There are three (3) key migration scripts (`migrate_*.py`), two (2) utilities (`delete_topics.py` and `utils.py`), and four (4) CSVs (`spectrum_messages.csv`, `spectrum_threads.csv`, `spectrum_users.csv`, `topic_mappings.csv`). 

### Migration

##### 1) `migrate_users.py`

Takes one argument - a CSV of Spectrum users - and creates a user in Discourse with the same email and username as Spectrum. Make sure to update line 46 to be whatever password you want it to be. Example usage: `python migrate_users.py spectrum_users_sample.csv`

##### 2) `migrate_topics.py`

Takes three arguments:

- A CSV of Spectrum threads
- A CSV of Spectrum users
- A CSV of topic mappings

Make sure to update the `channel_mappings` (line 22) to match what your Spectrum community's channel mappings are. Sample usage: `python migrate_topics.py spectrum_threads_sample.csv spectrum_users_sample.csv topic_mappings_sample.csv`

##### 3) `migrate_posts.py`

Takes three arguments:

- A CSV of Spectrum messages
- A CSV of Spectrum users
- A CSV of topic mappings

Sample usage: `python migrate_posts.py spectrum_messages_sample.csv spectrum_users_sample.csv topic_mappings_sample.csv`

### Utilities

##### 1) `delete_topics.py`

Deletes topics if you need to redo any part of the migration. Takes two arguments:

- Deletion start: the `topic_id` that you want to start deleting at (inclusive)
- Deletion end: the `topic_id` that you want to end deleting at (inclusive)

Sample usage: `python delete_topics.py 1123 1156`

##### 2) `utils.py`

Contains some utility functions, the Markdown parser, and a place to store your Discourse API key. This file is not executable.

### Data

Sample data that your Spectrum data should follow the format of:

- `spectrum_users_sample.csv` - Spectrum user data
- `spectrum_threads_sample.csv` – Spectrum thread data (maps to a Discourse topic)
- `spectrum_messages_sample.csv` – Spectrum message data (maps to a Discourse post)
- `topic_mappings_sample.csv` – Sample data for mapping Spectru, threads to Discourse `topic_id`s

## How to use this

General guidelines / steps:

1) Download all of your Spectrum data (the tables called `users`, `threads`, and `messages`)
2) Create an empty `topic_mappings.csv` file or use the sample one included
3) Put your Discourse API key into `utils.py` and choose a temporary user password in `migrate_users.py`
4) Run the users migration
5) Run the topics migration
6) Run the posts migration

MIT licensed.
