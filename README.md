# Museum Audio Tour Data

This folder contains all museum and exhibit data for the audio tour app.

## Folder Structure

```
data/
├── museums.json          # Index of all available museums
├── README.md             # This documentation
└── museums/
    └── {museum-id}/
        └── museum.json   # Museum details and exhibits
```

## How to Add a New Museum

### Step 1: Create the museum folder

Create a new folder in `/data/museums/` using a URL-friendly ID (lowercase, hyphens instead of spaces):

```
/data/museums/your-museum-name/
```

### Step 2: Create museum.json

Create `/data/museums/your-museum-name/museum.json` with this structure:

```json
{
  "id": "your-museum-name",
  "name": {
    "en": "Your Museum Name",
    "nl": "Je Museum Naam"
  },
  "description": {
    "en": "A brief description of the museum.",
    "nl": "Een korte beschrijving van het museum."
  },
  "address": "Street Address, City",
  "location": {
    "latitude": 52.0000,
    "longitude": 4.0000
  },
  "supportedLanguages": ["en", "nl"],
  "defaultLanguage": "en",
  "exhibits": []
}
```

### Step 3: Add to the museum index

Add an entry to `/data/museums.json`:

```json
{
  "id": "your-museum-name",
  "name": {
    "en": "Your Museum Name",
    "nl": "Je Museum Naam"
  },
  "city": "Amsterdam",
  "country": "Netherlands",
  "thumbnail": "your-museum-name/thumbnail.jpg",
  "exhibitCount": 0
}
```

## How to Add an Exhibit

Add an exhibit object to the `exhibits` array in the museum's `museum.json`:

```json
{
  "id": "exhibit-id",
  "order": 1,
  "name": {
    "en": "Exhibit Name",
    "nl": "Tentoonstelling Naam"
  },
  "artist": "Artist Name (optional)",
  "year": "1642 (optional)",
  "location": {
    "latitude": 52.0000,
    "longitude": 4.0000,
    "floor": 1,
    "room": "Room Name",
    "directions": {
      "en": "Directions to find the exhibit",
      "nl": "Aanwijzingen om de tentoonstelling te vinden"
    }
  },
  "description": {
    "en": "The full description that will be read aloud by text-to-speech. This should be informative and engaging, typically 2-4 paragraphs.",
    "nl": "De volledige beschrijving die wordt voorgelezen door tekst-naar-spraak."
  },
  "images": [
    "your-museum-name/exhibit-image.jpg"
  ],
  "tags": ["painting", "sculpture", "etc"]
}
```

**Important:** After adding exhibits, update `exhibitCount` in `/data/museums.json`.

## Field Reference

### Museum Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier (URL-friendly) |
| `name` | Yes | Localized museum name |
| `description` | Yes | Localized description |
| `address` | Yes | Physical address |
| `location` | Yes | GPS coordinates of the museum |
| `supportedLanguages` | Yes | Array of ISO 639-1 language codes |
| `defaultLanguage` | Yes | Fallback language code |
| `exhibits` | Yes | Array of exhibit objects |

### Exhibit Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier within the museum |
| `order` | Yes | Suggested tour order (1, 2, 3...) |
| `name` | Yes | Localized exhibit name |
| `artist` | No | Creator/artist name |
| `year` | No | Year of creation |
| `location` | Yes | GPS + indoor location |
| `description` | Yes | Localized text for audio tour (TTS) |
| `images` | No | Array of image paths |
| `tags` | No | Categorization tags |

### Location Fields

| Field | Required | Description |
|-------|----------|-------------|
| `latitude` | Yes | GPS latitude |
| `longitude` | Yes | GPS longitude |
| `floor` | Yes | Floor number or name |
| `room` | Yes | Room name or number |
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

## Tips for Writing Descriptions

The `description` field is read aloud by text-to-speech. Write it as if you're a tour guide speaking to visitors:

- Start with the most interesting fact
- Keep sentences clear and not too long
- Avoid abbreviations (write "centimeters" not "cm")
- Include context about the artist, period, or technique
- Aim for 3-4 minutes of speaking time (roughly 420-560 words). The exact length can vary depending on the available historical information for a stop — a rich historic site may warrant 500+ words, a transitional or closing stop may be shorter. Avoid going below 300 words or above 650 words.
