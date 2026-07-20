# SCEM Render Deployment

This project is ready to deploy to Render as a Python web service.

## Render settings

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Environment Variable: `SECRET_KEY`

## Important note about data

This project currently uses:

- `scem.db` for SQLite data
- `static/uploads`, `static/cv`, and `static/audio` for uploaded files

Render web services use an ephemeral filesystem by default. This means any admin edits or uploaded files can be lost after a restart or redeploy unless you attach a persistent disk or move the project to a managed database/object storage setup.
