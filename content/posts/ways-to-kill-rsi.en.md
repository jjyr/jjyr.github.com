---
title: "Some Ways to Kill RSI in the Future"
date: 2026-09-26T19:27:42+08:00
draft: true
---

![Human Wage vs AI Cost](/images/way-to-kill-rsi.jpg)

## RSI Ascension

When discussing AGI, a frequently heard term lately is RSI (Recursive Self-Improvement).

The core concept is simple: improvements made to an AI can be reinvested into further improving the AI itself.

Expanding on this, each leap in an AI model produces new intelligence; this heightened intelligence in turn accelerates human productivity across various industries, and those efficiency gains can then be funneled back through semiconductors, model R&D, and clean energy into the next iteration of AI models.

This self-reinforcing feedback loop got me thinking: what natural process can serve as an analogy for RSI?

I was reminded of rabbit reproduction: rabbits mature very quickly, and offspring immediately become "breeding tools" for the next round. Starting with just two rabbits, they can overrun an entire island in just a few cycles. However, this analogy only captures AI's ability to replicate, not to self-improve. The 100th generation of rabbits possesses no greater capabilities than the original pair—there are simply more of them.

Instead, a recent *Resident Evil* movie made me realize that RSI is much closer to the G-Virus in the franchise. The G-Virus continuously drives its host to mutate. Every time you encounter the boss in the game, you find it has undergone another round of RSI, evolving from form G1 all the way to G5, with both its physical form and destructive power leaping to the next tier.

Yet anyone who has played the games knows that this mutation comes at a steep price. The initial mutations make the boss exponentially more powerful, but by its final G5 form, it fails to achieve perfection. Instead, it turns into an overgrown, grotesque blob of flesh unable to support its own skeletal structure, ultimately choked by its own energy consumption and wedged inside a narrow tunnel. Fictional as the plot may be, it conforms surprisingly well to natural constraints.

What would happen if AI, like the G-Virus, attempted continuous self-iteration?

## The Replay of Moore's Law and the Real-World Closed Loop

The manifestation of RSI in the physical world actually looks remarkably like the trajectory of Moore's Law in semiconductors.

However, the self-iteration of intelligence is not a pure software loop floating in a vacuum; it must rely on real-world commerce and energy conversion:

![RSI Economic](/images/rsi-economic-loop.svg)

Much like Moore's Law today, gains initially came from sustained investments in fabrication processes, later shifting to algorithmic improvements and architectural breakthroughs—which is precisely the phase we are in now. When it will finally plateau in the future remains unknown.

Yet this exponential growth is clearly constrained by external factors. Once the low-hanging fruit has been picked, solving far harder problems becomes necessary to reach the fruit hanging higher up. Doubling performance each time demands ever-increasing resources—such as relying on TSMC's manufacturing ecosystem to build new chips, or requiring next-gen EDA tools to design 3D stacking. This shift—from merely packing more transistors to wrestling with complex lithography, 3D stacking, and architectural overhauls—fundamentally drives up technical complexity, as well as R&D and manufacturing costs.

The same applies to AI advancements. Intelligence improvements inevitably run into the physical limits of hardware and artificial neurons. As parameter counts surge, larger hardware clusters are needed to run them; much like human industrial production, the greater the concentration, the stronger the economies of scale.

Naturally, local edge models will continue to evolve, but constrained by hardware limits and economies of scale, the cost of on-device computation will consistently exceed that of the cloud. Local hardware upgrades and architectural optimizations will bring progress, but this resembles technological diffusion. Just like manufacturing, token production follows economies of scale: advances in intelligence will manifest first in the cloud, where the economic efficiency is greatest, and the frontier of intelligence will always reside there. Frontier intelligence cannot evade massive hardware capital expenditure simply through localization.

