from .conftest import unexpected_response_error


class TestParticipate:
    def test_get_ticket(self, client, raffle):
        """Get a ticket to participate in a raffle"""

        resp = client.post(f"/raffles/{raffle['id']}/participate/")
        assert resp.status_code == 201, unexpected_response_error(resp)
        data = resp.json()
        assert data["raffle_id"] == raffle["id"]
        assert 1 <= data['ticket_number'] <= raffle['total_tickets']
        assert bool(data['verification_code']) is True

    def test_get_ticket_none_left(self, client, raffle, get_ticket, ip_factory):
        """Can't get a ticket if none are left"""

        for n in range(raffle['total_tickets'] - 1):
            get_ticket(raffle['id'])

        resp1 = client.post(f"/raffles/{raffle['id']}/participate/",
                            REMOTE_ADDR=ip_factory)
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        resp2 = client.post(f"/raffles/{raffle['id']}/participate/",
                            REMOTE_ADDR=ip_factory)
        assert resp2.status_code == 410, unexpected_response_error(resp2)
        assert b'Tickets to this raffle are no longer available' in resp2.content

    def test_get_second_ticket_from_same_ip(self, client, raffle):
        """Same same ip can't get more than one ticket to a rafffle"""

        resp1 = client.post(f"/raffles/{raffle['id']}/participate/",
                            REMOTE_ADDR='234.234.234.234')
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        resp2 = client.post(f"/raffles/{raffle['id']}/participate/",
                            REMOTE_ADDR='234.234.234.234')
        assert resp2.status_code == 403 or b'Your ip address has already participated in this raffle' in resp2.content, unexpected_response_error(resp2)
        

    def test_get_tickets_to_different_raffles_from_same_ip(self, client, raffle_factory):
        """Same ip can participate in multiple raffles"""
        participant_ip = '234.234.234.234'
        raffle1 = raffle_factory()
        raffle2 = raffle_factory()
        resp1 = client.post(f"/raffles/{raffle1['id']}/participate/",
                            REMOTE_ADDR=participant_ip)
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        resp2 = client.post(f"/raffles/{raffle2['id']}/participate/",
                            REMOTE_ADDR=participant_ip)
        assert resp2.status_code == 201, unexpected_response_error(resp2)
