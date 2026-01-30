# AdSellix Premium AI Audit Framework
## Version 1.0 — Proprietary Methodology

---

## Table of Contents
1. [Audit Philosophy](#audit-philosophy)
2. [Data Requirements](#data-requirements)
3. [Audit Modules](#audit-modules)
4. [Output Structure](#output-structure)
5. [Technical Architecture](#technical-architecture)
6. [Scoring Methodology](#scoring-methodology)

---

## Audit Philosophy

### The 4 Pillars of a $1,000+ Audit

| Pillar | What It Answers | Value to Client |
|--------|-----------------|-----------------|
| **Diagnostic** | What's happening? | Clarity |
| **Explanatory** | Why is it happening? | Understanding |
| **Prescriptive** | What should we do? | Action |
| **Predictive** | What will happen next? | Foresight |

### Success Definition
An audit is successful if the brand owner can:
- Understand their exact position in 5 minutes (Executive Summary)
- Make confident decisions about every ASIN (Keep/Kill Matrix)
- Execute a clear 90-day action plan
- Forecast next quarter with confidence
- Identify new opportunities they didn't know existed

---

## Data Requirements

### Required Reports (Must Have)

| Report | Source | Time Period | Purpose |
|--------|--------|-------------|---------|
| **SQP Brand View** | Brand Analytics | 13 weeks (current + LY) | Market share, search demand |
| **SQP ASIN View** | Brand Analytics | 13 weeks | ASIN-level query performance |
| **PPC Bulk Sheet** | Advertising Console | 65 days + 1 year snapshot | Campaign performance |
| **Business Reports** | Seller Central | 12 months | Traffic, conversion, sales |
| **FBA Inventory Report** | Seller Central | Current | Stock health, fees |
| **Aged Inventory Report** | Seller Central | Current | Storage fees, excess |
| **FBA Fee Preview** | Seller Central | Current | Per-unit profitability |

### Supplementary Reports (Enhanced Analysis)

| Report | Source | Purpose |
|--------|--------|---------|
| **Search Catalog Performance** | Brand Analytics | Click/conversion by ASIN |
| **Repeat Purchase Behavior** | Brand Analytics | Customer retention |
| **Market Basket Analysis** | Brand Analytics | Cross-sell opportunities |
| **Demographics** | Brand Analytics | Customer segmentation |
| **Top Search Terms** | Brand Analytics | Category trends |
| **Returns Report** | Seller Central | Product issues |

### Manual Inputs Required

| Input | Format | Purpose |
|-------|--------|---------|
| **COGS per SKU** | CSV | True profitability |
| **Landed Cost** | CSV | Margin calculation |
| **Target Margins** | % | Threshold setting |
| **Competitive ASINs** | List | Competitive analysis |
| **Business Goals** | Text | Context for recommendations |

---

## Audit Modules

### Module 1: Executive Summary (The "5-Minute Brief")

**Output:** Single-page overview for C-suite/Owner

**Components:**
1. **Brand Health Score** (1-100)
   - Composite of all module scores
   - Trend arrow (↑↓→)
   - Benchmark vs. category average

2. **Key Metrics Summary**
   - Revenue (vs. LY, vs. Target)
   - True Profit (after all fees)
   - Market Share (vs. LY)
   - Advertising Efficiency (TACoS)

3. **Top 3 Wins** (what's working)
4. **Top 3 Risks** (what needs attention)
5. **Top 3 Opportunities** (what to pursue)

6. **90-Day Impact Forecast**
   - If no action: Projected revenue/profit
   - If actions taken: Projected revenue/profit
   - Delta = Value of action

---

### Module 2: Market Position Analysis

**Purpose:** Understand where you stand vs. competition

**2.1 Market Share Analysis (from SQP)**

```
For each top query:
├── Total Market Search Volume
├── Your Impression Share %
├── Your Click Share %
├── Your Purchase Share %
├── Trend (WoW, MoM, YoY)
└── Gap Analysis (Click Share - Purchase Share)
```

**Key Metrics:**
- **Search Demand Trend**: Is the market growing or shrinking?
- **Share of Voice**: Your impressions / Total impressions
- **Share of Click**: Your clicks / Total clicks
- **Share of Purchase**: Your purchases / Total purchases
- **Conversion Gap**: If click share > purchase share → listing issue
- **Visibility Gap**: If purchase share > impression share → need more visibility

**Analysis Questions:**
1. Which queries are you winning? (Purchase share > Click share)
2. Which queries are you losing? (Purchase share < Click share)
3. Where is market demand increasing but your share decreasing?
4. Where are you over-indexed (opportunity to reduce spend)?

**2.2 Competitive Position**

```
For top 10 queries:
├── Your rank (organic + sponsored)
├── Competitor ranks
├── Price comparison
├── Rating comparison
├── Review count comparison
└── Content quality score
```

**Output:** Competitive positioning matrix

---

### Module 3: Product Portfolio Analysis

**Purpose:** Decide what to keep, kill, invest in, or launch

**3.1 SKU Profitability Matrix**

```
For each ASIN:
├── Revenue (T12M, T3M, Current Month)
├── Units Sold
├── COGS
├── FBA Fees (pick & pack, storage, inbound)
├── Advertising Cost
├── Referral Fee
├── Returns Cost
├── True Contribution Margin
├── Margin Trend (improving/declining)
└── Days of Inventory
```

**Classification:**
- **Stars** (High margin, High growth): Invest
- **Cash Cows** (High margin, Low growth): Maintain
- **Question Marks** (Low margin, High growth): Optimize or exit
- **Dogs** (Low margin, Low growth): Exit

**3.2 Keep/Kill Decision Matrix**

| Factor | Weight | Scoring |
|--------|--------|---------|
| Contribution Margin | 25% | >30%: 5, 20-30%: 4, 10-20%: 3, 0-10%: 2, <0: 1 |
| Revenue Trend (YoY) | 20% | >20%: 5, 10-20%: 4, 0-10%: 3, -10-0%: 2, <-10%: 1 |
| Market Share Trend | 15% | Growing: 5, Stable: 3, Declining: 1 |
| Review Velocity | 10% | >10/mo: 5, 5-10: 4, 2-5: 3, 1-2: 2, <1: 1 |
| Rating | 10% | >4.5: 5, 4.2-4.5: 4, 4.0-4.2: 3, 3.5-4.0: 2, <3.5: 1 |
| Inventory Health | 10% | 30-60 days: 5, 60-90: 4, 15-30: 3, 90-120: 2, <15 or >120: 1 |
| Strategic Fit | 10% | Core: 5, Adjacent: 3, Non-core: 1 |

**Score Interpretation:**
- 4.0-5.0: **INVEST** — Increase inventory, expand ads
- 3.0-3.9: **MAINTAIN** — Keep current strategy
- 2.0-2.9: **OPTIMIZE** — Fix issues or prepare exit
- 1.0-1.9: **EXIT** — Liquidate, discontinue

**3.3 New Product Opportunities**

Based on:
- Top Search Terms with no/low competition
- High-performing queries where you have no ASIN
- Adjacent categories with strong demand
- Seasonal opportunities (upcoming events)
- Cross-sell patterns (Market Basket Analysis)

---

### Module 4: PPC Deep Dive

**Purpose:** Maximize ad efficiency and ROI

**4.1 Account Structure Audit**

```
Account Health Check:
├── Campaign Organization (Score 1-5)
│   ├── Naming conventions
│   ├── Campaign types (SP/SB/SD coverage)
│   ├── Match type segmentation
│   └── Product grouping logic
├── Targeting Efficiency (Score 1-5)
│   ├── % of spend on profitable keywords
│   ├── Negative keyword hygiene
│   ├── Search term to target ratio
│   └── ASIN targeting utilization
├── Bid Management (Score 1-5)
│   ├── Bid strategy alignment with goals
│   ├── Placement modifier usage
│   ├── Budget utilization rate
│   └── Dayparting (if applicable)
└── Coverage Analysis (Score 1-5)
    ├── % of catalog advertised
    ├── Top organic queries with no ads
    ├── Defensive brand campaigns
    └── Competitor conquest campaigns
```

**4.2 Query-Level Analysis**

```
For each search term:
├── Impressions, Clicks, Spend, Sales
├── ACoS, ROAS, CPC
├── Organic Rank (from SQP)
├── Sponsored Rank
├── SQP Click Share
├── SQP Purchase Share
├── Organic vs. Paid Sales Ratio
└── Efficiency Score
```

**Query Classification:**
- **Defend**: Branded terms, high organic rank, low ACoS
- **Attack**: Non-branded, high volume, profitable ACoS
- **Harvest**: High spend, declining returns, reduce bids
- **Test**: New terms, low data, need more time
- **Eliminate**: High spend, no conversions, negative

**4.3 Campaign Type Analysis**

| Campaign Type | Current % of Spend | Recommended % | Gap |
|---------------|-------------------|---------------|-----|
| Sponsored Products | X% | 60-70% | |
| Sponsored Brands | X% | 15-25% | |
| Sponsored Display | X% | 10-20% | |
| DSP | X% | 5-15% (if applicable) | |

**4.4 Wastage Analysis**

```
Total Ad Spend: $X
├── Profitable Spend (ACoS < Target): $X (X%)
├── Break-even Spend: $X (X%)
├── Loss-making Spend: $X (X%)
│   ├── Recoverable (optimization): $X
│   └── Eliminate (cut): $X
└── Potential Savings: $X
```

**4.5 Creative Audit (Sponsored Brands)**

For each SB campaign:
- Headline effectiveness (CTR benchmark)
- Custom image performance
- Video performance (if applicable)
- Store spotlight vs. Product collection
- Recommendations for improvement

---

### Module 5: Listing Quality Audit

**Purpose:** Maximize organic visibility and conversion

**5.1 Content Scorecard (per ASIN)**

| Element | Weight | Scoring Criteria | Score |
|---------|--------|------------------|-------|
| Title | 20% | Keyword-rich, clear, compliant, <200 chars | 1-5 |
| Bullets | 20% | Benefit-focused, keyword-rich, scannable | 1-5 |
| Images | 25% | 7+ images, infographics, lifestyle, video | 1-5 |
| A+ Content | 15% | Premium, storytelling, comparison charts | 1-5 |
| Backend Keywords | 10% | Utilized, no duplicates, relevant | 1-5 |
| Brand Story | 10% | Present, engaging, cross-links | 1-5 |

**5.2 Conversion Rate Analysis**

```
For each ASIN:
├── Session %  (Traffic share)
├── Unit Session % (Conversion rate)
├── vs. Category Average
├── vs. Last Year
├── Page Views vs. Sessions (bounce indicator)
└── Add to Cart Rate (from SQP)
```

**Low Conversion Diagnosis:**
- Price too high? (vs. competitors)
- Images poor? (first image CTR)
- Reviews too low? (<4.0 or <50)
- Content unclear? (bullets, A+)
- Out of stock history?

**5.3 Review Health**

```
For each ASIN:
├── Current Rating
├── Rating Trend (last 90 days)
├── Review Velocity (reviews/month)
├── Top Complaints (AI analysis)
├── Competitive Rating Gap
└── Review Program Eligibility (Vine, etc.)
```

---

### Module 6: Inventory & Operations Analysis

**Purpose:** Optimize cash flow and avoid costly fees

**6.1 Stock Health Dashboard**

```
Inventory Summary:
├── Total Units in FBA: X
├── Total Value: $X
├── Days of Supply (overall): X
├── Healthy (30-60 days): X units ($X)
├── Low (<30 days): X units ($X) ⚠️
├── Excess (>90 days): X units ($X) ⚠️
├── Aged (>180 days): X units ($X) 🔴
└── Long-term (>365 days): X units ($X) 🔴
```

**6.2 Fee Exposure Analysis**

| Fee Type | Current Monthly | Projected Next 3 Months | Action |
|----------|-----------------|-------------------------|--------|
| Monthly Storage | $X | $X | |
| Aged Inventory Surcharge | $X | $X | |
| Low Inventory Level Fee | $X | $X | |
| Removal/Disposal | $X | $X | |

**6.3 Restock Recommendations**

```
For each ASIN:
├── Current Stock: X units
├── Daily Velocity: X units/day
├── Days of Supply: X days
├── Lead Time: X days
├── Reorder Point: X units
├── Recommended Order Qty: X units
├── Reorder Date: [DATE]
└── Confidence Level: High/Medium/Low
```

**6.4 Liquidation Candidates**

ASINs recommended for exit:
- Aged >180 days with <30 day velocity
- Negative margin after fees
- Rating <3.5 with no fix path
- Delisted or suppressed
- Seasonal items past season

---

### Module 7: Seasonal & Trend Analysis

**Purpose:** Capitalize on upcoming opportunities

**7.1 Seasonality Patterns**

```
For each ASIN:
├── Historical monthly sales (24 months)
├── Seasonality index by month
├── Peak months identified
├── Off-peak months identified
├── YoY comparison
└── Forecast next 12 months
```

**7.2 Upcoming Events & Opportunities**

| Event | Date | Relevance | Preparation Deadline | Recommended Action |
|-------|------|-----------|---------------------|-------------------|
| Prime Day | July 2026 | High/Med/Low | May 15 | Stock +50%, Deals |
| Back to School | Aug 2026 | | | |
| Halloween | Oct 2026 | | | |
| BFCM | Nov 2026 | | | |
| Christmas | Dec 2026 | | | |
| Custom Events | | | | |

**7.3 Trend Capture Opportunities**

Based on:
- Search term trending data
- Category growth rates
- News/cultural events (e.g., World Cup 2026)
- Competitor launches
- Social media trends

Example Output:
```
🔥 TRENDING OPPORTUNITY: FIFA World Cup 2026 (June-July)
├── Relevant Products: [List ASINs]
├── Recommended New Products: [Ideas]
├── Search Terms to Target: [List]
├── Content Updates Needed: [Specifics]
├── Inventory Preparation: +X% by April
└── Ad Strategy: Launch conquest campaigns in May
```

---

### Module 8: Financial Analysis

**Purpose:** True profitability at every level

**8.1 P&L by ASIN**

```
For each ASIN:
├── Gross Revenue
├── (-) Promotions/Coupons
├── = Net Revenue
├── (-) COGS
├── (-) FBA Fulfillment Fees
├── (-) Referral Fee
├── (-) Storage Fees
├── (-) Advertising Cost
├── (-) Returns Cost
├── = Contribution Margin ($)
├── = Contribution Margin (%)
└── Trend vs. LY
```

**8.2 Unit Economics**

```
For each ASIN:
├── ASP (Average Selling Price)
├── ACoS
├── TACoS
├── True COGS (incl. landed cost)
├── Break-even ACoS
├── Current vs. Break-even Gap
└── Headroom for price reduction
```

**8.3 Cash Flow Analysis**

```
Inventory Investment:
├── Current inventory value at cost: $X
├── Turns per year: X
├── Cash cycle days: X
├── Capital tied up in slow movers: $X
└── Opportunity cost: $X
```

---

### Module 9: Strategic Roadmap

**Purpose:** Clear, prioritized action plan

**9.1 Immediate Actions (0-30 Days)**

| Action | ASIN/Area | Impact | Effort | Owner | Deadline |
|--------|-----------|--------|--------|-------|----------|
| Fix [issue] | ASIN X | High | Low | | Week 1 |
| Pause [campaign] | Campaign Y | $X/mo saved | Low | | Week 1 |
| ... | | | | | |

**9.2 Short-term Initiatives (30-90 Days)**

| Initiative | Description | Expected ROI | Resources |
|------------|-------------|--------------|-----------|
| Listing optimization | 5 ASINs | +15% CVR | Content team |
| PPC restructure | Account-wide | -20% TACoS | Ads team |
| ... | | | |

**9.3 Long-term Strategy (90+ Days)**

| Strategy | Description | Timeline | Investment |
|----------|-------------|----------|------------|
| New product launch | [Category] | Q3 2026 | $X |
| Market expansion | [Country] | Q4 2026 | $X |
| ... | | | |

**9.4 Category Expansion Recommendations**

Based on analysis:
- Market Basket (what buyers also buy)
- Search gap (queries with no products)
- Margin opportunity (high-margin adjacencies)
- Brand fit (complements positioning)

```
RECOMMENDATION: Expand into [Category]
├── Market Size: $X/year on Amazon
├── Growth Rate: X% YoY
├── Competition Level: Low/Medium/High
├── Your Advantages: [List]
├── Investment Required: $X
├── Time to Launch: X months
├── Projected Y1 Revenue: $X
└── Confidence: High/Medium/Low
```

---

### Module 10: Competitive Intelligence

**Purpose:** Understand and outmaneuver competitors

**10.1 Competitor Profiles**

```
For each main competitor:
├── Estimated Revenue (from tools)
├── Product Count
├── Avg Rating
├── Pricing Strategy
├── Ad Aggressiveness (share of voice)
├── Recent Changes (new ASINs, price changes)
├── Strengths
├── Weaknesses
└── Threat Level: High/Medium/Low
```

**10.2 Share of Voice Analysis**

| Query | Your SoV | Competitor A | Competitor B | Gap |
|-------|----------|--------------|--------------|-----|
| [keyword] | X% | X% | X% | |

**10.3 Competitive Content Comparison**

| Element | You | Competitor A | Competitor B | Winner |
|---------|-----|--------------|--------------|--------|
| Main Image | | | | |
| Title | | | | |
| Price | | | | |
| Rating | | | | |
| Review Count | | | | |
| A+ Content | | | | |

---

## Output Structure

### Deliverables

1. **Executive Summary** (2-3 pages, PDF)
   - Brand Health Score
   - Key metrics
   - Top opportunities
   - 90-day impact forecast

2. **Full Audit Report** (20-40 pages, PDF)
   - All modules with detailed analysis
   - Visualizations and charts
   - ASIN-level scorecards

3. **Action Plan** (Interactive, Notion/Sheets)
   - Prioritized tasks
   - Deadlines
   - Tracking

4. **Data Workbook** (Google Sheets)
   - Raw data with calculations
   - Keep/Kill matrix
   - Restock planner
   - Financial models

5. **Presentation Deck** (Optional, for calls)
   - 15-20 slides
   - Key findings
   - Recommendations

---

## Technical Architecture

### Recommended Stack

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│              Streamlit (Python Web App)                  │
│         - File upload (CSV/Excel)                        │
│         - Interactive filters                            │
│         - Real-time visualizations                       │
│         - PDF export                                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   ANALYSIS ENGINE                        │
│              Python (Pandas, NumPy)                      │
│         - Data cleaning & merging                        │
│         - Calculations & scoring                         │
│         - Trend analysis                                 │
│         - Forecasting (Prophet/statsmodels)              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    AI LAYER                              │
│                 Claude API                               │
│         - Natural language insights                      │
│         - Recommendation generation                      │
│         - Competitor analysis                            │
│         - Trend interpretation                           │
│         - Executive summary writing                      │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  OUTPUT GENERATION                       │
│         - PDF (ReportLab/WeasyPrint)                     │
│         - Excel (openpyxl)                               │
│         - Charts (Plotly)                                │
│         - Presentations (python-pptx)                    │
└─────────────────────────────────────────────────────────┘
```

### Hosting Options

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| **Streamlit Cloud** | Free | Easy, fast, free | Public only, limited resources |
| **Railway** | $5-20/mo | Easy deployment, good free tier | Limited customization |
| **Render** | $7-25/mo | Good for APIs | Cold starts |
| **DigitalOcean** | $5-20/mo | Full control, reliable | More setup |
| **Vercel** | Free-$20/mo | Fast, modern | Python limitations |

**Recommendation:** Start with Streamlit Cloud (free), migrate to Railway or DigitalOcean as you scale.

### API Costs

| Service | Usage | Est. Cost/Audit |
|---------|-------|-----------------|
| Claude API | ~50k tokens/audit | $0.50-2.00 |
| Total | | ~$2/audit |

**Margin:** Charge $997-1,997, cost ~$2 = 99%+ margin

---

## Scoring Methodology

### Brand Health Score (1-100)

```
Brand Health Score = Weighted Average of:
├── Market Position Score (20%)
│   └── (Impression Share + Click Share + Purchase Share) / 3 × Trend Multiplier
├── Financial Health Score (25%)
│   └── Contribution Margin × Revenue Growth Factor
├── Portfolio Health Score (15%)
│   └── % Stars + Cash Cows - % Dogs
├── Advertising Efficiency Score (15%)
│   └── (Target TACoS / Actual TACoS) × Coverage Factor
├── Listing Quality Score (10%)
│   └── Average of all ASIN content scores
├── Inventory Health Score (10%)
│   └── % Healthy Inventory - Fee Exposure Factor
└── Operational Score (5%)
    └── IPI Score / 10
```

### Trend Multipliers

- Growing (>10% YoY): 1.2x
- Stable (-10% to +10%): 1.0x
- Declining (<-10%): 0.8x

### Benchmark Interpretation

| Score | Rating | Interpretation |
|-------|--------|----------------|
| 80-100 | Excellent | Category leader, optimize for efficiency |
| 60-79 | Good | Strong position, focused improvements needed |
| 40-59 | Average | Significant opportunities, prioritize fixes |
| 20-39 | Below Average | Major issues, needs strategic overhaul |
| 0-19 | Critical | Business viability at risk, urgent action |

---

## Appendix: Report Templates

### SQP Analysis Template

```
Query: [SEARCH TERM]
─────────────────────────────────────
Market Metrics (This Week vs. Last Year)
• Total Search Volume: X (+/-Y%)
• Total Clicks: X (+/-Y%)
• Total Purchases: X (+/-Y%)

Your Performance
• Impression Share: X% (vs. Y% LY)
• Click Share: X% (vs. Y% LY)
• Purchase Share: X% (vs. Y% LY)

Funnel Analysis
• Click-through Rate: X% (vs. category avg Y%)
• Conversion Rate: X% (vs. category avg Y%)

Diagnosis:
[AI-generated insight about performance]

Recommendation:
[AI-generated action item]
─────────────────────────────────────
```

### ASIN Scorecard Template

```
ASIN: [B00XXXXXX]
Product: [PRODUCT NAME]
─────────────────────────────────────
OVERALL SCORE: X/100 [STATUS]

Financial Health
├── Revenue (T12M): $X (+/-Y%)
├── Contribution Margin: X%
├── Trend: [↑↓→]
└── Score: X/25

Market Position
├── Top Query Purchase Share: X%
├── Organic Rank (top query): #X
├── Trend: [↑↓→]
└── Score: X/25

Listing Quality
├── Content Score: X/5
├── Rating: X.X (Y reviews)
├── Image Score: X/5
└── Score: X/25

Inventory Health
├── Days of Supply: X
├── Stock Status: [Healthy/Low/Excess]
├── Fee Exposure: $X/month
└── Score: X/25

RECOMMENDATION: [INVEST/MAINTAIN/OPTIMIZE/EXIT]

Priority Actions:
1. [Action 1]
2. [Action 2]
3. [Action 3]
─────────────────────────────────────
```

---

*This specification is proprietary to AdSellix. Version 1.0.*
