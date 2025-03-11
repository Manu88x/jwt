######################
###############
##############
########

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, User, Job, JobApplication, Payment, ExtraResource
import datetime
from flask import Response
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from auth_routes import Register, Login, Protected, role_required
#from datetime import datetime 
from datetime import timedelta
from flask import request, jsonify
from werkzeug.security import generate_password_hash
import base64
import requests
from requests.auth import HTTPBasicAuth


app = Flask(__name__)
cors = CORS(app, origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Job.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change to a secure key
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Secret key for JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=37)  # Set expiration to 2 hours
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)  # Set refresh token expiry to 7 days

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

jwt = JWTManager(app)  # Initialize JWT Manager

# M-Pesa credentials (Use environment variables for security in production)
consumer_key = 'BAWVnD0jcd3WW9FiRuiwGTTrSwxXRjHGNn4XJXqBlzQPzqHQ'
consumer_secret = 'mc9CMe7k4EK1E0PIvetAgVuaom0shGWwChGxp7EiiNNUBu3PnxXBxxRjGLZQInQK'
shortcode = "174379"
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"

# OAuth URL for authentication to get an access token from Safaricom
api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

# M-Pesa API endpoint for the B2C payment request (sending money)
api_endpoint = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest'

# Define the callback URL (for simplicity, we use the same URL for callback)
callback_url = "https://yourserver.com/api/payment"  # Replace with your actual callback URL


# Base route to show available routes and info
class BaseRoute(Resource):
    def get(self):
        return jsonify({
            "message": "Welcome to the Job Management API! Below are the available routes:",
            "routes": {
                "/register": "Adding users",
                "/login": "Login route for user authentication.",
                "/get_jobs": "Retrieve all jobs.",
                "/get_job?job_id=1 or /get_job?job_name=Software Developer": "Retrieve a job by ID or job name",
                "/get_users": "Retrieve all users.",
                "/get_user?user_id=1, /get_user?username=john_doe, or /get_user?role=admin": "Retrieve a user by ID, username, or role",
                "/update_user/<int:user_id>": "Update a user by ID.",
                "/delete_user/<int:user_id>": "Delete a user by ID.",
                "/get_payments": "Retrieve all payments.",
                "/get_payment?payment_id=1 or /get_payment?username=john_doe": "Retrieve a payment by ID or username.",
                "/add_payment": "Add a new payment.",
                "/get_job_resources": "Retrieve all extra resources for a job.",
                "/get_job_resource?resource_id=1 or /get_job_resource?job_name=Software Engineer or /get_job_resource?resource_type=Document": "Retrieve a resource by ID, job name, or resource type",
                "/add_job_resource": "Add a new extra resource.",
                "/update_job_resource/<int:resource_id>": "Update a resource by ID.",
                "/delete_job_resource/<int:resource_id>": "Delete a resource by ID.",
                "/get_applications": "Retrieve all job applications.",
                "/get_application?application_id=1 or /get_application?username=john_doe or /get_application?job_name=Software Engineer": "Retrieve a job application by ID, username, or job name",
                "/add_application": "Add a new job application.",
                "/login": "Login route for user authentication.",
                "/protected": "A protected resource that requires a JWT token to access.",
                "/add_job_resource": "Admin route to add new job resources.",
            }
        })





        







# Job Routes
class GetJobs(Resource):
    @jwt_required()
    def get(self):
        jobs = Job.query.all()  # Retrieve all jobs
        jobs_list = []
        for job in jobs:
            print(job)
            job_data = job.to_dict()  # Get the full job dict
            print(job_data)
            job_data.pop('applications', None)  # Remove applications field if present
            job_data.pop('extra_resources', None)  # Remove extra_resources field if present
            jobs_list.append(job_data)
        return (jobs_list)  # Return the filtered list of jobs
    
api.add_resource(GetJobs, '/get_jobs')

class GetJob(Resource):
    @jwt_required()
    def get(self):
        job_id = request.args.get('job_id', type=int)
        job_name = request.args.get('job_name', type=str)

        if job_id:
            job = Job.query.get(job_id)
            if not job:
                # Return error as plain text
                return jsonify({"error": f"Job with ID {job_id} not found."}), 404
                #return Response(f"Job with ID {job_id} not found.", status=404, mimetype='text/plain')
        elif job_name:
            job = Job.query.filter_by(title=job_name).first()
            if not job:
                # Return error as plain text
                return {"error": f"Job with name '{job_name}' not found."}, 404
                #return Response(f"Job with name '{job_name}' not found.", status=404, mimetype='text/plain')
        else:
            # Return error as plain text
            return {"error": "Either 'job_id' or 'job_name' must be provided."}, 400
            #return Response("Either 'job_id' or 'job_name' must be provided.", status=400, mimetype='text/plain')

        # If the job is found, remove unwanted fields and return job data as JSON
        job_data = job.to_dict()  # Get the full job dict
        job_data.pop('applications', None)  # Remove applications field
        job_data.pop('extra_resources', None)  # Remove extra_resources field
        return job_data  # Return the filtered job dat

    

