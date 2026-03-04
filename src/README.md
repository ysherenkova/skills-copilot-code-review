# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- View active announcements on the homepage
- Manage announcements (add, edit, delete) for signed-in staff

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get currently active announcements                                  |
| GET    | `/announcements/manage?teacher_username={username}`              | Get all announcements for management (authenticated)                |
| POST   | `/announcements?message=...&end_date=YYYY-MM-DD&teacher_username={username}` | Create a new announcement (authenticated)               |
| PUT    | `/announcements/{announcement_id}?message=...&end_date=YYYY-MM-DD&teacher_username={username}` | Update an announcement (authenticated) |
| DELETE | `/announcements/{announcement_id}?teacher_username={username}`    | Delete an announcement (authenticated)                              |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Announcements** - Uses announcement id as identifier:

   - Message text
   - Optional start date (`YYYY-MM-DD`)
   - Required expiration date (`YYYY-MM-DD`)

Data is stored in MongoDB. Example data is initialized from `src/backend/database.py` when collections are empty.
