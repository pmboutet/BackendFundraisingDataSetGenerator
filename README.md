# Backend Fundraising Dataset Generator

## Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

## Deployment to Heroku

1. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set DEBUG=False
```

2. Deploy:
```bash
git push heroku main
```
