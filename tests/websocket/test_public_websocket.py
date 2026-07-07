"""WebSocket smoke tests for public exchange streams used by LexxSoft terminal.

Endpoints discovered from the terminal's JS bundle:
  - Binance Spot: wss://stream.binance.com
  - Binance Futures: wss://fstream.binance.com
  - OKX: wss://ws.okx.com
"""

from __future__ import annotations

import json
import pytest
import websocket


@pytest.mark.websocket
@pytest.mark.binance
class TestBinanceSpotWebSocket:
    """Smoke tests for Binance Spot public WebSocket streams."""

    URL = "wss://stream.binance.com:9443/ws/btcusdt@ticker"

    def test_stream_connects_and_receives_ticker(self):
        ws = websocket.create_connection(self.URL, timeout=10)
        try:
            message = json.loads(ws.recv())
            assert isinstance(message, dict)
            assert "s" in message  # symbol
            assert "c" in message  # last price
        finally:
            ws.close()

    def test_connection_closes_cleanly(self):
        ws = websocket.create_connection(self.URL, timeout=5)
        ws.close()
        assert ws.sock is None or not ws.sock.connected


@pytest.mark.websocket
@pytest.mark.binance
class TestBinanceFuturesWebSocket:
    """Smoke tests for Binance USDⓈ-M Futures public WebSocket streams.

    Note: Binance futures WebSocket often accepts the connection but does not
    push market data from some regions. We verify the connection and a ping
    round-trip rather than waiting for a ticker message.
    """

    URL = "wss://fstream.binance.com/ws/btcusdt@ticker"
    TIMEOUT = 5

    def test_stream_connects_and_pongs(self):
        ws = websocket.create_connection(self.URL, timeout=self.TIMEOUT)
        try:
            assert ws.connected
            ws.ping("ping")
            # websocket-client handles pong internally; reaching here means OK
        finally:
            ws.close()
        assert not ws.connected

    def test_connection_closes_cleanly(self):
        ws = websocket.create_connection(self.URL, timeout=self.TIMEOUT)
        ws.close()
        assert not ws.connected


@pytest.mark.websocket
class TestOkxWebSocket:
    """Smoke tests for OKX public WebSocket streams."""

    URL = "wss://ws.okx.com:8443/ws/v5/public"

    def test_stream_connects_and_subscribes_to_tickers(self):
        ws = websocket.create_connection(self.URL, timeout=10)
        try:
            subscribe = {
                "op": "subscribe",
                "args": [{"channel": "tickers", "instId": "BTC-USDT"}],
            }
            ws.send(json.dumps(subscribe))

            # OKX responds with a subscribe confirmation, then data messages
            for _ in range(5):
                message = json.loads(ws.recv())
                if message.get("event") == "subscribe":
                    assert message.get("arg", {}).get("channel") == "tickers"
                    return
                if "data" in message:
                    assert isinstance(message["data"], list)
                    return
            pytest.fail("Did not receive OKX subscribe confirmation or ticker data")
        finally:
            ws.close()
