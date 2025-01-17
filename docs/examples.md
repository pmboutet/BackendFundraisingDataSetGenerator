# Fundraising Dataset Generator - Examples

## Configuration Examples

### Basic Configuration
```yaml
# Basic settings
YEARS: 5
FIRST_YEAR: 2020
INITIAL_DONOR_DATABASE_SIZE: 10000
GLOBAL_CHURN_RATE: 0.99
LOCALISATION: 'en_GB'
GDPR_PROOF: True

# Channel configuration
CHANNELS:
  Email:
    distribution: "exponential"
    duration: 5
    initial_nb: 10000
    campaigns:
      prospecting:
        nb: 3
        max_reach_contact: 50000
        transformation_rate: 0.005
        avg_donation: 20
        std_deviation: 15
```

### Sample API Requests

1. Obtain JWT Token:
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
     -H 'Content-Type: application/json' \
     -d '{"username": "your_username", "password": "your_password"}'```

2. Generate Dataset:
```bash
curl -X POST http://localhost:8000/api/generate/ \
     -H 'Authorization: Bearer your_jwt_token' \
     -F 'config_file=@path_to_your_config.yml'
```

### Sample Response
```json
{
  "transactions": [
    {
      "date": "2024-01-15T10:30:00Z",
      "campaign_start": "2024-01-01T00:00:00Z",
      "campaign_end": "2024-01-31T00:00:00Z",
      "channel": "Email",
      "campaign_name": "2024-15_Email_Climate_awareness",
      "campaign_type": "prospecting",
      "donation_amount": 50.0,
      "payment_method": "Credit Card",
      "cost": 0.5,
      "reactivity": 0.02,
      "contact_id": "ABC12345"
    }
  ],
  "contacts": [
    {
      "contact_id": "ABC12345",
      "salutation": "Mr.",
      "gender": "male",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "address_1": "123 Main St",
      "address_2": "Apt 4B",
      "zip_code": "12345",
      "city": "Sample City",
      "country": "Sample Country",
      "job": "Engineer",
      "origin_decile": 5,
      "Creation_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```
