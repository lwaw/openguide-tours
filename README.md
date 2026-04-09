# Tour Data

This folder contains all tour and stop data for the audio tour app.

## Folder Structure

```
data/
├── tours.json          # Index of all available tours
├── README.md           # This documentation
└── tours/
    └── {tour-id}/
        ├── tour.json   # Full tour data including all stops
        └── *.jpg       # Optional local images (referenced in stop data)
```

## How to Add a New Tour

### Step 1: Create the tour folder

Create a new folder in `/data/tours/` using a URL-friendly ID (lowercase, hyphens instead of spaces):

```
/data/tours/your-tour-name/
```

### Step 2: Create tour.json

Create `/data/tours/your-tour-name/tour.json` with this structure:

```json
{
  "id": "your-tour-name",
  "name": {
    "en": "Your Tour Name",
    "nl": "Je Tournaam"
  },
  "description": {
    "en": "A brief description of the tour.",
    "nl": "Een korte beschrijving van de tour."
  },
  "type": "city",
  "duration": 90,
  "distance": 3.5,
  "startPoint": {
    "name": { "en": "Starting location name", "nl": "Naam startlocatie" },
    "address": "Street Address, City",
    "location": { "latitude": 52.0000, "longitude": 4.0000 }
  },
  "supportedLanguages": ["en", "nl"],
  "defaultLanguage": "en",
  "stops": []
}
```

For museum tours, use `"type": "museum"` and replace `startPoint` with `venue` (which also includes `openingHours` and `ticketInfo`).

### Step 3: Add to the tour index

Add an entry to `/data/tours.json`:

```json
{
  "id": "your-tour-name",
  "name": { "en": "Your Tour Name", "nl": "Je Tournaam" },
  "type": "city",
  "city": "Amsterdam",
  "country": "Netherlands",
  "thumbnail": "your-tour-name/thumbnail.jpg",
  "duration": 90,
  "stopCount": 0,
  "startLocation": { "latitude": 52.0000, "longitude": 4.0000 }
}
```

## How to Add a Stop

Add a stop object to the `stops` array in the tour's `tour.json`:

```json
{
  "id": "stop-id",
  "order": 1,
  "name": {
    "en": "Stop Name",
    "nl": "Stopnaam"
  },
  "subtitle": {
    "en": "Optional: year · short context",
    "nl": "Optioneel: jaar · korte context"
  },
  "location": {
    "latitude": 52.0000,
    "longitude": 4.0000,
    "directions": {
      "en": "How to find this stop.",
      "nl": "Hoe u deze stop vindt."
    }
  },
  "description": {
    "en": "The full narration text, read aloud by text-to-speech.",
    "nl": "De volledige tekst die wordt voorgelezen door tekst-naar-spraak."
  },
  "images": [],
  "tags": ["architecture", "history"]
}
```

After adding stops, update `stopCount` in `/data/tours.json`.

## Images

The `images` field accepts an array of zero or more image references. Two formats are supported:

**Local file** — a relative path from the `data/` folder to an image in the tour folder:
```json
"images": ["your-tour-name/stop-name.jpg"]
```

**Pexels URL** — the full photo page URL from [pexels.com](https://www.pexels.com):
```json
"images": ["https://www.pexels.com/photo/description-of-photo-12345678/"]
```

**No image yet** — use an empty array:
```json
"images": []
```

Multiple images per stop are supported by adding more entries to the array.

## Field Reference

### Tour Index Fields (tours.json)

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (URL-friendly) |
| `name` | Yes | Localized tour name |
| `type` | Yes | `"city"` or `"museum"` |
| `city` | Yes | City where the tour takes place |
| `country` | Yes | Country where the tour takes place |
| `thumbnail` | Yes | Local relative path to tour card image |
| `image` | No | Optional image: local relative path or Pexels photo page URL |
| `duration` | Yes | Estimated duration in minutes |
| `stopCount` | Yes | Number of stops (keep in sync with tour.json) |
| `startLocation` | Yes | GPS coordinates of the tour's starting point |

### Tour Fields (tour.json)

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (URL-friendly) |
| `name` | Yes | Localized tour name |
| `description` | Yes | Localized tour description |
| `type` | Yes | `"city"` or `"museum"` |
| `duration` | Yes | Estimated duration in minutes |
| `distance` | No | Walking distance in kilometres (city tours) |
| `startPoint` | City tours | Localized name, address, and GPS location |
| `venue` | Museum tours | Museum name, address, GPS, hours, tickets |
| `supportedLanguages` | Yes | Array of ISO 639-1 language codes |
| `defaultLanguage` | Yes | Fallback language code |
| `stops` | Yes | Array of stop objects |

### Stop Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the tour (URL-friendly) |
| `order` | Yes | Tour sequence number (1, 2, 3...) |
| `name` | Yes | Localized stop name |
| `subtitle` | No | Short localized context line (dates, significance) |
| `location` | Yes | GPS coordinates, optional indoor info, optional directions |
| `description` | Yes | Localized narration text for audio tour (TTS) |
| `images` | Yes | Array of image references (local paths or Pexels URLs); use `[]` if none |
| `tags` | Yes | Categorization tags |

### Location Fields

| Field | Required | Description |
|-------|----------|-------------|
| `latitude` | Yes | GPS latitude |
| `longitude` | Yes | GPS longitude |
| `indoor` | No | `{ "floor": 1, "room": "Room name" }` (museum stops) |
| `directions` | No | Localized wayfinding text |

## Multi-Language Support

All user-facing text fields use localized objects:

```json
{
  "en": "English text",
  "nl": "Nederlandse tekst",
  "de": "Deutscher Text"
}
```

Use [ISO 639-1 language codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

## Writing Stop Descriptions

The `description` field is read aloud by text-to-speech. See the TOUR CONTENT GUIDELINES section in `CLAUDE.md` for full narration style guidance, including target length (520–650 words), em dash avoidance, and tone.
