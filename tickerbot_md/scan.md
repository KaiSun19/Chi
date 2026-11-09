# POST /v2/scan

**Run a scan**

Every ticker matching a SQL WHERE clause. Right now, or with `asof`, as of any past date.

## Body parameters

| Name | In | Type | Required | Description |
|------|----|----|----------|-------------|
| `q` | body | string | yes | SQL WHERE expression. Max 4000 chars; semicolons, comments and write keywords are rejected. Your custom signals are valid here — each expands to its SQL at run time. Example: `above_sma_200 AND market_cap > 1e10`. |
| `universe` | body | string | no | Slug of a system universe (`top_10`, `top_100`) or one of your own. Omitted, the scan runs across all ~23,391 tracked tickers. Example: `top_100`. |
| `asset_class` | body | string[] | no | One or more asset classes — slug or comma-separated list (`stocks`, `rates`, `crypto`, `fx`). Validated for shape, not against a fixed list, so a well-formed class we don't track simply matches nothing. Echoed in `query`. Example: `stocks`. |
| `asof` | body | string | no | Optional. Target moment as `YYYY-MM-DD` (that day's close) or an ISO timestamp (that intraday moment; daily-only signals then carry the previous session's close, never that day's) — the same read as it stood then, unlimited depth. Full contract under [As of a past date](/docs/asof). Example: `2026-08-06`. |
| `interval` | body | string | no | Grain the past state is read at: `1m`, `1h`, `1d`, or `auto` (default). `auto` blends: each signal comes from its freshest grain at or before the instant (minute, then hourly, then the last closed daily session), so nothing is refused for grain and no ticker is dropped; `_meta.blended` and `_meta.intervals_present` say what contributed. Pin a grain for the fastest response: one grain is read instead of three, and every ticker is captured on the same clock. A signal the pinned grain does not store is a `400 interval_unavailable` naming the grains that carry it (`rsi_14`, fundamentals and valuation ratios are `1d`-only). Only valid alongside `asof`: a live read with `interval` is a 400. Enum: `1m`, `1h`, `1d`, `auto`. Default: `auto`. |
| `columns` | body | string[] | no | Extra signals per row, ADDITIVE — the defaults are always present (ticker, name, asset_class, asset_type, price, change_1d_pct, gap_pct, relative_volume, market_cap). Example: `pe_ratio,rsi_14`. |
| `full` | body | boolean | no | Return every signal instead of the default set. Mutually exclusive with `columns` — passing both is a 400. Default: `false`. Example: `true`. |
| `group_by` | body | string[] | no | AGGREGATE MODE: 1–6 group keys (signals, expressions, or one of your custom signals as a boolean key). Results become rollup rows. Name a key with `AS` to choose its JSON key (`market_cap > 1e11 AS mega`); an un-named expression is named for you rather than returned as `?column?`. Incompatible with `columns`/`full`/`cursor`; works with `asof`. Example: `sector`. |
| `select` | body | string[] | no | Aggregate output items (requires `group_by`). Default: the group keys + `COUNT(*) AS tickers`. Supports count/avg/sum/min/max/stddev/string_agg/bool_and/bool_or plus `FILTER (WHERE …)`, and your custom signals inside expressions. Alias with `AS`; a last item without one is a 400. Example: `sector, COUNT(*) AS n, AVG(rsi_14) AS avg_rsi`. |
| `having` | body | string | no | Filter the aggregate rows (requires `group_by`). Custom signals are valid here too. Example: `COUNT(*) >= 10`. |
| `order` | body | string | no | Signal to sort by. In aggregate mode the default is the count alias `tickers` — or, with a custom `select`, the last item's alias — sorted NULLS LAST with the group keys as tiebreak. Default: `change_1d_pct`. Example: `change_1d_pct`. |
| `dir` | body | string | no | Sort direction. Enum: `asc`, `desc`. Default: `desc`. |
| `limit` | body | integer | no | Page size. Max 100. Aggregate mode does not paginate — it sets `truncated: true` when groups were cut, so sort with `order` to keep the ones you want. Default: `50`. Example: `5`. |
| `cursor` | body | string | no | Opaque cursor from the previous response's `next_cursor`. Row mode only. |

## Returns

- `as_of` (string) — Server time this response was assembled (ISO 8601).
- `query` (object) — Your query, echoed — `q`, `order`, `dir`, `limit`, and any scope.
- `_meta` (object) — Present when there is something to disclose. Row-mode scans add `null_coverage` (per signal in the predicate, how many in-scope rows are NULL and therefore never evaluated; absence from `results` means "no value", not "did not match"). Shared keys: see [the `_meta` reference](/docs/asof#meta).
- `count` (number) — Rows in this page.
- `next_cursor` (string) — Opaque token for the next page; `null` on the last page. Pass it back as `cursor`.
- `truncated` (boolean) — Aggregate mode only (`group_by`): `true` when the rollup stopped at its row cap. Aggregate responses are unpaged, so `next_cursor` is absent there.
- `results` (array) — One row per match: the default columns (listed under `columns`) plus any you named, or every signal on the [Tables page](/docs/tables) with `full`.

## Status codes

- **200** — Success — the response shape is documented under Returns above.
- **400** — `bad_request` — malformed `q`, unknown signal, invalid `order`/`dir`/`columns`, `columns` together with `full`, or an invalid cursor.
- **404** — Referenced `universe` does not exist.

## Sample response

```json
{
  "as_of": "2026-08-11T22:24:53.710Z",
  "query": {
    "q": "above_sma_200 AND market_cap > 1e10",
    "limit": 3,
    "order": "change_1d_pct",
    "dir": "desc",
    "fields": [],
    "full": false,
    "universe": null,
    "asset_class": null
  },
  "_meta": {
    "null_coverage": {
      "measured_at": "2026-08-11T22:16:47.925Z",
      "in_scope_rows": 13793,
      "columns": {
        "above_sma_200": { "null_rows": 3249, "evaluable_rows": 10544 },
        "market_cap": { "null_rows": 7871, "evaluable_rows": 5922 }
      },
      "note": "Rows NULL on a signal in the predicate are not evaluated and never match — absence here means \"no value\", not \"did not match\"."
    }
  },
  "count": 3,
  "next_cursor": "eyJhZnRlcl9vcmRlcl92YWx1ZSI6MC4xMTI4LCJhZnRlcl90aWNrZXIiOiJOQklTIn0",
  "results": [
    { "ticker": "CRWV", "name": "CoreWeave, Inc. Class A Common Stock", "asset_class": "stocks", "asset_type": "CS",   "price": 102.21, "change_1d_pct": 0.159,  "gap_pct": 0.0312, "relative_volume": 0.8872, "market_cap": 49466863271 },
    { "ticker": "SE",   "name": "Sea Limited ADS",                     "asset_class": "stocks", "asset_type": "ADRC", "price": 131.5,  "change_1d_pct": 0.1455, "gap_pct": 0.1139, "relative_volume": 2.8355, "market_cap": 69474119330 },
    { "ticker": "NBIS", "name": "Nebius Group N.V. Class A",           "asset_class": "stocks", "asset_type": "CS",   "price": 204.88, "change_1d_pct": 0.1128, "gap_pct": 0.0184, "relative_volume": 0.7351, "market_cap": 47725243526 }
  ]
}
```

## More examples

### Market breadth by sector (aggregate mode)

Request:

```shell
curl -X POST "https://api.tickerbot.io/v2/scan" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"above_sma_200 AND market_cap > 1e9","group_by":"sector","having":"COUNT(*) >= 10"}'
```

Response (`200`):

```json
{
  "as_of": "2026-08-11T22:04:00.000Z",
  "query": { "q": "above_sma_200 AND market_cap > 1e9", "group_by": "sector", "having": "COUNT(*) >= 10", "limit": 50, "order": "tickers", "dir": "desc", "universe": null, "asset_class": null },
  "count": 12,
  "results": [
    { "sector": "Financial Services", "tickers": 348 },
    { "sector": "Healthcare",         "tickers": 275 },
    { "sector": "Technology",         "tickers": 258 },
    "… (one row per sector)"
  ]
}
```

### Add a signal: P/E for large caps above trend

Request:

```shell
curl -X POST "https://api.tickerbot.io/v2/scan" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"above_sma_200 AND market_cap > 1e10","columns":"pe_ratio","limit":1}'
```

Response (`200`):

```json
{
  "as_of": "2026-08-11T23:22:44.604Z",
  "query": { "q": "above_sma_200 AND market_cap > 1e10", "limit": 1, "order": "change_1d_pct", "dir": "desc", "fields": ["pe_ratio"], "full": false, "universe": null, "asset_class": null },
  "_meta": { "null_coverage": { "…": "see the sample response above" } },
  "count": 1,
  "next_cursor": "eyJhZnRlcl9vcmRlcl92YWx1ZSI6MC4xNzY0LCJhZnRlcl90aWNrZXIiOiJDUldWIn0",
  "results": [
    { "ticker": "CRWV", "name": "CoreWeave, Inc. Class A Common Stock", "asset_class": "stocks", "asset_type": "CS", "price": 103.748, "change_1d_pct": 0.1764, "gap_pct": 0.0312, "relative_volume": 0.9153, "market_cap": 49466863271, "pe_ratio": null }
  ]
}
```

### Pagination: pass next_cursor back in the body

Request:

```shell
curl -X POST "https://api.tickerbot.io/v2/scan" \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"market_cap>300000000","order":"ticker","dir":"asc","limit":100,"cursor":"<next_cursor from the previous page>"}'
```

Response (`200`):

```json
// Next page of the same query — same envelope, with the row after the cursor.
```

## Notes

- Send `q` and the rest in a JSON body — no URL-encoding, no length limits, the same shape on every paging request. Signal names are the customer-facing ones on [the Tables page](/docs/tables); there is no translation layer.
- **Aggregate mode:** pass `group_by` and results become rollup rows instead of tickers — breadth by sector, counts of new highs, average RSI per group — shaped by `select` and filtered by `having`. Same grammar as [`/v2/news`](/docs/endpoints/news/query). Add `asof` for the same rollups as of a past date.
- `_meta.null_coverage` is the honesty block: for each signal your `q` touches it reports `null_rows` vs `evaluable_rows` out of `in_scope_rows`. A row that is NULL on a signal in the predicate is never evaluated, so it cannot match — on a market-wide scan that is routinely thousands of tickers (market_cap alone is NULL on ~10,000 of ~16,000, ETFs and funds among them), and it is the difference between "nothing qualified" and "most of the universe had no value to test".
- Custom signals: `q` may reference your custom signal names — each is expanded to its SQL before the scan runs, mixed freely with built-in signals (`q = my_squeeze AND market_cap > 1e9`). See Create a custom signal.
- Add `asof` to run the same `WHERE` against the market as it stood at a past date (the parameter above; the full contract is on [As-of](/docs/asof)).
- The response echoes your projection as `fields`. A `null` in an added signal means that ticker has no value for it (CRWV has no `pe_ratio`), not that the signal was dropped.
- Cursors carry the (order-value, ticker) pair from the last row. Sort stability is guaranteed (`ticker ASC` is the tie-breaker). Treat them as opaque — pass back the `next_cursor` you received, in the same field you sent the rest of the query.

---

Interactive sandbox + parameter editor: https://tickerbot.io/docs/endpoints/scan/run