Everything exhibiting exponential growth in nature has its limits. In the cosmic sense, the ultimate ceiling of AI is consuming all the energy in the universe (akin to the cosmic computer AC in Isaac Asimov's short story *The Last Question*). But long before reaching that point, there are several much more immediate hurdles to overcome.

In my view, most barriers are fundamentally economic: **the limits of intelligence are ultimately dictated by economics; when gains in intelligence no longer yield corresponding revenue, sustained investment becomes impossible.** As illustrated in the diagram above, if technical complexity drives costs through the roof while commercial revenue fails to keep pace, driving profits into the negative, the RSI loop will stall at a critical threshold.

## Constraint 1: Economic Factors

Does greater intelligence always yield greater returns? Suppose AI truly reaches a point in the future where it can directly replace human workers at a lower cost—will employers prioritize hiring AI?

Of course they will! Yet paradoxically, this is where the self-limiting nature of capitalism reveals itself.

**Out of concern for unemployment rates and social stability, governments will intervene and "distort" this free market.**

To prevent mass unemployment, governments typically erect formidable institutional moats:

- **Policy incentives favoring human labor**: Similar to current measures protecting local workers against undocumented labor, hiring local staff often involves mandatory quotas or corporate tax deductions and wage subsidies (for example, Singapore waiving foreign worker levies alongside state-subsidized wages, or Japan offering direct corporate tax credits for hiring and wage increases).
- **Redistribution mechanisms**: Whether through a prospective AI automation tax or Universal Basic Income (UBI) schemes targeting technological unemployment, the essence is using institutional tools to siphon off superprofits generated by technology to buffer against the shock of unemployment.

Consequently, businesses will not pursue the "optimal solution" of a purely free market. Under government tax subsidies and employment protections, the comprehensive effective cost of subsidized human labor is artificially lowered, thereby constraining enterprise spending on AI.

**Connecting this back to the flowchart, it directly throttles the [Commercial Revenue] side on the right.** Techno-optimists assume that societal wages can be transferred frictionlessly into AI API revenue. In reality, with institutional distortions and diversions, the actual cold, hard cash AI can extract from the market hits a hard ceiling. With the revenue side institutionally capped, the primary valve driving the virtuous RSI loop is constricted.

## Constraint 2: The Inherent Tension Between Cost and Intelligence

Another constraint is the escalating cost required to elevate intelligence.

As model parameters scale from billions (B) to trillions (T) and beyond, infrastructural demands surge exponentially:

- **Chips and fabrication**: Confronting the physical limits of reticle size/wafer area and astronomically expensive High Bandwidth Memory (HBM)
- **Cluster interconnects**: Communication latency across clusters spanning tens or hundreds of thousands of GPUs
- **Energy infrastructure**: Power grid capacity

Algorithms can bootstrap themselves via RSI, but in reality, **the growth of infrastructure is bounded by the laws of physics and engineering timelines**. Building a semiconductor fab takes years; expanding power grids requires lengthy regulatory approvals and construction. The evolutionary pace of these foundational layers lags far behind the runaway expansion of parameter counts. The inertia of this physical foundation can easily drag down the projected velocity of RSI.

Accompanying this is a stark commercial dilemma.

Cloud providers certainly seek to maximize profits, but the server cluster and electricity expenses required to host larger-scale, highly scalable models are astronomical. This creates a paradox: **building smarter models may actually erode the model providers' margins.** The tipping point where profit drops to zero naturally becomes a hard ceiling for scaling AI intelligence.

Breaking through these inflection points demands quantum leaps in foundational technologies: energy, semiconductor processes, analog computing, architectures, and algorithms. While AI itself will accelerate breakthroughs in these fields, that acceleration is also constrained: **we can only afford the degree of intelligence that remains economically viable.** If current operations cannot generate positive cash flow, the funding runway will snap long before underlying technical breakthroughs materialize.

In computer hardware, there is a well-known concept called the **Memory Wall**—no matter how powerful a processor's computing capability is, it eventually gets choked by sluggish memory read/write latency.

We can similarly introduce the concept of the **Carbon Wall**: **silicon intelligence wants to iterate at digital clock speeds, but it remains physically throttled by the sluggish pace of our carbon-based world.**

On the supply side, energy infrastructure, grid upgrades, and chip manufacturing remain tethered to prolonged human construction and bureaucratic approval cycles.

**Embodied AI and robotics** are viewed as the ultimate key to untying this knot. But we must acknowledge that bridging the gap from today to **robots capable of autonomous self-replication is, in itself, a colossal and daunting Carbon Wall.**

## Constraint 3: Monopoly

Without competition, an ecosystem easily settles into a long-term local optimum, much like the dodo.

Big tech has repeatedly demonstrated this throughout history: years ago, Google developed stunning chatbots like Meena and LaMDA internally, yet chose to shelve them for years to safeguard its existing search ad revenues—until OpenAI emerged to shatter the monopolistic equilibrium.

Today, driven by commercial interests and the pursuit of monopoly, players like OpenAI and Anthropic have likewise begun erecting barriers under the banner of safety and compliance, strictly restricting weight distribution and API use cases. Once a monopoly takes hold, the most rational commercial move is to abandon risky, massive capital investments and instead coast on existing models. Anthropic's recent Opus 5.5 model even directly restricts usage in chip design. Had open-source models like DeepSeek not emerged, one can imagine monopolists locking away even more cutting-edge technology to harvest outsized profits. They may cloak their decisions in high-minded justifications like safety, but the root cause is simply the inherent greed and monopolistic instinct of capital.

Only by allowing technology to diffuse across the entire industry—enabling more vendors to build tailored hardware and deliver cheaper AI services—can global resources be mobilized to push RSI forward and guide AI models out of capital monopoly's local optimum.

## The Local Optimum

Recapping the factors mentioned earlier:
- **Constraint 1**: Government policies capping AI profits
- **Constraint 2**: Physical-layer bottlenecks in chips, fabrication, and power grids
- **Constraint 3**: Capitalism's drive for monopoly and rent-seeking

Combined, these three constraints could very well lock AI firmly into a **local optimum**.

This bears a strong resemblance to aerospace technology. During the Cold War Space Race, the United States and the Soviet Union poured resources into space programs with reckless abandon, landing on the Moon in just a decade. Yet the moment the Cold War ended and governments halted those massive, return-agnostic investments, space exploration swiftly stagnated for decades.

When the evolution of AI elevates to the existential plane of national security and geopolitical rivalry, the logic of investment is no longer bound by corporate balance sheets. Much like the Moon race, state institutions can deploy sovereign balance sheets to subsidize initiatives without expecting short-term commercial returns. When such adversarial forces transcend market rationality, AI may brute-force its way past foundational technical barriers, break free from the local optimum, and reignite the stalled flywheel of RSI.

## Conclusion

There is, of course, an even simpler dilemma: humanity goes extinct before RSI can break through the Carbon Wall. However, this scenario yields few interesting conclusions, so we won't dwell on it.

The fascination of thought experiments like this lies in how they occasionally lead to counterintuitive conclusions. For instance, while interstate rivalry is generally viewed as negative, in our thought experiment, geopolitical competition and conflict can break through capitalism's resource-allocation bottlenecks—rendering it, paradoxically, a boon for AI progress.
