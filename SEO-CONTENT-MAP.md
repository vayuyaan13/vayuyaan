# Search-intent and content ownership map

Last reviewed: 13 November 2026

## Scope and data limitation

This plan is for the **GitHub Pages repository** `vayuyaan13/vayuyaan` only.

The performance figures below came from the connected Google Search Console property for `https://vayuyaan.com/`, covering the available 30-day reporting window through 10 November 2026. They describe the main Vayuyaan website, **not** the GitHub Pages hostname. Do not present them as GitHub rankings or traffic.

No files, settings, content, redirects, metadata, sitemap or Search Console configuration on the main `vayuyaan.com` website are part of this plan.

## Search signals that guide the GitHub content

| Main-site page | Clicks | Impressions | CTR | GitHub content role |
|---|---:|---:|---:|---|
| Arduino Uno R3 complete guide | 53 | 67,353 | 0.08% | Practical supporting tutorials; do not reproduce the broad board introduction |
| What is LDR sensor | 34 | 31,059 | 0.11% | Link to it for fundamentals; keep circuit, calibration and project instructions here |
| IR sensor working | 5 | 13,812 | 0.04% | Main site owns broad definition and working intent; GitHub owns projects and calibration |
| IR sensor working principle and applications | 5 | 5,111 | 0.10% | Use as the broad IR reference; avoid another generic IR explainer here |
| IR sensor complete guide | 5 | 4,169 | 0.12% | GitHub content should focus on module testing and specific builds |
| Ultrasonic sensor quick-start guide | 9 | 7,272 | 0.12% | Link to it for broad range/overview; GitHub owns HC-SR04 pinout, wiring, code and diagnostics |
| Ultrasonic sensor in robotics | 14 | 3,680 | 0.38% | Use for broader robotics context; GitHub owns implementation details |
| Smart dustbin project | 27 | 5,621 | 0.48% | Link as a next project; do not create a duplicate smart-dustbin article in this repository |
| ESP32 development board guide | 22 | 7,518 | 0.29% | Link to main-site introduction; keep GitHub examples task-specific |
| Line follower robot | 4 | 2,030 | 0.20% | Link to the main project; GitHub owns IR calibration and subsystem guidance |

CTR is clicks divided by impressions. These rounded figures are a planning signal, not a guarantee of ranking opportunity.

## Content ownership rules

### LDR

- Main Vayuyaan article: broad meaning, full form, applications and working principle.
- GitHub `ldr-sensor-working-principle/`: voltage-divider circuit, resistor selection, Arduino analog readings and calibration.
- GitHub `arduino-ldr-automatic-street-light/`: complete practical project.
- GitHub `ldr-vs-photodiode/`: component-selection comparison.

Do not create another generic “What is LDR?” page in this repository.

### Infrared (IR)

- Main Vayuyaan articles: broad IR definition, working principle, types, range and applications.
- GitHub `ir-sensor-projects-arduino/`: practical beginner projects.
- GitHub `arduino-line-follower-ir-sensor-calibration/`: sensor readings, thresholds and line-tracking calibration.
- GitHub `ir-sensor-vs-ultrasonic-sensor/`: selection comparison between reflective IR modules and ultrasonic distance sensors.

Do not create another general IR working-principle page. Keep the difference between reflective obstacle/line modules and other IR sensor types explicit.

### Ultrasonic / HC-SR04

- Main Vayuyaan articles: broad ultrasonic sensor overview, range and robotics applications.
- GitHub `hc-sr04-ultrasonic-sensor-guide/`: pinout, Arduino wiring, distance formula, code and troubleshooting.
- GitHub `ir-sensor-vs-ultrasonic-sensor/`: compare sensing methods and project suitability.
- Link to the main-site smart-dustbin project as a practical next step; do not duplicate it here.

### Arduino and ESP32

- Main Vayuyaan articles remain the broad beginner entry points.
- GitHub pages should add implementation detail, focused code, wiring checks, calibration or a distinct project.
- Avoid publishing near-identical introductions that target the same broad queries.

## Internal-linking rules for this repository

1. Every practical guide should link back to its relevant GitHub hub.
2. Comparison pages should link to the detailed implementation guides for both sensor types.
3. Project pages should link to the calibration or wiring guide needed to complete the project.
4. Link to main-site articles when they provide a genuinely broader introduction or a distinct project.
5. Use descriptive anchor text that explains the destination; do not repeat exact-match keywords unnaturally.
6. Keep canonical URLs on the GitHub Pages hostname for GitHub-hosted pages. Do not canonicalise GitHub pages to the main website.
7. Do not add GitHub URLs to the main website sitemap or modify the main website to link back.

## Measurement and review

Before making claims about GitHub organic performance, add and verify the exact GitHub Pages URL-prefix property in Google Search Console. The existing Windsor.ai connection used for this audit reports the main `vayuyaan.com` property and is not evidence of GitHub Pages performance.

Review this map when new GitHub pages are proposed or when query ownership materially changes. Do not create a new article solely to target a keyword already served by a relevant page.
