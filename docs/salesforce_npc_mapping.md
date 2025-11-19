# Salesforce Non-Profit Cloud Column Mapping

This document describes how internal column names are mapped to Salesforce Non-Profit Cloud (NPC) format using the `object_name::field_name` convention.

## Mapping Format

All exported CSV files now use Salesforce NPC naming convention: `ObjectName::FieldName`

- Standard Salesforce fields use standard names (e.g., `Contact::FirstName`)
- Custom fields use `__c` suffix (e.g., `Contact::Gender__c`)
- Summary/Rollup fields are prefixed with the related object (e.g., `Gift_Transaction__c::Total_Gifts__c`)

## Contact Object Fields

| Internal Column | Salesforce NPC Field | Description |
|----------------|---------------------|-------------|
| `contact_id` | `Contact::Id` | Unique contact identifier |
| `salutation` | `Contact::Salutation` | Formal title (Mr., Mrs., etc.) |
| `gender` | `Contact::Gender__c` | Gender (custom field) |
| `first_name` | `Contact::FirstName` | First name |
| `last_name` | `Contact::LastName` | Last name |
| `phone` | `Contact::Phone` | Phone number |
| `address_1` | `Contact::MailingStreet` | Primary address |
| `address_2` | `Contact::MailingStreet2__c` | Secondary address (custom) |
| `zip_code` | `Contact::MailingPostalCode` | Postal/ZIP code |
| `city` | `Contact::MailingCity` | City name |
| `country` | `Contact::MailingCountry` | Country name |
| `job` | `Contact::Title` | Occupation/Job title |
| `origin_decile` | `Contact::Wealth_Decile__c` | Wealth decile based on first donation (custom) |
| `Creation_date` | `Contact::CreatedDate` | Contact creation date |
| `Creation_year` | `Contact::Created_Year__c` | Creation year (custom) |
| `longevity_years` | `Contact::Donor_Tenure_Years__c` | Donor longevity in years (custom) |
| `job_category` | `Contact::Job_Category__c` | Job category (Wealthy/Non-Wealthy) (custom) |
| `wealth_category` | `Contact::Wealth_Category__c` | Wealth category (Low/Medium/High) (custom) |
| `longevity_category` | `Contact::Longevity_Category__c` | Longevity category (custom) |
| `combined_category` | `Contact::Donor_Segment__c` | Combined donor segment (custom) |

## Gift Transaction Summary Fields

These are rollup/summary fields calculated from individual gift transactions:

| Internal Column | Salesforce NPC Field | Description |
|----------------|---------------------|-------------|
| `nb_donations` | `Gift_Transaction__c::Total_Gifts__c` | Total number of donations (rollup) |
| `total_donated` | `Gift_Transaction__c::Total_Amount__c` | Total amount donated (rollup) |
| `avg_donation` | `Gift_Transaction__c::Average_Gift_Amount__c` | Average donation amount (rollup) |
| `first_donation` | `Gift_Transaction__c::First_Gift_Date__c` | Date of first donation (rollup) |
| `primary_channel` | `Gift_Transaction__c::Primary_Channel__c` | Primary communication channel (rollup) |
| `is_regular` | `Gift_Transaction__c::Is_Regular_Donor__c` | Regular donor flag (≥3 donations) (rollup) |
| `channel_type` | `Gift_Transaction__c::Channel_Type__c` | Channel type (Digital/Non-Digital) (custom) |

## Gift Transaction (Individual Transaction) Fields

| Internal Column | Salesforce NPC Field | Description |
|----------------|---------------------|-------------|
| `date` | `Gift_Transaction__c::Transaction_Date__c` | Transaction date |
| `campaign_start` | `Campaign::StartDate` | Campaign start date |
| `campaign_end` | `Campaign::EndDate` | Campaign end date |
| `channel` | `Gift_Transaction__c::Channel__c` | Communication channel |
| `campaign_name` | `Campaign::Name` | Campaign name |
| `campaign_type` | `Campaign::Type` | Campaign type (prospecting/retention) |
| `donation_amount` | `Gift_Transaction__c::Amount__c` | Donation amount |
| `cost` | `Campaign::Cost_Per_Contact__c` | Campaign cost per contact (custom) |
| `reactivity` | `Campaign::Response_Rate__c` | Response rate metric (custom) |
| `contact_id` | `Contact::Id` | Related contact ID |
| `payment_method` | `Gift_Transaction__c::Payment_Method__c` | Payment method (custom) |
| `amount_decile` | `Gift_Transaction__c::Amount_Decile__c` | Donation amount decile (custom) |

## File Naming Convention

Exported files follow Salesforce NPC naming:

- **Contact data**: `Contact_YYYYMMDD_HHMMSS.csv`
- **Gift Transaction data**: `Gift_Transaction_YYYYMMDD_HHMMSS.csv`
- **Analysis data**: `complex_analysis_data_salesforce.csv`

Original format files are also included for backward compatibility:
- `contacts_YYYYMMDD_HHMMSS.csv`
- `transactions_YYYYMMDD_HHMMSS.csv`
- `complex_analysis_data.csv`

## Usage

The Salesforce mapping is automatically applied when:

1. **Generating data via API**: `/api/generate/` endpoint
2. **Generating demo data**: `generate_demo_data_en.py` or `generate_demo_data.py`
3. **Running analysis**: `demo_analysis_en.py` or `demo_analysis.py`

All exports include both Salesforce NPC format and original format files for compatibility.

## Custom Fields

Fields marked with `__c` are custom fields that would need to be created in your Salesforce Non-Profit Cloud org:

- `Contact::Gender__c`
- `Contact::MailingStreet2__c`
- `Contact::Wealth_Decile__c`
- `Contact::Created_Year__c`
- `Contact::Donor_Tenure_Years__c`
- `Contact::Job_Category__c`
- `Contact::Wealth_Category__c`
- `Contact::Longevity_Category__c`
- `Contact::Donor_Segment__c`
- `Gift_Transaction__c::Channel__c`
- `Gift_Transaction__c::Payment_Method__c`
- `Gift_Transaction__c::Amount_Decile__c`
- `Gift_Transaction__c::Total_Gifts__c` (rollup)
- `Gift_Transaction__c::Total_Amount__c` (rollup)
- `Gift_Transaction__c::Average_Gift_Amount__c` (rollup)
- `Gift_Transaction__c::First_Gift_Date__c` (rollup)
- `Gift_Transaction__c::Primary_Channel__c` (rollup)
- `Gift_Transaction__c::Is_Regular_Donor__c` (rollup)
- `Gift_Transaction__c::Channel_Type__c`
- `Campaign::Cost_Per_Contact__c`
- `Campaign::Response_Rate__c`

## Importing to Salesforce

To import these CSV files into Salesforce Non-Profit Cloud:

1. Ensure all custom fields exist in your org (create them if needed)
2. Use Data Import Wizard or Data Loader
3. Map columns using the `object_name::field_name` format
4. For rollup fields, you may need to use Process Builder, Flow, or Apex triggers to calculate them

## Notes

- The `::` separator is used to clearly indicate object and field relationships
- Standard Salesforce fields don't require `__c` suffix
- Custom fields require `__c` suffix per Salesforce conventions
- Rollup fields are prefixed with the object they summarize (e.g., `Gift_Transaction__c::`)



