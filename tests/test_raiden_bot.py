from json import loads

from logic import Payment
from raiden_bot import parse_received_payments


sample_data = """
[
    {
        "event": "EventPaymentSentFailed",
        "log_time": "2020-01-15T17:57:56.834000",
        "reason": "there is no route available",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "event": "EventPaymentSentFailed",
        "log_time": "2020-01-15T17:58:05.887000",
        "reason": "there is no route available",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "1",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "17",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:24:26.341000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "3",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "19",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:27:17.663000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "42",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "22",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:27:32.583000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "66",
        "event": "EventPaymentSentSuccess",
        "identifier": "31",
        "log_time": "2020-01-16T10:11:42.455000",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    }
]
"""


partner_address = "0x61Be41317a57D1C869CDf612A4e47745b189DBde"
token_address = "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
expected_payments = {
    Payment(sender=partner_address, token=token_address, amount=1),
    Payment(sender=partner_address, token=token_address, amount=3),
    Payment(sender=partner_address, token=token_address, amount=42)
}


def test_parse_received_payments():
    records = loads(sample_data)
    payments = parse_received_payments(records)
    assert set(payments) == expected_payments
