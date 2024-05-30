# SplitWiseCalc

## Description

SplitWiseCalc is a Django REST API project designed to manage expenses and shared expenses among users. It allows users to create expenses, share them with others, view their wallet balances, and perform various administrative tasks. The project includes authentication and authorization mechanisms to ensure secure access to the API endpoints.

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    ```

2. Navigate to the project directory:

    ```bash
    cd SplitWiseCalc
    ```

3. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Apply migrations:

    ```bash
    python manage.py migrate
    ```

## Usage

1. Run the development server:

    ```bash
    python manage.py runserver
    ```

2. Access the Swagger documentation:

    [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

3. Access the ReDoc documentation:

    [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

## API Endpoints

- `/api/create_user/`: Create a new user.
- `/api/login_user/`: Login user and generate access token.
- `/api/expenses/`: Create, list, or retrieve a specific expense.
- `/api/expenses/share/`: Share an expense with other users.
- `/api/wallet/balance/`: Check wallet balance for the authenticated user.
- `/admin/expenses/`: Admin view to list all expenses.
- `/admin/user_wallets/`: Admin view to list user wallets and balances.

## Dependencies

- **Django**: Web framework for building APIs.
- **Django REST Framework**: Toolkit for building Web APIs.
- **drf-yasg**: Library for generating Swagger/OpenAPI documentation.
- **PyJWT**: JSON Web Token implementation for Python.
- **Django-filter**: Filtering support for Django REST framework.

## Contributing

Contributions are welcome! Please open an issue to discuss proposed changes or submit a pull request directly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
