# Moringa Pathway Backend Built with Flask

#### By **Abdul Aljawaab & Emmanuel Okoth**

## Description

The **Moringa Pathway Backend** is a web application designed to manage job postings, user profiles, payments, and resources for a platform that connects job seekers with employers. The system includes features for adding jobs, managing user roles, processing payments, and handling job applications. It uses a Flask backend for data management and API handling.

---

## How to Use

### In order to be up to date on the progress of this repository, be sure to source your code from the branch named Abdul

### Requirements

* Python 3.6 or higher installed on your system.
* Flask for the backend API.
* SQLite for database storage.

### Setup Instructions

1.  **Clone the Repository**

    Access the repository:

    ```bash
    git clone https://github.com/Manu88x/jwt.git
    
    ```

    Set Up the Backend:

    Navigate to the backend directory:
    Go to Branches then open Abdul branch 
    Then clone the repo
    ```bash
    git@github.com:Manu88x/jwt.git
    ```
    ```bash
    cd jwt
    ```

    Install Python dependencies:

    ```bash
    pipenv install
    ```

    Run the Flask server:

    ```bash
    python3 seed.py
    python3 app.py
    ```



### Features

* **Job Management:** Add, update, and delete job postings.
* **User Management:** Register users, update profiles, and manage roles (admin, user, premium).
* **Payment Processing:** Handle payments for premium subscriptions.
* **Job Applications:** Manage job applications and track their status.
* **Resource Management:** Add and manage resources for job seekers.
* **Authentication:** Secure API endpoints using JWT (JSON Web Tokens).
* **RBAC:** Allow access to API endpoints for users with specific roles.
 
### Technologies Used

* Flask: Backend framework for handling API requests.
* SQLite: Database for persistent data storage.
* Flask-RESTful: For building RESTful APIs.
* Flask-JWT-Extended: For user authentication and authorization.
* Flask-Migrate: For database migrations.

### Files in the Project

#### Backend (server)

* `app.py`: The main Flask application file.
* `models.py`: Contains the database models for users, jobs, payments, and resources.
* `auth_routes.py`: Handles user authentication and authorization.
* `resources/`: Contains resource classes for handling API endpoints.

### API Endpoints

#### Authentication

* `POST /register`: Register a new user.
* `POST /login`: Log in and receive a JWT token.
* `GET /protected`: A protected route that requires a JWT token to access.

#### Jobs

* `GET /get_jobs`: Retrieve all jobs.
* `GET /get_job?job_id=1`: Retrieve a specific job by ID.
* `GET /get_job?job_name=Software Developer`: Retrieve a specific job by name.
* `POST /add_job`: Add a new job posting.

#### Users

* `GET /get_users`: Retrieve all users (admin only).
* `GET /get_user?user_id=1`: Retrieve a specific user by ID.
* `GET /get_user?username=john_doe`: Retrieve a specific user by username.
* `GET /get_user?role=admin`: Retrieve users by role.
* `POST /add_user`: Add a new user.
* `PUT /update_user/<int:user_id>`: Update a user's profile.
* `DELETE /delete_user/<int:user_id>`: Delete a user (admin only).

#### Payments

* `GET /get_payments`: Retrieve all payments (admin only).
* `GET /get_payment?payment_id=1`: Retrieve a specific payment by ID.
* `GET /get_payment?username=john_doe`: Retrieve payments for a specific user.
* `POST /add_payment`: Add a new payment record.

#### Resources

* `GET /get_job_resources`: Retrieve all job resources.
* `GET /get_job_resource?resource_id=1`: Retrieve a resource by ID.
* `GET /get_job_resource?job_name=Software Engineer`: Retrieve resources for a job.
* `GET /get_job_resource?resource_type=Document`: Retrieve resources by type.
* `POST /add_job_resource`: Add a new job resource.
* `PUT /update_job_resource/<int:resource_id>`: Update a job resource.
* `DELETE /delete_job_resource/<int:resource_id>`: Delete a job resource.

#### Applications

* `GET /get_applications`: Retrieve all job applications.
* `GET /get_application?application_id=1`: Retrieve a specific application by ID.
* `GET /get_application?username=john_doe`: Retrieve applications for a user.
* `GET /get_application?job_name=Software Engineer`: Retrieve applications for a job.
* `POST /add_application`: Add a new job application.

#### Admin Routes

* `GET /admin/users`: Admin route to manage users.
* `GET /admin/applications`: Admin route to view all applications.
* `GET /admin/payments`: Admin route to view all payments.

### Future Enhancements

* Implement email notifications for job applications and payments.
* Add support for file uploads (e.g., resumes).
* Integrate with a payment gateway like M-Pesa for seamless payments.

### License

MIT License
```
© 2025 Abdul Aljawaab & Emmanuel Okoth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