# User Routes
class GetUsers(Resource):
    #@role_required('admin') # Only admin users can access this route
    @jwt_required()
    def get(self):
        users = User.query.all()
        users_list = []
        for user in users:
            user_data = user.to_dict()
            user_data.pop('applications', None)
            user_data.pop('payments', None)
            users_list.append(user_data)
        return users_list

class GetUser(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def get(self):
        user_id = request.args.get('user_id', type=int)
        username = request.args.get('username', type=str)
        role = request.args.get('role', type=str)  # New role parameter

        if user_id:
            user = User.query.get(user_id)
            if not user:
                # Return error as plain text
                return {"error": f"User with ID {user_id} not found."}, 404
                #return Response(f"User with ID {user_id} not found.", status=404, mimetype='text/plain')
        elif username:
            user = User.query.filter_by(username=username).first()
            if not user:
                # Return error as plain text
                return {"error": f"User with username '{username}' not found."}, 404
                #return Response(f"User with username '{username}' not found.", status=404, mimetype='text/plain')
        elif role:
            user = User.query.filter_by(role=role).first()
            if not user:
                # Return error as plain text
                return {"error": f"No users found with role '{role}'."}, 404
                #return Response(f"No users found with role '{role}'.", status=404, mimetype='text/plain')
        else:
            # Return error as plain text
            return {"error": "Either 'user_id', 'username', or 'role' must be provided."}, 400
            #return Response("Either 'user_id', 'username', or 'role' must be provided.", status=400, mimetype='text/plain')

        # If the user is found, remove unwanted fields and return user data as JSON
        user_data = user.to_dict()
        user_data.pop('applications', None)
        user_data.pop('payments', None)
        return user_data # Return the filtered user data as JSON


class UpdateUser(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def patch(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        try:
            # Update user attributes if provided
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            
            # Handle password update if provided
            if 'password_hash' in data:
                user.password_hash = generate_password_hash(data['password_hash'])
            
            if 'role' in data:
                user.role = data['role']

            # Update related applications (if applicable)
            if 'applications' in data:
                for app_data in data['applications']:
                    app = JobApplication.query.get(app_data['id'])
                    if app:
                        if 'position' in app_data:
                            app.position = app_data['position']
                        if 'status' in app_data:
                            app.status = app_data['status']
                        # You can add any other application-specific fields here
                    db.session.commit()

            # Update related payments (if applicable)
            if 'payments' in data:
                for payment_data in data['payments']:
                    payment = Payment.query.get(payment_data['id'])
                    if payment:
                        if 'amount' in payment_data:
                            payment.amount = payment_data['amount']
                        if 'status' in payment_data:
                            payment.status = payment_data['status']
                        # You can add any other payment-specific fields here
                    db.session.commit()

            # Commit the changes to the user record
            db.session.commit()

            return jsonify(user.to_dict())
        
        except Exception as e:
            db.session.rollback()  # Rollback any changes in case of an error
            return {"error": str(e)}, 400

class DeleteUser(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)

        # Keep job applications and payments but retain user data in them
        applications = JobApplication.query.filter_by(user_id=user.id).all()
        for app in applications:
            app.user_id = None  # Disconnect the user from the job application
            app.username = user.username
            app.email = user.email
            app.phone = user.phone
            db.session.commit()

        payments = Payment.query.filter_by(user_id=user.id).all()
        for payment in payments:
            payment.user_id = None  # Disconnect the user from the payment
            payment.username = user.username
            payment.email = user.email
            payment.phone = user.phone
            db.session.commit()

        # Delete the user, but retain the user info in applications and payments
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted but related applications and payments retained."}
    
# Payment Routes
class GetPayments(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def get(self):
        payments = Payment.query.all()
        return jsonify([payment.to_dict() for payment in payments])

class GetPayment(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def get(self):
        payment_id = request.args.get('payment_id', type=int)
        username = request.args.get('username', type=str)

        # Check for payment_id
        if payment_id:
            payment = Payment.query.get(payment_id)  # .get() is used for getting by ID
            if payment:
                return jsonify(payment.to_dict())
            else:
                # Return error as plain text
                return {"error": "Payment not found with the provided ID."}, 404

        # Check for username
        elif username:
            user = User.query.filter_by(username=username).first()
            if user:
                payments = Payment.query.filter_by(user_id=user.id).all()
                if payments:
                    return jsonify([payment.to_dict() for payment in payments])
                else:
                    # Return error as plain text
                    return {"error": "No payments found for the provided username."}, 404
                    #return Response("No payments found for the provided username.", status=404, mimetype='text/plain')
            else:
                # Return error as plain text
                return {"error": "User with the provided username does not exist."}, 404
                #return Response("User with the provided username does not exist.", status=404, mimetype='text/plain')

        # If neither payment_id nor username is provided
        else:
            # Return error as plain text
            return {"error": "Payment not found with the provided ID."}, 400
            #return Response("Either 'payment_id' or 'username' must be provided.", status=400, mimetype='text/plain')


class AddPayment(Resource):
    def post(self):
        data = request.get_json()
        try:
            payment = Payment(
                user_id=data['user_id'],
                amount=5000.0,
                payment_status=data.get('payment_status', 'completed'),
                payment_date=datetime.datetime.strptime(data['payment_date'], '%Y-%m-%d %H:%M:%S')
            )
            db.session.add(payment)
            db.session.commit()

            user = User.query.get(data['user_id'])
            if payment.amount == 5000 and payment.payment_status == 'completed':
                user.role = 'premium'
                db.session.commit()

            return payment.to_dict(), 201
        except Exception as e:
            return {"error": str(e)}, 400


class GetResources(Resource):
    #@role_required('premium_user')
    def get(self):
        resources = ExtraResource.query.all()
        return jsonify([resource.to_dict() for resource in resources])

class GetResource(Resource):
    #@role_required('premium_user')  # Only admin & premium users can access this route
    @jwt_required()
    def get(self):
        resource_id = request.args.get('resource_id', type=int)
        job_name = request.args.get('job_name', type=str)
        resource_type = request.args.get('resource_type', type=str)

        # Handle resource_id
        if resource_id:
            resource = ExtraResource.query.get(resource_id)
            if resource:
                return jsonify(resource.to_dict())  # No iteration needed for a single object
            else:
                # Return error as plain text
                return {"error": "Resource not found with the provided ID."}, 404
                #return Response("Resource not found with the provided ID.", status=404, mimetype='text/plain')

        # Handle job_name
        elif job_name:
            job = Job.query.filter_by(title=job_name).first()
            if job:
                resources = ExtraResource.query.filter_by(job_id=job.id).all()
                if resources:
                    return jsonify([resource.to_dict() for resource in resources])
                else:
                    # Return error as plain text
                    return {"error": "No resources found for this job."}, 404
                    #return Response("No resources found for this job.", status=404, mimetype='text/plain')

        # Handle resource_type
        elif resource_type:
            resources = ExtraResource.query.filter_by(resource_type=resource_type).all()
            if resources:
                return jsonify([resource.to_dict() for resource in resources])
            else:
                # Return error as plain text
                return {"error": "No resources found for this type."}, 404
                #return Response("No resources found for this type.", status=404, mimetype='text/plain')

        # If neither resource_id, job_name, nor resource_type is provided
        else:
            # Return error as plain text
            return {"error": "Provide either 'resource_id', 'job_name', or 'resource_type'."}, 400
            #return Response("Provide either 'resource_id', 'job_name', or 'resource_type'.", status=400, mimetype='text/plain')

class AddResource(Resource):
    #@role_required('admin')  # Only admin can access this route
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Validate required fields
        if not data.get('job_id') or not data.get('resource_name') or not data.get('resource_type'):
            return {"error": "job_id, resource_name, and resource_type are required fields."}, 400

        try:
            # Fetch the job or create a new one
            job = Job.query.get(data['job_id'])
            if not job:
                # Validate application_deadline
                if 'application_deadline' not in data:
                    return {"error": "application_deadline is a required field."}, 400
                
                # Validate the date format
                try:
                    application_deadline = datetime.strptime(data['application_deadline'], "%Y-%m-%d")
                except ValueError:
                    return {"error": "Invalid date format for application_deadline. Expected format: YYYY-MM-DD."}, 400

                # Create a new job with default values for optional fields
                job = Job(
                    title=data.get('job_title', 'Default Title'),
                    description=data.get('job_description', ''),
                    location=data.get('job_location', 'Remote'),
                    salary_min=data.get('salary_min', 0),
                    salary_max=data.get('salary_max', 0),
                    job_type=data.get('job_type', 'Full-time'),
                    skills_required=data.get('skills_required', ''),
                    benefits=data.get('benefits', ''),
                    application_deadline=application_deadline,
                    employer=data.get('employer', ''),
                    employer_email=data.get('employer_email', ''),
                    employer_phone=data.get('employer_phone', '')
                )
                db.session.add(job)
                db.session.commit()
                print(f"Created new job with ID: {job.id}")

            # Create the resource
            resource = ExtraResource(
                job_id=job.id,
                resource_name=data['resource_name'],
                description=data.get('description', ''),
                resource_type=data['resource_type']
            )
            db.session.add(resource)
            db.session.commit()
            print(f"Created new resource with ID: {resource.id}")

            return resource.to_dict(), 201
        except Exception as e:
            # Log the error and rollback the session
            db.session.rollback()
            print(f"Error: {str(e)}")  # This will help with debugging
            return {"error": str(e)}, 400
        
class UpdateResource(Resource):
    #@role_required('admin')  # Only admin can access this route
    @jwt_required()
    def patch(self, resource_id):
        # Fetch the ExtraResource by resource_id
        resource = ExtraResource.query.get_or_404(resource_id)
        data = request.get_json()

        try:
            # Partial update: Update only the fields that are provided in the request
            if 'resource_name' in data:
                resource.resource_name = data['resource_name']
            if 'description' in data:
                resource.description = data['description']
            if 'resource_type' in data:
                resource.resource_type = data['resource_type']

            # If job_id is provided, update the associated job details
            if 'job_id' in data:
                job = Job.query.get(data['job_id'])
                if not job:
                    return {"error": "Job not found"}, 404  # Return error if job doesn't exist

                # Update job details if provided in the request
                if 'job_title' in data:
                    job.title = data['job_title']
                if 'job_location' in data:
                    job.location = data['job_location']
                if 'salary_min' in data:
                    job.salary_min = data['salary_min']
                if 'salary_max' in data:
                    job.salary_max = data['salary_max']
                if 'job_type' in data:
                    job.job_type = data['job_type']
                if 'skills_required' in data:
                    job.skills_required = data['skills_required']
                if 'benefits' in data:
                    job.benefits = data['benefits']
                if 'application_deadline' in data:
                    try:
                        # Ensure the application_deadline is correctly formatted as datetime
                        application_deadline = datetime.strptime(data['application_deadline'], "%Y-%m-%d")
                        job.application_deadline = application_deadline
                    except ValueError:
                        return {"error": "Invalid date format for application_deadline. Expected format: YYYY-MM-DD."}, 400
                if 'employer' in data:
                    job.employer = data['employer']
                if 'employer_email' in data:
                    job.employer_email = data['employer_email']
                if 'employer_phone' in data:
                    job.employer_phone = data['employer_phone']

                db.session.commit()  # Commit changes to the job

            db.session.commit()  # Commit changes to the resource
            return resource.to_dict()  # Return updated resource as a dictionary

        except Exception as e:
            db.session.rollback()  # Rollback if an error occurs
            print(f"Error updating resource: {str(e)}")  # For debugging purposes
            return {"error": str(e)}, 400
                
class DeleteResource(Resource):
    #@role_required('admin')  # Only admin can access this route
    @jwt_required()
    def delete(self, resource_id):
        resource = ExtraResource.query.get_or_404(resource_id)
        job = Job.query.get_or_404(resource.job_id)

        # Get all related applications and retain job info in them
        related_applications = JobApplication.query.filter_by(job_id=job.id).all()
        for app in related_applications:
            # Keep the job details in the application, even if job is deleted
            app.job_title = job.title
            app.job_location = job.location
            app.salary_min = job.salary_min
            app.salary_max = job.salary_max
            app.job_type = job.job_type
            app.skills_required = job.skills_required
            app.benefits = job.benefits
            app.application_deadline = job.application_deadline

            db.session.commit()

        # Check if the job still has other resources; if not, delete the job
        remaining_resources = ExtraResource.query.filter_by(job_id=job.id).all()
        if not remaining_resources:
            db.session.delete(job)
        
        # Delete the resource (but not the job data from applications)
        db.session.delete(resource)
        db.session.commit()

        return {"message": "Resource deleted, but job information retained in applications."}        

# Job Application Routes
class GetApplications(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def get(self):
        applications = JobApplication.query.all()
        return jsonify([application.to_dict() for application in applications])


class GetApplication(Resource):
    #@role_required('admin')  # Only admin users can access this route
    @jwt_required()
    def get(self):
        try:
            application_id = request.args.get('application_id', type=int)
            username = request.args.get('username', type=str)
            job_name = request.args.get('job_name', type=str)

            # Handle application_id search
            if application_id:
                application = JobApplication.query.get(application_id)
                if application:
                    return jsonify(application.to_dict())  # Return application as JSON
                else:
                    return jsonify({"error": f"Application not found with ID {application_id}."}), 404
                    #return Response(f"Application not found with ID {application_id}.", status=404, mimetype='text/plain')

            # Handle username search
            elif username:
                user = User.query.filter_by(username=username).first()
                if user:
                    applications = JobApplication.query.filter_by(user_id=user.id).all()
                    if applications:
                        return jsonify([application.to_dict() for application in applications])
                    else:
                        return {"error": f"No applications found for user '{username}'."}, 404
                        #return Response(f"No applications found for user '{username}'.", status=404, mimetype='text/plain')
                else:
                    return {"error": f"User with username '{username}' does not exist."}, 404
                    #return Response(f"User with username '{username}' does not exist.", status=404, mimetype='text/plain')

            # Handle job_name search
            elif job_name:
                job = Job.query.filter_by(title=job_name).first()
                if job:
                    applications = JobApplication.query.filter_by(job_id=job.id).all()
                    if applications:
                        return jsonify([application.to_dict() for application in applications])
                    else:
                        return {"error": f"No applications found for job '{job_name}'."}, 404
                        #return Response(f"No applications found for job '{job_name}'.", status=404, mimetype='text/plain')

            # If none of the parameters are provided
            else:
                return {"error": "Please provide either 'application_id', 'username', or 'job_name'."}, 400
                #return Response("Please provide either 'application_id', 'username', or 'job_name'.", status=400, mimetype='text/plain')

        except Exception as e:
            # Return a plain text error message
            return {"error": f"An error occurred: {str(e)}"}, 500
            #return Response(f"An error occurred: {str(e)}", status=500, mimetype='text/plain')



class AddApplication(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Automatically get user_id from the JWT token payload
        user_id = get_jwt_identity()  # Assumes the JWT token has user_id in it

        # Automatically set job_id based on your logic
        # Example: Fetch the first available job or some logic to select job_id
        job_id = data.get('job_id')  # If the job_id is passed in the payload, use it
        if not job_id:
            # Example: Get the first available job from the database
            job = Job.query.filter_by(status='open').first()  # Modify this query as needed
            if job:
                job_id = job.id
            else:
                return {"error": "No open jobs available"}, 404

        try:
            # Automatically set status to "pending"
            # Automatically set date_applied to the current date and time
            application = JobApplication(
                user_id=user_id,  # Use the user_id fetched from JWT
                job_id=job_id,    # Use the job_id fetched from logic
                status="pending",  # Automatically set status
                application_date=datetime.now()  # Automatically set to current date and time
            )
            
            # Add the new application to the session and commit
            db.session.add(application)
            db.session.commit()

            # Return the created application as a dictionary with a status code 201
            return application.to_dict(), 201

        except SQLAlchemyError as e:
            # Handle database-related errors
            db.session.rollback()  # Rollback any changes in case of error
            return {"error": "Database error: " + str(e)}, 500

        except KeyError as e:
            # Handle missing key error
            return {"error": f"Missing key: {str(e)}"}, 400

        except Exception as e:
            # General error handling
            return {"error": str(e)}, 500
                    
#authentication routes
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Protected, '/protected')

# Add resources to API with specific HTTP methods and unique routes
api.add_resource(BaseRoute, '/')



api.add_resource(GetJob, '/get_job')  # Changed this route to handle both job ID and job name
api.add_resource(GetUsers, '/get_users')
api.add_resource(GetUser, '/get_user')  # Changed this route to handle both user ID and username
api.add_resource(UpdateUser, '/update_user/<int:user_id>')
api.add_resource(DeleteUser, '/delete_user/<int:user_id>')

api.add_resource(GetPayments, '/get_payments')
api.add_resource(GetPayment, '/get_payment')  # Changed this route to handle both payment ID and username
api.add_resource(AddPayment, '/add_payment')

api.add_resource(GetResources, '/get_job_resources') 
api.add_resource(GetResource, '/get_job_resource')  # Changed this route to handle ID, job name, or resource type
api.add_resource(AddResource, '/add_job_resource')
api.add_resource(UpdateResource, '/update_job_resource/<int:resource_id>')
api.add_resource(DeleteResource, '/delete_job_resource/<int:resource_id>')

api.add_resource(GetApplications, '/get_applications')
api.add_resource(GetApplication, '/get_application')  # Changed this route to handle application ID, username, or job name
api.add_resource(AddApplication, '/add_application')

if __name__ == "__main__":
    app.run(debug=True, port=6000)