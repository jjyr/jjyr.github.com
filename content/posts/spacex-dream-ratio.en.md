---
title: "SpaceX's Price-to-Dream Ratio"
date: 2026-06-14T21:44:02+08:00
draft: false
---

An attempt at valuing SpaceX.

SpaceX runs diverse businesses, broadly grouped into the following segments:

- Space: Rocket launch and aerospace operations
- Connectivity: Starlink network services
- AI: Formerly xAI operations

2026 Q1 Revenue Breakdown

| Business Segment | 2026 Q1 Revenue | Share |
| --- | --- | --- |
| Space | $619M | 13.2% |
| Connectivity | $3,257M | 69.4% |
| AI | $818M | 17.4% |
| Total | $4,694M | 100% |

Annualizing Q1 revenue yields approximately $13.8B. Based on the closing share price on its June 12 IPO debut, SpaceX commands a market capitalization of around $2.1T.

Calculating the Price-to-Sales (P/S) multiple:

- Valuation / Annual Sales = ~152x P/S
- By comparison, Tesla currently trades at ~15x P/S

Looking strictly at SpaceX's existing businesses, this clearly cannot support a $2.1T market cap.

## Future Horizons: Terafab and Orbital Data Centers

Beyond operational businesses, SpaceX has more "in the sky" ventures. The two most commercially promising are tied directly to AI:

- Terafab: Ultra-scale semiconductor fabrication
- ODC: Orbital Data Centers

SpaceX's "Price-to-Dream Ratio" is largely anchored by these two bets.

Terafab is in its infancy. Estimating how many years it will take to rival TSMC and generate meaningful profits is nearly impossible today; a viable prototype is likely 3 to 5 years out.

The second frontier is ODC—space-based data centers. While sounding like sci-fi, Starlink's commercial viability and scale prove SpaceX's engineering chops in orbital infrastructure. SpaceX is not alone: Google launched [Project SunCatcher](https://research.google/blog/exploring-a-space-based-scalable-ai-infrastructure-system-design/) in 2025 to explore space-based TPU data centers, planning two TPU-equipped prototype satellites in early 2027. Musk cited 2028 for commercial deployment—a remarkably aligned timeline. ODC might arrive sooner than anticipated; future collaboration between Google and SpaceX is worth watching.

## The Commercial Logic of Orbital Compute

ODC combines technical imagination with commercial advantages through simultaneous "push" and "pull" dynamics.

The push comes from terrestrial AI infrastructure constraints.

Hyperscalers scaling compute no longer just procure GPUs—they must solve facility construction, power availability, and time-to-power concurrently. Gigawatt-scale data centers demand land, buildings, cooling, switchgear, and substations, alongside locking in long-term power purchase agreements (PPAs), nuclear, natural gas, geothermal, or SMR projects.

Expanding terrestrial compute incurs the cost of an entire physical infrastructure stack, not just silicon.

The pull comes from the alternative value ODC offers.

If SpaceX can hoist AI compute into orbit powered by solar arrays and cooled by radiative dissipation into deep space, it can theoretically bypass facility construction, decouple from terrestrial grid constraints, and dramatically slash time-to-power.

For hyperscalers, the scarcest resource is often not the cheapest kilowatt-hour, but how quickly they can activate usable gigawatt-scale compute.

Thus, ODC's commercial thesis extends beyond "cheaper power in space." It leverages launch cadence, satellite manufacturing, and Starlink mesh connectivity to substitute for data center construction costs, power infrastructure capital, and protracted grid interconnection delays.

Removing terrestrial power bottlenecks could inflate demand further. We set that aside for now to avoid overly bullish assumptions pushing valuation beyond $5T. Hyperscalers have largely spent down reserves and begun levering up balance sheets; capital constraints may temper expansion before AI yields substantial new profits. We assume demand grows steadily without runaway hyper-expansion.

## Estimating the Demand Side

We can estimate the total addressable market directly from hyperscaler demand: capital previously committed to physical facilities and power contracts could be partially reallocated to SpaceX's ODC.

We evaluate capital expenditures from AWS, Google, Azure, and Meta on data centers and power commitments over the past three years, then project forward demand.

| Company | Public Data Center Project Capex |
| --- | --- |
| Google | ~$5.3B |
| Microsoft | ~$6.8B |
| AWS | ~$41.0B |
| Meta | ~$10.0B (excl. Blue Owl) |
| Total | ~$63.1B |
| Incl. Meta Blue Owl | ~$90.1B |

Public commitments indicate ~$90B spent over three years, averaging $30B annually.

Power capital intensity varies widely; we adopt industry estimates:

| Generation Type | Estimated Capital Intensity |
| --- | --- |
| Gas Turbine / CCGT | ~$1M–$2M / MW |
| Solar PV | ~$1M / MW (low capacity factor) |
| Wind | ~$1.5M–$2M / MW |
| Battery Storage (BESS) | Variable by duration |
| Nuclear / SMR | Likely $5M–$10M+ / MW |
| Transmission / Interconnection | Highly project-specific |

Assuming $4M/MW represents a blended median cost for comprehensive power delivery.

We model optimistic demand growth—driven by autonomous driving and robotics foundational models—yielding a 20% annual increase in hyperscaler data center and power capex. Additionally, local opposition to power plants near metropolitan areas stalls terrestrial builds, redirecting contracts to SpaceX's ODC. Assuming SpaceX captures 50% of incremental data center + power capital, projected ODC revenue over 5 years scales as follows:

| Year | Annual Energy Demand | Total Load | New Load Added | Power Infra Capex | Facility Capex | Total Addressable Pool | SpaceX Revenue (50%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Year 1 | 185.4 TWh | 21.16 GW | +3.53 GW | $14.1B | $30.7B | $44.8B | $22.4B |
| Year 2 | 222.5 TWh | 25.40 GW | +4.23 GW | $16.9B | $36.8B | $53.7B | $26.9B |
| Year 3 | 267.0 TWh | 30.48 GW | +5.08 GW | $20.3B | $44.2B | $64.5B | $32.3B |
| Year 4 | 320.5 TWh | 36.58 GW | +6.10 GW | $24.4B | $53.0B | $77.4B | $38.7B |
| Year 5 | 384.4 TWh | 43.89 GW | +7.32 GW | $29.3B | $63.6B | $92.9B | $46.5B |

Adding this projected ODC revenue to baseline Space and Connectivity businesses (conservatively modeled at 20% annual growth):

| Year | Space Revenue | Connectivity Revenue | ODC Revenue | Total Revenue | Implied P/S at $2.1T |
| --- | --- | --- | --- | --- | --- |
| Year 1 | $4.4B | $13.7B | $22.4B | $40.5B | 51.9x |
| Year 2 | $4.8B | $16.4B | $26.9B | $48.1B | 43.7x |
| Year 3 | $5.1B | $19.7B | $32.3B | $57.1B | 36.8x |
| Year 4 | $5.6B | $23.6B | $38.7B | $67.9B | 30.9x |
| Year 5 | $6.0B | $28.3B | $46.5B | $80.8B | 26.0x |

Even granting SpaceX a premium 30x P/S multiple—reflecting monopoly positioning and the "Musk premium"—it would take four years of flawless ODC execution to reach a valuation multiple supporting $2.1T. For buyers today, this hardly qualifies as value investing. By the time ODC matures, however, a new catalyst like Terafab may emerge to elevate valuations once again.

Much like Tesla's historical multiples, Musk companies resist simplistic P/E or P/S heuristics. But our projections suggest one conclusion: SpaceX is destined to share Tesla's trademark high volatility.
