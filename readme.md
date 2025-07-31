# Dagster UI Custom Authentication (LDAP + DB Users)

This project enhances the open-source [Dagster](https://dagster.io/) data orchestrator with a **custom authentication system** supporting **dual login mechanisms**
- LDAP login (for internal users)
- PostgreSQL-based user login (for external users)
## Features

- Dual-mode authentication: LDAP & PostgreSQL users
- Web interface built using Starlette
- PostgreSQL-backed user store
- Session management using Starlette-Login
- Plug-and-play replacement for default Dagster UI server
---
## Local Development Setup

To set up the Dagster project for local development and enable custom authentication logic, follow the steps below:
### Tools & Prerequisites

Ensure the following tools are installed on your system:

- [Git Bash](https://git-scm.com/downloads) – Terminal interface for command execution (especially on Windows)
- [Miniconda/Anaconda](https://docs.conda.io/en/latest/miniconda.html) – For managing Python environments
- [Node.js (LTS)](https://nodejs.org/) – Required for building Dagster's frontend
- [Yarn](https://yarnpkg.com/) – JavaScript package manager used with Node.js

### Step-by-Step Setup

1. **Clone the Dagster Repository**
   ```
   git clone https://github.com/dagster-io/dagster.git
   cd dagster
2. **Create and Activate a Python Environment**
    Using Conda:
    ```
    conda create --name dagster_env python=3.12
    source .venv/Scripts/activate
    conda activate dagster_env
    ```
3. **Install Node.js and Yarn**
    Download and install Node.js from the official website
4. **Install Yarn**
    From the root of the Dagster repository:

        yarn install

5. **Install Dagster for Development**
    Run the following command to install all necessary Python packages and dependencies:
    
        make dev_install
---

## Code Implementation Details

This project involved direct modifications to the Dagster open-source codebase to enable dual-mode authentication (LDAP + PostgreSQL users). The changes span across both the Python backend and the React-based Dagster UI frontend.

---

### Backend Modifications – `dagster-webserver`

> Located in: `dagster-master/python_modules/dagster-webserver/dagster_webserver/`

- **`ldap_auth.py`**
  - Implements connection and authentication logic for LDAP users using `ldap3`.
  - Validates user credentials against the configured LDAP directory.

- **`db_auth.py`**
  - Handles PostgreSQL integration for external (non-LDAP) users.
  - Manages user signup, password hashing using `passlib`, and login validation.

- **`webserver.py`**
  - Extended with custom **routes** for:
    - `/login` – Login page rendering and authentication logic
    - `/signup` – External user registration
    - `/logout` – Clears session and redirects to login
  - Enforces **authentication as a prerequisite** for accessing the Dagster UI dashboard.

- **`graphql.py`**
  - Added static user credential logic to support the authenticated session during UI usage.

---

### Frontend Enhancements – `dagster-ui`

#### User Profile Dropdown

> File: `dagster-master/js_modules/dagster-ui/packages/ui-core/src/app/profile/UserProfileDropdown.tsx`

- Introduced a new **`UserProfileDropdown`** component to display:
  - My Profile (currently inactive)
  - Logout button
- Helps reflect authentication state on the Dagster UI top navigation bar.

#### Application Entry

> File: `dagster-master/js_modules/dagster-ui/packages/app-oss/src/App.tsx`

- Imported and rendered the new `UserProfileDropdown` component just after the `AppTopNav` component for better visibility of login context.

#### Build the UI Component
To compile the Dagster UI frontend, navigate to the `js_modules` directory 
    
    yarn build
---

### HTML Templates

> Directory: `dagster-master/python_modules/dagster-webserver/dagster_webserver/webapp/build/`
- **`login.html`**
  - Custom login form for both LDAP and external users.
  - Handles error messaging and form submission.

- **`signup.html`**
  - External users can register by creating new accounts.
  - Passwords are hashed before being stored in PostgreSQL.

---

## Deployment

After applying code changes, follow these steps to deploy the updated Dagster webserver:

1. **Build the Wheel Package**
   Navigate to the `dagster-webserver` directory and run:
   
        cd dagster-master/python_modules/dagster-webserver
        python -m build
    This will generate a .whl file inside the dist/ folder.

2. **Dockerfile**

        FROM python:3.12-slim
        RUN pip install --upgrade pip
        COPY dagster_webserver-1.11.2-py3-none-any.whl .
        RUN pip install --no-cache-dir dagster dagster-graphql dagster-postgres dagster-docker Starlette-Login ldap3
        RUN pip install --no-cache-dir passlib[bcrypt] psycopg2-binary
        RUN pip install dagster_webserver-1.11.2-py3-none-any.whl
        ENV DAGSTER_HOME=/opt/dagster/dagster_home/
        RUN mkdir -p $DAGSTER_HOME
        COPY dagster.yaml workspace.yaml $DAGSTER_HOME
        WORKDIR $DAGSTER_HOME

3. **Build the Docker Image**
    Use the generated wheel file to build the custom Docker image:
    
        docker build -t dagster-webserver-auth .
4. **Run with Docker Compose**
    Make sure your docker-compose.yml uses the new image and then start the services:
    
        docker-compose up

These changes result in a secure, user-friendly login system integrated directly into the Dagster OSS architecture—without requiring enterprise-level add-ons.


