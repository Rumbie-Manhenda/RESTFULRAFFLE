# Restful raffle
![Screenshot 2024-08-20 024801](https://github.com/user-attachments/assets/ed9fc574-b02c-44a1-962a-cd282e0b8ca4)

## Getting started

### Setup and Configuration

1. Created and activated a virtual environment named `raffleEnv` to isolate project dependencies with `python -m venv raffleEnv`.
2. Installed the required packages listed in `requirements.txt` using `pip install -r requirements.txt`.
3. Created a new Django application named `raffle` using `python manage.py startapp raffle`.
4. Added necessary app files: `serializers.py`, `permissions.py`, `urls.py`, `utils.py`, `exceptions.py`, `logging_utils.py`, and `signals.py`.

#### Testing

1. Updated the `test_raffle_list` function in `raffle_retrieval_tests.py` to handle paginated responses.
2. Created additional tests to cover all the listed requirements.
3. Added a fixture in `conftest.py` to disable caching during testing.
```python 

python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt
export MANAGER_IPS=123.123.123.123,127.0.0.2
pytest
python manage.py runserver
```



## Requirements

* The raffle manager creates a new raffle specifying the number of tickets and the prizes.
* Ticket numbers for each raffle are sequential starting from `1`. I.e. if a raffle has 50 tickets total, the ticket numbers must be `1, 2, ..., 49, 50`. 
* The raffle tickets are be given out to participants requesting them in a non-sequential order.
* The raffle tickets contain a verification code, that can be used to validate the ticket (e.g. when redeeming prizes).
* The application does not save the verification codes in plaintext.
* The same ticket number is never given out to multiple participants of a raffle.
* One ip address may not participate in a raffle more than once.
* When no raffle tickets are remaining, the raffle manager draws the winners. 
* The winners must not be pre-determined.
* One raffle ticket can't win more than one prize.
* Access to the raffle manager endpoints is only allowed from ips listed in the `MANAGER_IPS` environment variable.
* The application performance should not severly degrade with a large number of raffle tickets, prizes and participants.


## API endpoints

| Endpoint                            | Description                       | Manager only |
|-------------------------------------|-----------------------------------|:------------:|
| `POST /raffles/`                    | Create a new raffle               |     Yes      |
| `GET /raffles/`                     | List raffles starting from latest |      No      |
| `GET /raffles/<id>/`                | Get details of a raffle           |      No      |
| `POST /raffles/<id>/participate/`   | Get a raffle ticket               |      No      |
| `POST /raffles/<id>/winners/`       | Draw winners of a raffle          |     Yes      |
| `GET /raffles/<id>/winners/`        | List winners of a raffle          |      No      |
| `POST /raffles/<id>/verify-ticket/` | Verify ticket and winnings        |      No      |

**[Raffle Website Demo](https://youtu.be/G_glPIl5Dro?si=DmiIH3oQ4esYO0BF)**
