import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_prototype import load  # noqa: E402
from prototype_data import (  # noqa: E402
    build_mock_data,
    client_detail_href,
    event_thread_href,
    serialize_mock_data_js,
)


class PrototypeDataContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load()
        cls.data = build_mock_data(cls.rows)

    def test_client_detail_href_uses_uid_query(self):
        self.assertEqual(client_detail_href("12345"), "client-detail.html?uid=12345")

    def test_event_thread_href_uses_event_query(self):
        self.assertEqual(event_thread_href("evt-001"), "event-thread.html?event=evt-001")

    def test_build_mock_data_contains_clients_and_events(self):
        self.assertEqual(len(self.data["clients"]), len(self.rows))
        self.assertGreaterEqual(len(self.data["events"]), 8)
        self.assertIn(self.data["defaultClientUid"], self.data["clientsById"])
        self.assertIn(self.data["defaultEventId"], self.data["eventsById"])

    def test_all_events_reference_known_clients(self):
        client_ids = set(self.data["clientsById"])
        for event in self.data["events"]:
            self.assertIn(event["clientUid"], client_ids)
            self.assertEqual(event["href"], event_thread_href(event["id"]))
            self.assertEqual(event["thread"]["id"], event["id"])
            self.assertEqual(event["thread"]["clientUid"], event["clientUid"])

    def test_related_event_ids_resolve_to_same_client(self):
        for client in self.data["clients"]:
            for event_id in client["relatedEventIds"]:
                event = self.data["eventsById"][event_id]
                self.assertEqual(event["clientUid"], client["uid"])

    def test_js_payload_exports_window_contract(self):
        payload = serialize_mock_data_js(self.data)
        self.assertIn("window.PROTOTYPE_DATA", payload)
        self.assertIn(self.data["defaultClientUid"], payload)
        self.assertIn(self.data["defaultEventId"], payload)


if __name__ == "__main__":
    unittest.main()
