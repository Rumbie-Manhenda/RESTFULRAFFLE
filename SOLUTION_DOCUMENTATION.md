
```markdown
# RESTful Raffle Application Documentation

This document outlines the implementation details of the RESTful Raffle application, detailing the setup, structure, and functionality as specified in the accompanying `README.md` file.

## Project Overview

The RESTful Raffle application provides a platform for managing raffles, allowing users to participate by purchasing tickets, and enabling the raffle manager to draw winners and validate tickets. The application follows the Model-View-Serializer (MVS) architecture pattern, a widely adopted approach in Django REST Framework (DRF) applications.

## Project Structure

The primary components of the solution are organized as follows:

### 1. Models

The `models.py` file defines the following database models:

- **Raffle**: Represents a single raffle event, including fields such as:
  - `name`: The name of the raffle.
  - `total_tickets`: The total number of tickets available for the raffle.
  - `prizes`: A list of prizes associated with the raffle.
  - `created_at`: Timestamp for when the raffle was created.

- **Ticket**: Represents an individual ticket within a raffle, including:
  - `ticket_number`: A unique identifier for each ticket.
  - `verification_code`: A code used to validate the ticket.
  - `participant_info`: Information about the participant who claims the ticket.

- **Winner**: Represents a participant who has won a prize, linking:
  - `ticket`: The winning ticket associated with the participant.
  - `prize`: The prize won.

These models define the necessary fields, relationships, and methods to support raffle functionality.

### 2. Serializers

The `serializers.py` file includes the following serializer classes to convert Django models into JSON-compatible representations:

- **PrizeSerializer**: Serializes prize information for a raffle.
- **RaffleSerializer**: Serializes the Raffle model, including:
  - Nested prize data.
  - Additional fields for available tickets and winners drawn status.
  
- **TicketSerializer**: Serializes the Ticket model, incorporating read-only fields for automatically generated data.
- **WinnerSerializer**: Serializes the Winner model, including associated ticket and prize data.

### 3. Views

The `views.py` file contains view classes that handle HTTP requests and return appropriate responses. The key views include:

- **RaffleListCreateView**: Handles listing and creating raffles; supports GET and POST requests.
- **RaffleDetailView**: Retrieves details of a specific raffle; supports GET requests.
- **ParticipateView**: Allows users to participate in a raffle by claiming a ticket; supports POST requests.
- **RaffleWinnersView**: Manages listing and drawing of raffle winners; supports GET and POST requests.
- **VerifyTicketView**: Verifies a raffle ticket and returns its winning status; supports POST requests.

The views utilize serializers to parse and validate request data, execute necessary database operations, and return appropriate responses.

## Implementation Details

### Setup and Configuration

1. **Virtual Environment**: Created and activated a virtual environment named `raffleEnv` to isolate project dependencies:
   ```bash
   python -m venv raffleEnv
   source raffleEnv/bin/activate
   ```
   
2. **Package Installation**: Installed required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Django Application Creation**: Created a new Django application named `raffle`:
   ```bash
   python manage.py startapp raffle
   ```

4. **Application Files**: Added necessary application files including `serializers.py`, `permissions.py`, `urls.py`, `utils.py`, `exceptions.py`, `logging_utils.py`, and `signals.py`.

### Testing

1. **Test Updates**: Updated the `test_raffle_list` function in `raffle_retrieval_tests.py` to handle paginated responses.
   
2. **Test Coverage**: Created additional tests to ensure comprehensive coverage of all listed requirements.

3. **Caching Fixture**: Added a fixture in `conftest.py` to disable caching during testing:
   ```python
   DISABLE_TEST_CACHING = True

   @pytest.fixture(autouse=True)
   def disable_test_caching(settings):
       settings.DISABLE_TEST_CACHING = True
   ```

4. **Settings Configuration**: Updated `settings.py` to configure pagination, renderers, exception handling, and caching settings:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 10,  # Number of items per page
       'DEFAULT_RENDERER_CLASSES': (
           'rest_framework.renderers.JSONRenderer',
           'rest_framework.renderers.BrowsableAPIRenderer',
       ),
       'EXCEPTION_HANDLER': 'raffle.logging_utils.custom_exception_handler',
   }
   ```

### Performance Optimization

1. **Caching Strategies**: Implemented caching for frequently accessed data, such as raffle details and winner lists, using Django's in-memory caching backend.
   
2. **Cache Invalidation**: Configured cache invalidation using signal receivers in `signals.py` to ensure data consistency.

### API Endpoints

The following API endpoints were implemented:

| Method | Endpoint                       | Description                          | Manager Only |
|--------|--------------------------------|--------------------------------------|--------------|
| POST   | `/raffles/`                   | Create a new raffle                  | Yes          |
| GET    | `/raffles/`                   | List raffles starting from latest    | No           |
| GET    | `/raffles/<id>/`              | Get details of a raffle              | No           |
| POST   | `/raffles/<id>/participate/`  | Claim a raffle ticket                | No           |
| POST   | `/raffles/<id>/winners/`      | Draw winners of a raffle             | Yes          |
| GET    | `/raffles/<id>/winners/`      | List winners of a raffle             | No           |
| POST   | `/raffles/<id>/verify-ticket/` | Verify ticket and winnings            | No           |

### Access Control

Access to the raffle manager endpoints (e.g., `POST /raffles/` and `POST /raffles/<id>/winners/`) is restricted to IP addresses listed in the `MANAGER_IPS` environment variable.

## Conclusion

The RESTful Raffle application adheres to the provided instructions and requirements, implementing a robust and scalable API using Django REST Framework. The solution follows best practices for code organization, testing, and performance optimization, ensuring a reliable and efficient raffle management system.

## Requirements Summary

- The raffle manager creates a new raffle specifying the number of tickets and prizes.
- Ticket numbers for each raffle are sequential, starting from 1.
- Tickets are issued to participants in a non-sequential order.
- Verification codes for tickets are not stored in plaintext.
- Each ticket number is unique to a participant within a raffle.
- A single IP address may not participate in a raffle more than once.
- Raffle winners are drawn randomly from remaining tickets.
- One ticket cannot win more than one prize.
- Access to manager endpoints is restricted to specified IP addresses.
- Application performance must remain optimal even with a large number of tickets, prizes, and participants.

## Raffle Website Demo

[Link to Demo Here](https://www.youtube.com/watch?v=G_glPIl5Dro )


