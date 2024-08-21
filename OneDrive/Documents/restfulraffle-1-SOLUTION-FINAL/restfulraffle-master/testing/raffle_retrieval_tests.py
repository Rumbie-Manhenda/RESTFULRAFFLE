from .conftest import unexpected_response_error


def test_raffle_list(client, raffle_factory):
    """List raffles sorted by creation time in descending order"""
    """
    I updated test_raffle_list to handle paginated responses:
    - Checks for empty 'results' and zero 'count' when no raffles exist
    - Verifies correct 'count' and order of raffles in 'results' after creating raffles
    - Accommodates pagination structure while still ensuring proper sorting by creation time
    """
    resp = client.get("/raffles/")
    assert resp.status_code == 200, unexpected_response_error(resp)
    data = resp.json()
    assert data['count'] == 0
    assert data['results'] == []

    raffle_factory(name="Foo")
    raffle_factory(name="Bar")
    raffle_factory(name="Glue")
    resp = client.get("/raffles/")
    data = resp.json()
    assert data['count'] == 3
    assert ['Glue', 'Bar', 'Foo'] == [raffle["name"] for raffle in data['results']]



def test_raffle_detail(client, raffle_factory, get_ticket):
    """Get raffle details by id counting available tickets"""

    raffle = raffle_factory(name="Barfoo", total_tickets=20)
    resp = client.get(f"/raffles/{raffle['id']}/")
    assert resp.status_code == 200, unexpected_response_error(resp)
    data1 = resp.json()
    assert data1["name"] == "Barfoo"
    assert data1["total_tickets"] == 20
    assert data1["available_tickets"] == 20
    assert data1['winners_drawn'] is False

    get_ticket(raffle['id'])

    data2 = client.get(f"/raffles/{raffle['id']}/").json()
    assert data2["total_tickets"] == 20
    assert data2["available_tickets"] == 19
    assert data2['winners_drawn'] is False
