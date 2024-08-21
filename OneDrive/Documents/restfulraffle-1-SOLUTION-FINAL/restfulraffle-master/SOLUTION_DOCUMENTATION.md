# RESTful Raffle Application Solution Documentation

This document outlines the implementation details of the RESTful Raffle application, following the instructions and requirements specified in the README.md file.

## Project Structure

The solution follows the Model-View-Serializer (MVS) architecture pattern, which is a common approach in Django REST Framework (DRF) applications. The main components of the solution are:

### Models

The `models.py` file defines the following database models:

- **Raffle**: Represents a single raffle event, including its name, total number of tickets, prizes, and creation date.
- **Ticket**: Represents a single ticket in a raffle, with a unique ticket number, verification code, and participant information.
- **Winner**: Represents a participant who has won a prize in a raffle, linking the winning ticket to the prize.

The models define the necessary fields, relationships, and methods to support the raffle functionality.

### Serializers

The `serializers.py` file contains the serializer classes used to convert the Django models into JSON-compatible representations. The main serializers are:

- **PrizeSerializer**: Serializes the prize information for a raffle.
- **RaffleSerializer**: Serializes the Raffle model, including nested prize data and additional fields for available tickets and winners drawn status.
- **TicketSerializer**: Serializes the Ticket model, with read-only fields for automatically generated data.
- **WinnerSerializer**: Serializes the Winner model, including the associated ticket and prize data.

### Views

The `views.py` file contains the view classes that handle the HTTP requests and return the appropriate responses. The main views are:

- **RaffleListCreateView**: Handles listing and creating raffles. Supports GET and POST requests.
- **RaffleDetailView**: Retrieves the details of a specific raffle. Supports GET requests.
- **ParticipateView**: Allows users to participate in a raffle by claiming a ticket. Supports POST requests.
- **RaffleWinnersView**: Handles listing and drawing raffle winners. Supports GET and POST requests.
- **VerifyTicketView**: Verifies a raffle ticket and returns its winning status. Supports POST requests.

The views utilize the serializers to parse and validate request data, perform the necessary database operations, and return the appropriate responses.

## Implementation Details

### Setup and Configuration

1. Created and activated a virtual environment named `raffleEnv` to isolate project dependencies.
2. Installed the required packages listed in `requirements.txt` using `pip install -r requirements.txt`.
3. Created a new Django application named `raffle` using `python manage.py startapp raffle`.
4. Added necessary app files: `serializers.py`, `permissions.py`, `urls.py`, `utils.py`, `exceptions.py`, `logging_utils.py`, and `signals.py`.

### Testing

1. Updated the `test_raffle_list` function in `raffle_retrieval_tests.py` to handle paginated responses.
2. Created additional tests to cover all the listed requirements.
3. Added a fixture in `conftest.py` to disable caching during testing.
```python 
DISABLE_TEST_CACHING = True

@pytest.fixture(autouse=True)
def disable_test_caching(settings):
    settings.DISABLE_TEST_CACHING = True
```

4. Updated `settings.py` to configure pagination, renderers, exception handling, and caching settings.
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Number of items per page
    'DEFAULT_RENDERER_CLASSES': (
       'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        #'rest_framework.renderers.TemplateHTMLRenderer',
    ),
    'EXCEPTION_HANDLER': 'raffle.logging_utils.custom_exception_handler',
}
DISABLE_TEST_CACHING = True
MANAGER_IPS = os.environ.get('MANAGER_IPS')
```
### Performance Optimization

1. Implemented caching strategies for frequently accessed data, such as raffle details and winner lists, using Django's in-memory caching backend.
2. Configured cache invalidation using signal receivers in `signals.py` to ensure data consistency.

### API Endpoints

The following API endpoints were implemented:

| Endpoint | Description | Manager only |
|----------|-------------|--------------|
| POST /raffles/ | Create a new raffle | Yes |
| GET /raffles/ | List raffles starting from latest | No |
| GET /raffles/<id>/ | Get details of a raffle | No |
| POST /raffles/<id>/participate/ | Get a raffle ticket | No |
| POST /raffles/<id>/winners/ | Draw winners of a raffle | Yes |
| GET /raffles/<id>/winners/ | List winners of a raffle | No |
| POST /raffles/<id>/verify-ticket/ | Verify ticket and winnings | No |

### Access Control

Access to the raffle manager endpoints (POST /raffles/ and POST /raffles/<id>/winners/) is restricted to IP addresses listed in the `MANAGER_IPS` environment variable.

## Conclusion

The RESTful Raffle application solution adheres to the provided instructions and requirements, implementing a robust and scalable API using Django REST Framework. The solution follows best practices for code organization, testing, and performance optimization, ensuring a reliable and efficient raffle management system.