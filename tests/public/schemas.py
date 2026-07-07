"""Pydantic models for public market-data API responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class BinanceExchangeInfoSymbol(BaseModel):
    symbol: str
    status: str
    baseAsset: str
    quoteAsset: str


class BinanceExchangeInfo(BaseModel):
    timezone: str
    serverTime: int
    symbols: list[BinanceExchangeInfoSymbol]


class BinanceOrderBook(BaseModel):
    lastUpdateId: int
    bids: list[list[str]]
    asks: list[list[str]]

    @field_validator("bids", "asks", mode="before")
    @classmethod
    def ensure_lists(cls, value: Any) -> Any:
        if not isinstance(value, list):
            raise ValueError("must be a list")
        return value[:5]


class BinanceTicker24hr(BaseModel):
    symbol: str
    priceChange: str
    priceChangePercent: str
    weightedAvgPrice: str
    lastPrice: str
    lastQty: str
    bidPrice: str
    askPrice: str
    openPrice: str
    highPrice: str
    lowPrice: str
    volume: str
    quoteVolume: str


class BinanceTrade(BaseModel):
    id: int
    price: str
    qty: str
    quoteQty: str
    time: int
    isBuyerMaker: bool
    isBestMatch: bool = True


class OkxRestResponse(BaseModel):
    code: str
    msg: str = ""
    data: list[dict[str, Any]]

    @field_validator("code", mode="before")
    @classmethod
    def code_as_string(cls, value: Any) -> str:
        return str(value)


class OkxTicker(BaseModel):
    instType: str
    instId: str
    last: str
    bidPx: str | None = None
    askPx: str | None = None
    open24h: str | None = None
    high24h: str | None = None
    low24h: str | None = None
    volCcy24h: str | None = None
    vol24h: str | None = None
    ts: str


class OkxTrade(BaseModel):
    instId: str
    side: str
    sz: str
    px: str
    tradeId: str
    ts: str
