# NYC Tech Events — Data Quality Report
- Total rows: **12**
- Missing → title:0, date:0, url:0, platform:0
- Dates not in Oct 2025: **0**
- Bad domains: **0**
- Duplicates: **0 keys** (across 0 rows)
- URL status sample: **{200: 12}**
- Non-techy titles (heuristic): **4**
- By platform: **{'Eventbrite': 12}**
- **Quality Score:** **100 / 100**

## Notes
- Dates strictly validated against **October 2025**.
- Trusted domains: `eventbrite.*`, `lu.ma`.
- Duplicates computed over `(title, date, platform)`.
- URL health checked via HEAD/GET on a small sample for politeness.