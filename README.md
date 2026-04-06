# AI Event Aggregator

A full-stack event platform with sponsorship marketplace, plus a standalone Sponsor Hub site.

## Setup

```bash
# Main app
cd "[team]-circle---ai-event-platform"
npm install

# Standalone Sponsor Hub
cd sponsor_hub_site
npm install
```

## Run Main App

```bash
cd "[team]-circle---ai-event-platform"
npm run dev
```

Runs backend + frontend at `http://localhost:3000`

## Run Standalone Sponsor Hub

Start the main app first (backend must be on port 3000), then:

```bash
cd sponsor_hub_site
npm run dev
```

Runs at `http://localhost:3001`
