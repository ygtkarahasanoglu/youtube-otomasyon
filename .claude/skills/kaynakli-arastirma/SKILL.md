---
name: kaynakli-arastirma
description: Researches a business topic with sourced facts and numbers (annual reports, SEC filings, earnings calls, government and trade statistics, reputable press), labels evidence levels, builds cost breakdowns that add up, and writes arastirma.md. Use before every script.
---

# Sourced research → `videolar/<folder>/arastirma.md`

1. **Questions:** write the 3 questions the video answers.
2. **Sources:** search, then OPEN each page you use (WebFetch); a search snippet is not a source. Priority: company filings (10-K, annual report, investor deck) → regulators/statistics (SEC, BLS, Census, Eurostat, UN Comtrade, USDA) → industry bodies → reputable press (Reuters, Bloomberg, FT, WSJ, CNBC) → others.
3. **Fact table** (every number the script may use):
   | # | Fact | Value | Evidence (exact / sourced estimate / unknown) | Source (title + URL) | Date |
4. **Cost breakdown** (every video's Cost Tower): for a megaproject: land/reclamation, design & engineering, materials (steel, concrete, rock), heavy equipment, labour, financing, overruns vs original budget, who paid (state, private, loans); for a ship/yacht build: hull & structure, propulsion/engines, systems, interior & joinery, deck (teak), stainless & hardware, glass, electronics, paint, labour, yard margin, design/naval architecture; for a year of ownership: crew, berth, fuel, insurance, maintenance & refit reserve, management, taxes; for a product: materials, manufacturing, freight, duties, distribution, margin. Leave an empty 'Owner review' section at the end; the Channel Manager fills it after asking the owner (CLAUDE.md rule 8). Use ranges from ≥2 sources where possible, choose a midpoint, label "estimate". Components must add up to the shelf price; put the remainder into an honest "retail & other" item.
5. **Insider notes:** 2-3 procurement/supply-chain insights (MOQ, landed cost, freight terms, supplier concentration, payment terms) that add original value. State them as analysis, not as personal anecdotes.
6. **Risks:** contested claims, outdated numbers, legal sensitivity (say "reported", attribute claims).
7. **Competitor notes** (from viral-tarama/transkript-cek): what top videos covered and missed.

Never invent numbers, quotes or sources. If something can't be verified, the script must avoid it or label it clearly.
