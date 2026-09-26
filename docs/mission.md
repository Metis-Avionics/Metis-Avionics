# Mission

Mētis (Μῆτις) in Greek is not wisdom. It is the quality of being resourceful,
of learning fast, of adapting before the situation requires it. It is
intelligence as a verb rather than a possession. That is the whole idea, and
everything below is downstream of it.

## Why an avionics company

We call ourselves an avionics company. The reality underneath that name is a
hardware-and-software common problem: intelligence. Not the "AI product"
version of the word — the engineering capacity to model a physical situation,
know what you do not know about it, and act before the situation has finished
happening.

So the work touches avionics, aerospace, simulation, guidance/navigation/
control, embedded systems, systems engineering, and the engineering
infrastructure all of that requires.

## Dual technology

We build dual-use technology. We do not apologise for it and we do not
launder it: dual-domain capability is not a covert agenda, it is a property of
the engineering.

We also do not accept responsibility for how a third party misuses what we
publish. The line we do hold: build it openly, document its real limits, and do
not hand anyone a system that pretends to be safe when it is not.

## Open source intelligence

The intelligence stance of Mētis Avionics is that open source intelligence
should be freely available, as well as responsibly used. Openness is the
delivery mechanism, not a marketing position: a capability that only the author
can audit is not one anybody else can rely on.

## What follows from this

Three commitments, stated here because they constrain engineering decisions:

1. **Determinism.** The same inputs produce the same outputs, or the system is
   wrong. No hidden clocks, no ambient state, no unreproducible randomness.
2. **Explicit boundaries.** A stated limit is worth more than an implied one.
   Every system in this organisation carries a safety boundary naming what it
   must never do. `seven` was the first, and the boundary was the first thing in
   its README for a reason.
3. **Documentation that matches reality.** If a document and the code disagree,
   that is a defect in the document. It gets recorded as a discrepancy, not
   quietly reconciled in the direction that looks better.

## Provenance

Adapted from the organisation statement *The purpose of Metis Avionics*
(metis.md), which was written as prose and is recorded here in structured form.
No organisational structure, repository or project is derived from this page.
Where this page and [`spec.toml`](../spec.toml) disagree, `spec.toml` is
authoritative.
