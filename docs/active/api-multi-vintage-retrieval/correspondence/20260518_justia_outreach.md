# Justia outreach — research data-access request

**Date sent:** 2026-05-18
**From:** Dan Parshall (Canary Institute / Corda Democracy Fellowship)
**To:**
- Tim Stanley (CEO, co-founder) — `tim@justia.com` *(format-inferred, not verified)*
- Stacy Stern (President, co-founder) — `stacy@justia.com` *(format-inferred, not verified)*
- Marketing — `marketing@justia.com` *(belt-and-suspenders catch-all)*

**Status:** Sent, awaiting reply.

**Context for the resuming agent:** Cloudflare bot mitigation on `law.justia.com` blocked the Playwright-based statute-fetch pipeline today (handoff `20260518_fetch_2015_section_bodies.md`). After three CF widenings across the afternoon (pass-3 articles → pass-1 state indexes → single section even after IP switch), the cleanest path forward was switching from technical workarounds to direct outreach.

---

## Subject

Research collaboration on historical state-code access

## Body

> Hi Justia folks,
>
> I'm guessing you get more "will you cooperate with my scraping" emails than you'd like, but I think this one is worth your time.
>
> For most primary legal work, Public.Resource.Org is our default. But PRO's archive thins out fast for historical vintages, and our project needs roughly seven snapshots per state across 2009-2025. As far as we can tell, your law.justia.com/codes/<state>/<year>/ archive is the most complete open record of dated state-code snapshots anywhere. So we're at your door rather than PRO's, and I'd rather coordinate than scrape.
>
> I'm with the Corda Democracy Fellowship working on ways to leverage AI for the public benefit. Right now I'm doing basically "LobbyView for states", extending In Song Kim's federal LobbyView model to state lobbying-disclosure data. We need the statute data to understand what's required, and to compare against prior research so we can report accuracy numbers with confidence.
>
> I found that even at 1 request per 5 seconds sequentially I'm tripping Cloudflare. I don't want to keep bouncing off your bot mitigation, and you presumably don't want our traffic showing up in your logs as scrape attempts.
>
> Three options that would solve it on our side, in rough order of what we'd guess is lowest-friction for you:
>
> 1. A bulk download of the codes/<state>/<year>/ trees you have on file (zip, S3 manifest, whatever's easiest).
> 2. A rate-limited endpoint or scraping allowlist for a registered User-Agent.
> 3. An IP whitelist with a courtesy rate limit we'd agree to in advance.
>
> In exchange: explicit Justia acknowledgment in any publications and in the open-source repo, a copy of the final extraction outputs if useful to you, and whatever data-use agreement makes sense on your end.
>
> Happy to scope this by email or on a short call. Either way, thanks for keeping the archive open. It's one of the more usable corners of the legal web.
>
> Take care,
>
> Dan Parshall
>
> ---
> Daniel Parshall, Ph.D.
> Canary Institute
> dan@canaryinstitute.ai

---

## Notes

- **Voice iteration generated VOICE.md updates** (M5 compression, Inv 1 empirical-findings extension, Inv 3 audience-calibrated specificity, A15 performed similarity, A16 press-release register ban) at `~/code/dotfiles/nori-researcher/VOICE.md`. The first LLM draft and Dan's revision are diffed in this session's chat log.
- **If tim@ and stacy@ bounce:** fall back to General Info phone `650-810-1990` or the contact form at `justia.com/marketing/contact/` (lawyer-marketing arm, will need explicit "please route to Tim Stanley / Stacy Stern re: research data-sharing inquiry").
- **If a reply comes back routing us to a specific person/team:** update this file and create a follow-up correspondence record for the thread.
