# Restaurant Manager System

## Overview
Restaurant Manager is a comprehensive web application designed to streamline restaurant operations. It provides tools for menu management, order processing, billing, and staff management.

## Features
- **Menu Management**: Create, update, and organize menu items with categories, variants, and pricing
- **Order Processing**: Real-time order management with WebSocket support
- **Billing System**: Generate and manage bills with different payment methods
- **User Management**: Role-based access control for staff members
- **Restaurant Management**: Multi-restaurant support with categorization

## Technology Stack
- **Backend**: Django, Django REST Framework
- **Real-time Communication**: Django Channels
- **Database**: SQLite (default), can be configured for PostgreSQL
- **Authentication**: Django authentication system with custom permissions

## Installation

### Prerequisites
- Python 3.8+
- Redis (for WebSocket support)

### Setup
1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Start Redis server (for WebSocket support):
   ```
   redis-server --port 6380
   ```
7. Run the development server:
   ```
   daphne restromanager.asgi:application
   ```

## Project Structure
- **menu**: App for menu items, categories, and order management
- **restaurants**: App for restaurant management
- **users**: App for user management and authentication
- **restromanager**: Main project configuration

## API Documentation
API documentation is available in the `guid for api` directory:
- `api_endpoints_reference.md`: Detailed API endpoint documentation
- `frontend_api_guide.md`: Guide for frontend integration
- `workflow_diagram.md`: System workflow diagrams

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.