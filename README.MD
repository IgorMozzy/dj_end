# BangBang course final project
The project is a Django based website with a list of movies, their ratings and reviews added by other users. It includes functionality for free viewing of all data and possibility to register your own profile:
* Administrators: Adding new movies.
* Users: Viewing movie details, rating, and reviewing them.
* Moderators: Editing or deleting reviews.

Main page:

![Example](/docs/ex1.webp)

Detailed page:

![DetExample](/docs/ex3.webp)

See `/docs` for more examples.
## ⚙️ Used techs:
* Python 3.12
* Django 5.0
* Django REST Framework
* Docker & Docker Compose
* Nginx
* Prometheus & Grafana
* GitHub Actions for CI/CD
* Bootstrap 5
## 📁 Project Structure
```/
├── api/              # API handling app
├── certs/            # Predefined path to certificates
├── conf/             # Django configuration
├── docs/             # Project info and interface examples
├── movies/           # Main app: models, logic, HTML-templates
├── nginx/            # basic nginx configuration
└── users/            # Users managment app
```

### 💾 Main apps
1. **Users** – user models, registration, and authentication logic (post-migration ensures the presence of the groups: Admins, Moderators, Users).
2. **API** – DRF endpoints for user management (creation, deletion, obtaining JWT tokens). Currently, only user and group management is supported, but not movies.
3. **Movies** – The main application, including models for working with the movie database and Django templates for rendering.

### 👤 User Management
The is_staff system role is considered the main indicator of an administrator. The Admins and Users groups can be used to restrict access to views.

`/a/users/` - default route for simple user management.

![Example2](/docs/ex2.webp)

At the same time the Django admin panel is still active at `/d/admin/`.

Using DRF and JWT (authentication in the API is implemented via JWT):
Obtain Access and Refresh tokens using login credentials:
```
POST /api/token/
{
  "username": "username",
  "password": "string"
}
```
Obtain a new Access token using a Refresh token:
```
POST /api/refresh/
{
  "refresh": "string"
}
```
### 🛝️ API
Endpoints for managing users and groups:
Groups:
```
GET, POST → /groups/
GET, PUT, PATCH, DELETE → /groups/{id}/
```
Users:
```
GET, POST → /users/
GET, PUT, PATCH, DELETE → /users/{id}/
```
API Documentation:
```
# Swagger UI with auto-generated documentation and testing capabilities (available to administrators)
/swagger/

#  API schema in JSON format
/swagger.json
```
## 🏗️ Deployment
**For production and test installations, you must have docker and docker compose installed.**
### Development environment
1. Clone the repository:
```
git clone git@github.com:IgorMozzy/dj_end.git .
cd dj_end.git
```
2. Build Docker compose setup:
```
docker-compose up --build -d
```
3. It's done. App should be available at http://localhost/
### SSL-server environment
1. The repository is set up with automatic testing and deployment via GitHub Actions, using a configuration designed for deployment on a Linux server with Docker Сompose.
2. The installation script requires setting the repository Secrets parameters: `SSH_HOST`, `SSH_PRIVATE_KEY`, and `SSH_USERNAME` — to connect to the specified machine via SSH during the automated deployment process.
3. For a successful connection during deployment, the server will need to access the repository. If the repository is private, this may also require the private key to be present on the server (with the public key added to the GitHub account settings for authentication).
4. If needed, you can pre-check the server's authentication with GitHub using the following command: `ssh -T git@github.com`
5. After the initial deployment, you need to copy the SSL certificate to the server. The certificate generation paths are specified in the Nginx configuration. By default, the certificates are named `cert.crt` and `cert.key` and are located in the `/certs` folder at the root of the project.
6. Adjust the .env file settings in the project folder on the server by adding the `SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` (comma-separated). For example:
```
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web,158.160.26.232,somedomain.ru

DJANGO_CSRF_TRUSTED_ORIGINS=https://somedomain.ru,http://somedomain.ru
```
7. Rebuild and restart the Docker containers with the following command:
```commandline
docker compose up -d --build
```
9. Future updates should be made directly through the repository to avoid merge conflicts. Currently, the branch for cloning is specified **manually** in `.github/workflows/ci_cd.yaml`.
10. After the initial deployment, you also need to configure Grafana. Use the default password from the environment variables for the first login. Grafana is accessible on port 3000 via HTTP using the host's IP address.
11. The Prometheus server is already added to Grafana at: `http://prometheus:9090`
12. The first superuser can be created inside the web container with the following commands:
```
docker compose exec web bash
python3 manage.py createsuperuser
```
### Feed the database with test data
If you need to populate the database with test data, you can use the following command:
```commandline
# runs the script located at movies/management/seed_data.py
python manage.py seed_data
```
#### Misc
Here are some example commands used in the process:
```
# Copying keys using scp
scp -i ./.ssh/key "C:\Users\..." name@IP:<destination path>

# SSH connection with a specific key:
ssh -i ./.ssh/key name@IP

# Generating a Django secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```