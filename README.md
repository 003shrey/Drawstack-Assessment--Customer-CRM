# SupportDesk CRM

A full-stack customer support ticketing CRM built for the Datastraw assessment.

## Features

- Create customer support tickets
- Automatically generate sequential ticket IDs such as `TKT-001`
- View all tickets
- Search tickets by customer name, ticket ID, email, or description
- Filter tickets by status
- View ticket details
- Update ticket status
- Add internal notes to ticket threads
- Mobile-responsive frontend
- Basic status dashboard showing Open, In Progress, and Closed counts

Authentication is intentionally out of scope for this MVP, as allowed by the assessment.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy ORM
- SQLite
- Jinja2 templates
- Tailwind CSS CDN
- Vanilla JavaScript
- Railway deployment

The application uses exactly two database tables: `tickets` and `notes`.

## Standout Feature

The standout feature is the basic statistics dashboard.

It shows the number of Open, In Progress, and Closed tickets at a glance, which is useful for a support team monitoring workload. The tradeoff is that the counts are calculated from the currently loaded ticket list rather than introducing a third analytics table or a more complex reporting system.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

On Windows, create `.env` manually from `.env.example`.

Start the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The SQLite database file `tickets.db` is created automatically on first startup.

## API Documentation

FastAPI automatically exposes interactive documentation at:

```text
/docs
```

### Create Ticket

```http
POST /api/tickets
Content-Type: application/json
```

Request:

```json
{
  "customer_name": "Asha Sharma",
  "customer_email": "asha@example.com",
  "subject": "Unable to access account",
  "description": "The password reset link is not working."
}
```

Response:

```json
{
  "ticket_id": "TKT-001",
  "created_at": "2026-09-11T12:00:00Z"
}
```

### List Tickets

```http
GET /api/tickets
```

Optional parameters:

```text
/api/tickets?status=Open
/api/tickets?search=asha
/api/tickets?status=Closed&search=TKT-001
```

Response:

```json
[
  {
    "ticket_id": "TKT-001",
    "customer_name": "Asha Sharma",
    "subject": "Unable to access account",
    "status": "Open",
    "created_at": "2026-09-11T12:00:00Z"
  }
]
```

Valid statuses:

```text
Open
In Progress
Closed
```

### Get Ticket Detail

```http
GET /api/tickets/TKT-001
```

Response:

```json
{
  "ticket_id": "TKT-001",
  "customer_name": "Asha Sharma",
  "customer_email": "asha@example.com",
  "subject": "Unable to access account",
  "description": "The password reset link is not working.",
  "status": "Open",
  "notes": []
}
```

### Update Ticket

```http
PUT /api/tickets/TKT-001
Content-Type: application/json
```

Request:

```json
{
  "status": "In Progress",
  "notes": "Support agent is investigating the password reset flow."
}
```

Both fields are optional individually, but at least one must be supplied.

Response:

```json
{
  "success": true,
  "updated_at": "2026-09-11T12:10:00Z"
}
```

## Error Handling

- `404`: Requested ticket does not exist
- `422`: Invalid request data, invalid status, or empty update
- Validation errors are returned as JSON with field-level details

## Railway Deployment

1. Push the project to GitHub.
2. Create a new project in Railway.
3. Choose **Deploy from GitHub repo**.
4. Select the repository.
5. Railway will install dependencies from `requirements.txt`.
6. The start command is configured in `railway.json` and `Procfile`.
7. Generate a public domain from the Railway service's Networking settings.
8. Add `DATABASE_URL` in Railway variables if you want to override the default SQLite location.

The production start command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For a persistent SQLite database on Railway, attach a Railway volume and point `DATABASE_URL` to a database path on that volume. Without persistent storage, the SQLite file may be lost when the service is redeployed.

## Production Notes

This is an intentionally simple assessment MVP. Before using it for a real support organization, I would add authentication, authorization, database migrations, automated tests, structured logging, rate limiting, backups, and persistent managed database storage.
