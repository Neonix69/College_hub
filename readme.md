# College Hub

**College Hub** is a centralized web platform designed to help students
find, organize, upload, and download academic resources. It organizes
learning materials by course, academic year, semester, and subject,
making it easier to locate relevant exam resources.

-   **GitHub repository:** https://github.com/Neonix69/College_hub

## Overview

Academic resources are often scattered across group chats, folders, and
different websites. College Hub aims to bring these materials into one
structured platform so students can browse resources according to their
course and subjects.

The project is built with Django and includes user accounts, student
profiles, resource search, resource uploads and downloads, and an
administration interface.

## Key Features

-   **Organized academic structure:** Browse courses, academic years,
    semesters, and subjects.
-   **Academic resource library:** Store and access resources associated
    with subjects.
-   **Exam resource categories:** Resources can be classified as
    internal exams or semester exams, with optional labels such as
    Internal 1 or Internal 2.
-   **Search:** Search across the platform for relevant resources.
-   **Upload resources:** Users can upload academic materials for a
    subject.
-   **Download resources:** Download available files from resource
    pages.
-   **User accounts:** Sign-up, login, logout, and profile editing.
-   **Student profiles:** Profiles support details such as course,
    enrollment year, an "about me" section, and an optional avatar.
-   **Download tracking:** Resource records include a download counter.
-   **Administration:** Django's admin interface supports administrative
    management of the platform's data.

## Technology Stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Main programming language

  Django                              Web framework, routing,
                                      authentication, and data models

  HTML templates                      Server-rendered pages

  CSS                                 Website styling

  SQLite                              Local development database by
                                      default

  PostgreSQL                          Supported through the configured
                                      database URL for deployment

  Gunicorn                            Production WSGI application server

  WhiteNoise                          Serving static assets in deployment

  Render                              Deployment configuration is
                                      included in `render.yaml`
  -----------------------------------------------------------------------

## Project Structure

``` text
College_hub/
├── accounts_admin/   # Account and administration-related application
├── collegehub/       # Django project settings and URL configuration
├── resources/        # Academic resources, models, views, and routes
├── static/css/       # CSS assets
├── templates/        # HTML templates
├── manage.py         # Django management utility
├── requirements.txt  # Python dependencies
├── render.yaml       # Render deployment configuration
└── .gitignore        # Files excluded from version control
```

## Getting Started

### Requirements

-   Python 3.10 or a compatible Python version supported by the
    installed dependencies
-   pip
-   Git

### 1. Clone the repository

``` bash
git clone https://github.com/Neonix69/College_hub.git
cd College_hub
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

For local development, Django settings provide defaults. For deployment,
set a secure `SECRET_KEY`, set `DEBUG=False`, and configure
`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL` as
appropriate for your environment.

Do not commit production secrets or database credentials to Git.

### 5. Apply database migrations

``` bash
python manage.py migrate
```

### 6. Create an administrator account

``` bash
python manage.py createsuperuser
```

Follow the prompts to create the account.

### 7. Start the development server

``` bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Administration

The Django administration interface is available at:

``` text
/admin/
```

When running locally, visit `http://127.0.0.1:8000/admin/`. Sign in with
a Django staff/superuser account to access the admin interface. The
admin URL is not a substitute for authentication or appropriate
permissions.

## Deployment

A `render.yaml` file is included to describe a Render deployment. It
configures a Python web service, installs dependencies, collects static
files, applies database migrations, and starts Django through Gunicorn.
It also defines a PostgreSQL database configuration.

Before deploying:

1.  Review `render.yaml` and ensure the allowed host and CSRF trusted
    origin match the actual Render service URL.
2.  Keep `DEBUG=False` in production.
3.  Ensure `SECRET_KEY` is generated securely and never exposed
    publicly.
4.  Confirm the database plan and persistence requirements for your
    deployment.
5.  Decide how uploaded media files will be stored. Files saved to a web
    service's local filesystem may not persist across redeploys or
    restarts; use persistent storage or an external object-storage
    service for production uploads.
6.  Test account registration, login, resource uploads, downloads, and
    admin permissions after deployment.

## Academic Resource Organization

The project models academic content using a hierarchy:

**Course → Academic Year → Semester → Subject → Resource**

Resources can include an exam type, an optional exam label, a file,
notes, the uploader, upload time, and a year field. This structure is
intended to make exam papers and other study materials easier to find.

## Future Improvements

Possible directions for further development include:

-   Add pagination and more advanced search filters.
-   Add file type and file size validation for uploads.
-   Add clearer permission rules for who can upload, edit, or remove
    resources.
-   Add resource previews and improved mobile accessibility.
-   Add reporting or moderation for incorrect or inappropriate uploads.
-   Use persistent or object storage for uploaded files in production.
-   Add automated tests for authentication, permissions, search,
    uploads, and downloads.
-   Add backups and monitoring for production deployment.

## Contributing

Contributions and suggestions are welcome. To propose a change:

1.  Fork the repository.
2.  Create a feature branch.
3.  Make and test your changes.
4.  Open a pull request describing the improvement.

## License

No license is specified here. Check the repository for a license before
reusing or distributing the project's code.

------------------------------------------------------------------------

*College Hub --- bringing academic resources together in one organized
place.*
