# FLASK CRUD

Simple CRUD RESTFul API made with FLask and SQLAlchemy.

## Previous requirements
1. Python 3.6 or newer versions.

## Running
1. Clone:
```bash
  git clone https://github.com/ggmorais/flask-crud
  cd flask-crud
```
2. Install requirements:
```bash
  pip install -r requirements.txt
```

3. Edit environment variables at _.env.example_ and then rename to _.env_

3. Create database:
```bash
  python -c "from app.main import db; db.create_all()"
```

4. Run
```
  python app/main.py
```
