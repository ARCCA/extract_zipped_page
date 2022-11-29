# extract_zipped_page
For a project we needed to extract files from Zip without extracting all the files.

# Setup

```bash
$ python -m pip install -r requirements.txt
```

# Running

```bash
$ python zip_code.py
```

# Configuration

The file was just a quick test so currently need to modify the bottom of the script, sftp functionality (to copy files to a remote server) can be set to ```None``` and it will be stored locally.  Currently is loops through a csv file with a column called id and it looks for starting id so it doesnt process it from the beginning all the time.
