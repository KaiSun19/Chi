# GET /v2/news

**Query news**

SQL query over the news archive. Article rows, or rollups when you group them.

## Query / path parameters

| Name            | In    | Type     | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| --------------- | ----- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `search`        | query | string   | no       | Full-text search over `title` + `summary` — websearch grammar: `apple earnings` (all words), `"price target"` (phrase), `chips OR semiconductors`, `-crypto` (negation). Max 200 chars. ANDs with `q` and the scoping params. Language-stemmed English. Example: `apple earnings`.                                                                                                                                                                                                                                                                                             |
| `q`             | query | string   | no       | WHERE clause over the news_article table. Max 4000 chars. Required UNLESS `search` or a scoping param (`ticker`/`tickers`/`universe`/`from`/`to`) is present — the simplest call needs no SQL. Queryable columns: `time_published`, `title`, `summary`, `source`, `source_domain`, `category`, `authors`, `topics`, `overall_sentiment_score`, `overall_sentiment_label`, `tickers`, `ticker_data`, `banner_image`, `url`, `id`, `created_at` — plus `tk`, the per-ticker UNNEST alias. Signal/state columns are not joinable here. Example: `overall_sentiment_score < -0.2`. |
| `ticker`        | query | string   | no       | Articles mentioning this symbol (ANDed with `q`). Example: `NVDA`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `tickers`       | query | string[] | no       | Comma list, up to 50 — articles mentioning ANY of them. Not combinable with `ticker` or `universe`. Example: `NVDA,AMD`.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `universe`      | query | string   | no       | Universe slug — articles mentioning any member. Not combinable with `ticker`/`tickers`. Example: `top_100`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `min_relevance` | query | number   | no       | With `ticker`/`tickers`/`universe`: keeps an article only when it is about one of those tickers, meaning that ticker's relevance score (`ticker_data.<TICKER>.rel`, 0 to 1) is at least this value. `0.8` drops passing mentions. Omitted: every article that mentions them. `400` without a ticker scope; inside `q`, filter `(ticker_data->'AAPL'->>'rel')::numeric >= 0.8` directly. Example: `0.8`.                                                                                                                                                                        |
| `from`          | query | string   | no       | Earliest `time_published` (inclusive) — strict ISO: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM[:SS]Z`. A bare date starts at 00:00 ET that day. Example: `2026-09-25`.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `to`            | query | string   | no       | Articles strictly before this instant — same strict ISO subset, matching `/v2/events`. A bare `YYYY-MM-DD` means through the end of that day (the ET calendar day), so `from` and `to` on the same date return that day. Example: `2026-10-23`.                                                                                                                                                                                                                                                                                                                                |
| `group_by`      | query | string[] | no       | AGGREGATE MODE: comma-separated group keys, 1-6 (max 1000 chars). Switches the response to rollup rows. Use `tk` to roll up per ticker without writing the UNNEST. Name a key with `AS` to choose its JSON key; an un-named expression is named for you rather than returned as `?column?`. Example: `tk`.                                                                                                                                                                                                                                                                     |
| `select`        | query | string[] | no       | Columns/expressions to return (max 2000 chars). Defaults to article columns (no `group_by`) or `<group_by cols>, COUNT(*) AS volume` (with `group_by`). Example: `tk, COUNT(*) AS volume`.                                                                                                                                                                                                                                                                                                                                                                                     |
| `having`        | query | string   | no       | HAVING clause on the aggregate (max 1000 chars). Requires `group_by`. Example: `COUNT(*) >= 10`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `order`         | query | string   | no       | Sort — a bare column name or SELECT alias only (put expressions in `select` and order by their alias). Defaults to `time_published` (article rows) or `volume` (aggregate rows; with your own `select` that has no `volume` column, its last column's alias). Example: `time_published`.                                                                                                                                                                                                                                                                                       |
| `dir`           | query | string   | no       | Sort direction. Enum: `asc`, `desc`. Default: `desc`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `limit`         | query | integer  | no       | Page size. Max 1000. Default: `50`. Example: `5`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `cursor`        | query | string   | no       | Opaque pagination cursor from a prior response's `next_cursor`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

## Returns

- `as_of` (string) — Server time this response was assembled (ISO 8601).
- `query` (object) — Your filters, echoed.
- `count` (number) — Rows in this page.
- `next_cursor` (string) — Opaque token for the next page; `null` on the last page, and when a custom `select` leaves out the `order` column (keep it in `select` to page). Pass it back as `cursor`.
- `truncated` (boolean) — Aggregate mode only (`group_by`): `true` when the rollup stopped at its row cap.
- `results` (array) — Article rows, or rollup rows when you passed `group_by`. Aggregate responses add `truncated: true` when `limit` cut the group list.

## Status codes

- **200** — Success — the response shape is documented under Returns above.
- **400** — `bad_request` or `invalid_query` — missing/malformed `q`, unknown column, or invalid parameter.

## Sample response

```json
{
  "as_of": "2026-08-11T22:58:32.095Z",
  "query": {
    "q": "overall_sentiment_score < -0.2",
    "tickers": ["NVDA"],
    "select": null,
    "group_by": null,
    "having": null,
    "order": "time_published",
    "dir": "desc",
    "limit": 2
  },
  "count": 2,
  "next_cursor": "eyJhZnRlcl9vcmRlcl92YWx1ZSI6IjIwMjYtMDgtMDlUMTQ6NDc6MDkuMDAwWiIsImFmdGVyX2lkIjoxNTk1MjU4fQ",
  "results": [
    {
      "id": 1597662,
      "time_published": "2026-08-10T20:15:47.000Z",
      "title": "Qualcomm Inc Stock (QCOM) Closed Down by 3.31% on Aug 10: What Investors Need To Know",
      "source": "TradingKey",
      "tickers": ["QCOM", "MU", "NVDA", "AAPL"],
      "overall_sentiment_score": -0.3435,
      "overall_sentiment_label": "Somewhat-Bearish"
    },
    "… (one row per article)"
  ]
}
```

## More examples

### How much each article is about AAPL

Request:

```shell
curl "https://api.tickerbot.io/v2/news?ticker=AAPL&min_relevance=0.8&select=id,%20time_published,%20title,%20ticker_data%20-%3E%20'AAPL'%20-%3E%3E%20'rel'%20AS%20rel&limit=2" \
  -H "Authorization: Bearer YOUR_KEY"
