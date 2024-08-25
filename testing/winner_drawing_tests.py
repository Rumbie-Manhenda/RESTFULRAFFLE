from .conftest import unexpected_response_error


def test_draw_winners_untrusted_ip(client, raffle, get_ticket):
    """Can't draw winners from non-manager ip address"""

    for n in range(raffle['total_tickets']):
        get_ticket(raffle['id'])

    resp = client.post(f"/raffles/{raffle['id']}/winners/")
    assert resp.status_code == 403, unexpected_response_error(resp)


def test_draw_winners_tickets_remaining(client, raffle, manager_ip, get_ticket):
    """Can't draw winners if there are still tickets available"""

    for n in range(raffle['total_tickets'] - 1):
        get_ticket(raffle['id'])

    resp = client.post(f"/raffles/{raffle['id']}/winners/",
                       REMOTE_ADDR=manager_ip)
    assert resp.status_code == 403
    assert b"Winners can't be drawn when tickets are still available" in resp.content


def test_draw_winners(client, raffle, manager_ip, get_ticket):
    """Draw winners and verify prizes"""

    for num in range(raffle['total_tickets']):
        get_ticket(raffle['id'])

    resp = client.post(f"/raffles/{raffle['id']}/winners/",
                       REMOTE_ADDR=manager_ip)
    assert resp.status_code == 201, unexpected_response_error(resp)
    wins = resp.json()
    assert len(wins) == 9

    assert len(list(filter(lambda win: win['prize'] == 'firm handshake', wins))) == 5
    assert len(list(filter(lambda win: win['prize'] == 'warm hug', wins))) == 3
    assert len(list(filter(lambda win: win['prize'] == 'invisibility', wins))) == 1

    winning_numbers = set([win['ticket_number'] for win in wins])
    assert len(winning_numbers) == 9
    assert max(winning_numbers) <= raffle['total_tickets']
    assert min(winning_numbers) >= 1
    losing_numbers = set(range(1, raffle['total_tickets'] + 1)) - winning_numbers
    assert len(losing_numbers) > 0
    assert len(losing_numbers) + len(winning_numbers) == raffle["total_tickets"]


def test_draw_winners_already_drawn(client, raffle, manager_ip, get_ticket):
    """Winners can't be drawn more than once"""

    for n in range(raffle['total_tickets']):
        get_ticket(raffle['id'])

    resp1 = client.post(f"/raffles/{raffle['id']}/winners/",
                        REMOTE_ADDR=manager_ip)
    assert resp1.status_code == 201, unexpected_response_error(resp1)

    resp2 = client.post(f"/raffles/{raffle['id']}/winners/",
                        REMOTE_ADDR=manager_ip)
    assert resp2.status_code == 403, unexpected_response_error(resp2)
    assert b"Winners for the raffle have already been drawn" in resp2.content


def test_verify_winning_tickets_winners_not_drawn(client, raffle, manager_ip,
                                                  get_ticket):
    resp = client.post(f"/raffles/{raffle['id']}/verify-ticket/",
                       {'ticket_number': 5,
                        'verification_code': 'abcd' * 8},
                       REMOTE_ADDR=manager_ip)
    assert resp.status_code == 400, unexpected_response_error(resp)
    assert b"Winners for the raffle have not been drawn yet" in resp.content
