# Backend Fundraising Dataset Generator

A Django REST Framework service for generating synthetic fundraising datasets based on YAML configurations. This service allows you to generate realistic fundraising data for testing, development, and demonstration purposes.

## Quick Start

1. Install the package:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

2. Set up the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Run the server:
```bash
python manage.py runserver
```

4. Access the API documentation at:
- http://localhost:8000/api/docs/ (Swagger UI)
- http://localhost:8000/api/redoc/ (ReDoc)

## Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration Guide](docs/configuration.md) - YAML configuration reference
- [Examples](docs/examples.md) - Sample configurations and API usage
- [OpenAPI Specification](docs/openapi.yml) - Full API specification

## Features

### Data Generation
- Multiple fundraising channels (Email, Face2Face, Print, etc.)
- Realistic donor profiles with demographic data
- Configurable campaign parameters
- Cross-channel donor relationships
- Time-based data distribution patterns

### Customization Options
- Channel-specific settings
- Campaign themes and targeting
- Payment method distribution
- Demographic settings
- GDPR compliance options

### API Features
- RESTful endpoints
- JWT authentication
- Detailed API documentation
- File upload support
- Comprehensive response data

## API Endpoints

### Authentication
- `POST /auth/jwt/create/` - Obtain JWT token
- `POST /auth/jwt/refresh/` - Refresh JWT token
- `POST /auth/users/` - Register new user

### Data Generation
- `POST /api/generate/` - Generate fundraising dataset

## Configuration Example

```yaml
# Basic Configuration
YEARS: 5
FIRST_YEAR: 2020
INITIAL_DONOR_DATABASE_SIZE: 10000
GLOBAL_CHURN_RATE: 0.99

# Channel Example
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

## Sample API Usage

1. Obtain JWT token:
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
     -H 'Content-Type: application/json' \
     -d '{"username": "your_username", "password": "your_password"}'```

2. Generate dataset:
```bash
curl -X POST http://localhost:8000/api/generate/ \
     -H 'Authorization: Bearer your_jwt_token' \
     -F 'config_file=@your_config.yml'
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
flake8 .
pylint fundraising_generator
```

## Deployment

### Heroku
```bash
heroku create
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Docker
```bash
docker build -t fundraising-generator .
docker run -p 8000:8000 fundraising-generator
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Rest Framework for the powerful API framework
- Faker library for generating realistic data
- All contributors who have helped shape this project