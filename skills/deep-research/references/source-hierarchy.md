# Source Hierarchy Reference

## Tier 1 Sources (Primary — Highest Reliability)

| Category | Examples | Navigation Pattern |
|----------|----------|-------------------|
| **Government/Regulatory** | .gov sites, SEC, central banks | Direct URL navigation |
| **Academic** | Peer-reviewed journals, ArXiv, PubMed | Search + filter by date |
| **Official Data** | World Bank, IMF, OECD, WHO | Data portals, reports |
| **Legal/Regulatory** | Court decisions, regulatory guidance | Legal databases |

```bash
# Example: SEC filings
agent-browser open https://www.sec.gov/cgi-bin/browse-edgar
agent-browser fill @companySearch "[company name]"
agent-browser click @searchBtn
agent-browser screenshot sec-results.png
```

## Tier 2 Sources (Industry Authoritative — High Reliability)

| Category | Examples |
|----------|----------|
| **Major Consulting** | Deloitte, PwC, EY, KPMG research |
| **Strategy Consulting** | McKinsey Global Institute, BCG, Bain |
| **Financial Intelligence** | Bloomberg, Reuters, FT analysis |
| **Research Firms** | Gartner, Forrester, IDC |

## Tier 3 Sources (Corroborative — Supporting Evidence)

| Category | Examples |
|----------|----------|
| **Quality Journalism** | WSJ, The Economist, HBR |
| **Industry Bodies** | Professional associations, trade orgs |
| **Corporate Intelligence** | Annual reports, 10-K filings |
| **Expert Analysis** | Verified SME commentary |

## Authenticated Sources

```bash
agent-browser state save session.json   # After login
agent-browser state load session.json   # Resume later
```
