# Data Downloads

## Overview

When generating datasets through the API, the service automatically packages the generated data into a ZIP file for convenient downloading. This document explains the structure and contents of the downloaded data.

## File Structure

The downloaded ZIP file contains two CSV files:

1. `transactions_YYYYMMDD_HHMMSS.csv` - Contains all transaction records
2. `contacts_YYYYMMDD_HHMMSS.csv` - Contains all contact/donor information

The timestamp in the filenames helps track when the data was generated.

## Downloading Methods

### Browser Download

When accessing the API through a web browser:
1. Make a POST request to `/api/generate/`
2. Provide your JWT token and configuration file
3. The browser will automatically initiate the download of the ZIP file

### Command Line Download

Using curl:
```bash
curl -X POST http://localhost:8000/api/generate/ \
     -H 'Authorization: Bearer your_jwt_token' \
     -F 'config_file=@your_config.yml' \
     --output fundraising_data.zip
```

## File Contents

### Transactions CSV

Contains the following columns:
- date: Transaction date
- campaign_start: Campaign start date
- campaign_end: Campaign end date
- channel: Communication channel
- campaign_name: Unique campaign identifier
- campaign_type: Type of campaign
- donation_amount: Amount donated
- cost: Campaign cost per contact
- reactivity: Response rate metric
- contact_id: Unique donor identifier
- payment_method: Method of payment
- amount_decile: Donation amount percentile

### Contacts CSV

Contains the following columns:
- contact_id: Unique donor identifier
- salutation: Formal title
- gender: Donor's gender
- first_name: First name
- last_name: Last name
- phone: Contact phone number
- address_1: Primary address
- address_2: Secondary address (optional)
- zip_code: Postal code
- city: City name
- country: Country name
- job: Occupation
- origin_decile: Initial donation percentile
- Creation_date: First donation date
- Creation_year: Year of first donation

## Technical Details

- File Format: ZIP (using DEFLATE compression)
- CSV Encoding: UTF-8
- File Naming: Includes timestamp for unique identification
- Content-Type: application/zip
- Download Trigger: Content-Disposition header set to 'attachment'

## Error Handling

In case of errors:
- Invalid YAML configuration: Returns 400 Bad Request with error details
- Authentication failure: Returns 401 Unauthorized
- Server errors: Returns 500 Internal Server Error with error message

## Best Practices

1. Always verify the timestamp in filenames matches your generation request
2. Extract both CSV files before processing the data
3. Maintain the relationship between transactions and contacts using contact_id
4. Consider backing up the ZIP files as they contain the original timestamp information