```

Response (`200`):

```json
{
  "as_of": "2026-10-26T20:53:23.126Z",
  "query": {
    "q": null,
    "tickers": ["AAPL"],
    "min_relevance": 0.8,
    "select": [
      "id",
      "time_published",
      "title",
      "ticker_data -> 'AAPL' ->> 'rel' AS rel"
    ],
    "group_by": null,
    "having": null,
    "order": "time_published",
    "dir": "desc",
    "limit": 2
  },
  "count": 2,
  "next_cursor": "eyJhZnRlcl9vcmRlcl92YWx1ZSI6IjIwMjYtMTAtMjNUMTg6NTA6MDMuMDAwWiIsImFmdGVyX2lkIjo0MDU3MjEzfQ",
  "results": [
    {
      "id": 4058827,
      "time_published": "2026-10-23T19:36:00.000Z",
      "title": "Apple’s Faceprints And BIPA: A New Ruling On Biometric Data And Control",
      "rel": "0.989988"
    },
    {
      "id": 4057213,
      "time_published": "2026-10-23T18:50:03.000Z",
      "title": "The 2026 Apple Mac mini just got a rare $120 discount at Amazon",
      "rel": "1"
    }
  ]
}
```

### Top tickers by article volume — single day

Request:

```shell
curl "https://api.tickerbot.io/v2/news?from=2026-08-10&to=2026-08-11&group_by=tk&order=volume&dir=desc&limit=3" \
  -H "Authorization: Bearer YOUR_KEY"
```

Response (`200`):

```json
{
  "as_of": "2026-08-11T22:58:32.284Z",
  "query": {
    "q": null,
    "from": "2026-08-10",
    "to": "2026-08-11",
    "select": null,
    "group_by": ["tk"],
    "having": null,
    "order": "volume",
    "dir": "desc",
    "limit": 3
  },
  "count": 3,
  "next_cursor": null,
  "truncated": true,
  "results": [
    { "tk": "AMD", "volume": 43 },
    { "tk": "BAC", "volume": 40 },
    { "tk": "JPM", "volume": 35 }
  ]
}
```

## Notes

- Without `group_by`, each result is one article. By default it has 7 columns (`id`, `time_published`, `title`, `source`, `tickers`, `overall_sentiment_score`, `overall_sentiment_label`); name any of the 16 columns listed under `q` in `select` to get them. With `group_by` set, results become aggregate rollups and the default SELECT becomes `<group_by cols>, COUNT(*) AS volume`. Use the `tk` alias — an auto-UNNEST of `tickers` — to roll up per ticker without writing the join.
- Same scoping sugar as `/v2/events`: `ticker`/`tickers`/`universe` and `from`/`to` AND into the WHERE clause, and `q` is optional once any of them is present — `?ticker=NVDA&from=2026-07-01` needs no SQL at all.
- There is no `asof` parameter here: "as of" is a WHERE filter on `time_published`, because every article already carries the moment it was published.
- Both `GET` and `POST` are supported; the `POST` body takes the same parameter names, for queries too long to fit in a URL.
- `/v2/news` is the canonical path — the log-shaped endpoints read uniformly (`/v2/scan`, `/v2/news`, `/v2/events`) — and the original spelling `/v2/news/scan` answers identically. The anonymous sandbox mirrors both spellings, GET and POST, with the same limits.

---

Interactive sandbox + parameter editor: https://tickerbot.io/docs/endpoints/news/query
