# Image Generation Tools

This directory contains tools for generating manga images for "The Time I Reincarnated as a Hoe."

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get a Hugging Face API token from https://huggingface.co/settings/tokens

3. Set your token:
   ```bash
   export HF_TOKEN=your_token_here
   ```

## Usage

### Generate a chapter's images

```bash
python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN
```

### Generate a single image

```bash
python generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN --image 5
```

### List available chapters

```bash
python generate_images.py --list-chapters
```

### Create a new chapter template

```bash
python generate_images.py --create-template arc1/chapter02
```

### Dry run (see prompts without generating)

```bash
python generate_images.py --chapter arc1/chapter01 --dry-run
```

## Chapter JSON Format

Each chapter is defined by a JSON file in the `manga/` directory with this structure:

```json
{
  "title": "Chapter Title",
  "arc": "arc1",
  "chapter_number": 1,
  "pov": "howen",
  "summary": "Brief chapter summary from Howen's perspective.",
  "images": [
    {
      "page": 1,
      "description": "Detailed scene description for the AI",
      "caption": "Dialogue or narration text to overlay",
      "characters": ["howen", "cora"],
      "location": "vault",
      "mood": "mysterious",
      "visual_elements": ["glowing mushrooms", "dust particles"],
      "reference_images": ["arc1/chapter01/page_03.png"]
    }
  ]
}
```

### Image Fields

| Field | Description |
|-------|-------------|
| `page` | Page number (1-24) |
| `description` | Detailed scene description for image generation |
| `caption` | Text to display on the page (dialogue, narration) |
| `characters` | List of characters in the scene |
| `location` | Location reference key |
| `mood` | Emotional tone (mysterious, tense, peaceful, etc.) |
| `visual_elements` | Specific elements to include |
| `reference_images` | Paths to reference images for consistency |

### Available Characters

- `howen` - The persona hoe (POV character)
- `cora` - Cora Barleybloom (wielder)
- `chitin` - Megascarab companion
- `vex` - Captain Saren Vex
- `wheatstone` - Charles Wheatstone (AI)

### Available Locations

- `vault` - Ancient danger vault
- `mushroom_garden` - Howen's cultivation area
- `megascarab_nest` - Chitin's home
- `rim_surface` - Outside on the rimworld
- `imperial_fort` - Empire military installation
- `barleybloom_valley` - Tribal farming community
- `anima_grove` - Sacred psychic location
- `deserter_camp` - Resistance hideout

## POV Guidelines

All images are from Howen's perspective (the hoe). This means:

1. **Camera angle**: Often ground-level or from waist/hip height (where a hoe would be carried)
2. **Cora's face**: Usually shown from below or side angle
3. **Emotional indicators**: Howen's glowing core and any plant growth on her handle reflect her emotional state
4. **Limited vision**: When stored, show darkness or fabric textures
5. **Combat POV**: Dramatic swinging motions, blur effects, impact moments

## Output

Generated images are saved to:
```
manga/output/{chapter_path}/page_{number}.png
```

Images are 768x1024 pixels (manga page proportions).
