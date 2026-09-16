# Capture design

Decisions for the first-year pilot. A GoPro HERO10 Black takes a time-lapse photo, 23 MP, every 5 minutes.

## Uses, in priority order

1. **Night light pollution:** a qualitative "soft demo" of how the city's night glow changes over months and years.
2. **Clouds:** monitoring, and data for tuning local forecasts to São Paulo.
3. **Other urban signals:** haze and smog, when the lights come on and go off, traffic peaks.

## Cadence: 5 minutes (keep)

| Use | Needs | At 5 minutes |
|-----|-------|--------------|
| Light pollution | a few frames per night, compared over months | more than enough; extra frames can be median-stacked to cut noise |
| Clouds / nowcasting | 1–10 min steps (clouds change within minutes) | good; at 15 min or more you lose cloud motion |
| Urban daily cycles | minutes to an hour | good |

Cost: ~288 frames a day, ~105k frames and ~550 GB a year (see [HOSTING](HOSTING.md)). 1 minute would be 5× that for little gain.
10 minutes would halve it, but it's borderline for clouds.

## Exposure: auto (accepted)

The camera runs Protune with Auto ISO 100–800, auto shutter and auto white balance.
Brightness and colour therefore change from frame to frame because of the camera, not only the city.
**Decision: this is accepted, and light-pollution results are qualitative.**

Upgrade path, if quantitative trends are ever wanted: lock the settings (fixed shutter, ISO min = max, fixed white balance such as 4000K, EV 0).
Start a new collection when you do.

Rule: **a new collection starts every time the camera settings or position change.**
Write the settings in the collection description.

## RAW (GPR): not in the pilot

- It's about 6× the size (~30 MB per frame), roughly 3 TB a year at 5 minutes.
- It only pays off for real radiometry, which the pilot doesn't aim for.
- Possible later step: a short RAW campaign (a few weeks) to calibrate the JPEG series.
  First check whether the HERO10 supports RAW in time-lapse photo mode at a 5-minute interval (not verified).

## Field notes

- **Power:** runs longer than a few hours need external USB power.
- **Storage:** 5 MB × 288 a day is about 1.5 GB a day, so a 128 GB card lasts about 80 days. Offload well before that.
- **Clock:** file names come from the camera clock. In the first collection it ran ~1 min off GPS time; check it at every offload.
- **Lens:** check for condensation, dirt and insects. Keep the framing identical between visits.
