# Backend Fundraising Dataset Generator

A Django REST Framework service for generating synthetic fundraising datasets based on YAML configurations. This service allows you to generate realistic fundraising data for testing, development, and demonstration purposes.

## Features

- Generate synthetic fundraising transactions
- Create realistic donor profiles
- Support for multiple fundraising channels
- Configurable campaign parameters
- JWT Authentication
- OpenAPI/Swagger documentation

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/pmboutet/BackendFundraisingDataSetGenerator.git
cd BackendFundraisingDataSetGenerator
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows:
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (for admin access):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

## Basic Usage

1. Access the API documentation:
   - Swagger UI: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

2. Obtain JWT Token:
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
     -H 'Content-Type: application/json' \
     -d '{"username": "your_username", "password": "your_password"}'
```

3. Generate Dataset:
```bash
curl -X POST http://localhost:8000/api/generate/ \
     -H 'Authorization: Bearer your_jwt_token' \
     -H 'Content-Type: multipart/form-data' \
     -F 'config_file=@path_to_your_config.yml'
```

## Configuration File Example

```yaml
# Basic Configuration
YEARS: 11
FIRST_YEAR: 2014
INITIAL_DONOR_DATABASE_SIZE: 10000
GLOBAL_CHURN_RATE: 0.99
LOCALISATION: 'en_GB'
GDPR_PROOF: True

# Channel Example: Email
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
      retention:
        nb: 12
        transformation_rate: 0.02
        avg_donation: 30
        std_deviation: 10
        cross_sell:
          - ['Email', 100]
          - ['Print', 40]
    target:
      ses_wealth_decile: [1, 8]
    payment:
      Credit/Debit Card: 65
      PayPal: 10
      Mobile Payment App: 10
      Direct Debit: 10
      Cheque: 3
      Bank Transfer: 1
    cost_per_reach: 0.05
```

## API Endpoints

- `/api/generate/` - Generate fundraising dataset
- `/auth/jwt/create/` - Obtain JWT token
- `/auth/jwt/refresh/` - Refresh JWT token
- `/auth/users/` - User registration
- `/api/docs/` - Swagger documentation
- `/api/redoc/` - ReDoc documentation

## Response Format

The API returns data in the following format:
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
            "job": "Engineer"
        }
    ]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
