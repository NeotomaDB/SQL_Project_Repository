# Working with the Python Data Upload Template

This set of python scripts is intended to support the bulk upload of a set of records to Neotoma. It consists of two steps,
the initial validation of records, and then the subsequent upload.

The upload set assumes that _all errors have been corrected_ and that files remain unchanged (based on the hashing function applied to the records).

## Validation

We execute the validation process by running:

```bash
> python3 template_validate.py FILEFOLDER
```

This will then search the folder for csv files with the appropriate format and parse them for validity.

Issues that will result in a failing upload:

* Units
* Invalid column names
* Invalid geographic units

Issues that return warnings, but will result in new elements being added to the database:

* Sites
* Collection Units
* Contacts
* Publications

Each file will recieve a `log` file associated with it that contains a report of potential issues.

The log files begin with an md5 hash of the csv template file. This appears as a string of numbers and letters that record a point in time of the file. The hash is used to identify whether or not files have changed since validation.

The validation step identifies each element of the template being validated, provides a visual reference as to whether or not the element passes validation (**✔**, **?** or **✗**) and provides guidance as to whether changes need to be made.

## Upload

The upload process is initiated using the command:

```bash
> python3 template_upload.py
```

The upload process will return the distince siteids, and related data identifiers for the uploads.
