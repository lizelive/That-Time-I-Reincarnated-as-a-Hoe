# Manga Chapters

This directory contains the image definitions for each manga chapter of "The Time I Reincarnated as a Hoe."

## Directory Structure

```
manga/
├── README.md
├── references/
│   ├── characters/     # Character reference JSONs
│   │   ├── howen.json
│   │   ├── cora.json
│   │   └── ...
│   └── locations/      # Location reference JSONs
│       ├── vault.json
│       └── ...
├── arc1/
│   ├── chapter01/
│   │   ├── chapter_meta.json    # Chapter metadata
│   │   ├── page_001.json        # Individual page definitions
│   │   ├── page_002.json
│   │   └── ...
│   └── chapter02/
│       └── ...
└── output/             # Generated images (gitignored)
```

## POV Guidelines

**All chapters are told from Howen's perspective** (the sentient hoe). This means:

1. The camera/viewpoint is always from Howen's position
2. When being held, this is from waist/hip level looking up at Cora or around
3. When lying on the ground, this is low-angle perspective
4. Howen cannot see behind her or places she cannot sense
5. Howen's internal monologue drives all narration
6. Other characters are seen as Howen sees them

## Prompting Guide (FLUX.2)

Following the [FLUX.2 prompting guide](https://docs.bfl.ai/guides/prompting_guide_flux2_klein):

### Write Like a Novelist
Describe scenes as flowing prose, not keywords. Subject first, then setting, details, and lighting.

### Prompt Structure
**Subject → Setting → Details → Lighting → Atmosphere**

| Element | Purpose | Example |
|---------|---------|---------|
| Subject | What the image is about | "A blue point of light awakens in darkness" |
| Setting | Where the scene takes place | "deep within an ancient vault" |
| Details | Specific visual elements | "dust particles catch the glow, archotech circuits pulse" |
| Lighting | How light shapes the scene | "single point source blue light, minimal illumination" |
| Atmosphere | Mood and emotional tone | "Style: Awakening consciousness. Mood: Primordial, uncertain." |

### Lighting is Key
Lighting has the greatest impact on output quality. Describe:
- Source (natural, artificial, bioluminescent)
- Quality (soft, harsh, diffused)
- Direction (side, back, overhead)
- Temperature (warm, cool, blue, purple)

### Style Annotations
End prompts with explicit style and mood:
```
Style: Science fiction archaeology, survival horror aesthetic.
Mood: Ancient, dangerous, secrets waiting.
```

## Chapter Structure

Each chapter contains exactly 24 images (pages) following manga conventions:
- Pages 1-3: Opening hook
- Pages 4-8: Building action
- Pages 9-16: Main content
- Pages 17-22: Climax/development
- Pages 23-24: Chapter closing/cliffhanger

## Arc Overview

### Arc 1: Life in the Vault (Chapters 1-12)
Howen awakens, learns her new form, cultivates mushrooms, befriends Chitin, and eventually escapes with Cora's help.

| Chapter | Title | Key Events |
|---------|-------|------------|
| 01 | Awakening in Darkness | First consciousness, discovering hoe form, first mushrooms |
| 02 | The Garden Grows | Expanding garden, meeting megascarab nymphs, bonding with Chitin |
| 03 | Tending the Darkness | Learning limits, avoiding the Centipede, Chitin growing |
| 04 | The First Voice | Sensing something outside, first attempt at the wall |
| 05 | She Who Digs | Cora discovers the vault, their first meeting |
| 06 | A Wielder Found | Cora picks up Howen, the bond forms |
| 07 | Waking the Giant | The Centipede activates, escape begins |
| 08 | Through Fire and Fungus | Boom mushrooms vs Scorcher mechanoid |
| 09 | The Clever Trap | Defeating the Centipede through strategy |
| 10 | Chitin's Choice | Chitin falls into the vault depths |
| 11 | Breaking Free | Final escape from the vault |
| 12 | The World Above | First view of the rimworld surface |

### Arc 2: The Wider Rim (Chapters 1-12)
Survival on the surface, learning about the rimworld, encounters with traders and dangers, eventual contact with the Empire.

### Arc 3: Embrace of the Empire (Chapters 1-12)
Joining the Empire, training, comfort, neurotrainer powers, nine months of belonging before darkness.

### Arc 4: The Fall (Chapters 1-12)
Discovery of rip-scanning, fleeing, finding the Barleybloom Tribe, and watching it burn.

### Arc 5: The Deserter's Path (Chapters 1-12)
Joining the Deserters, anima tree attunement, true power, final escape from the rimworld.

## JSON Format

### Chapter Metadata (`chapter_meta.json`)
```json
{
  "chapter_id": "arc1_ch01",
  "arc": 1,
  "arc_title": "Life in the Vault",
  "chapter": 1,
  "chapter_title": "Awakening in Darkness",
  "pov": "howen",
  "total_pages": 24,
  "summary": "...",
  "themes": [],
  "character_development": {},
  "key_moments": [],
  "page_files": ["page_001.json", ...],
  "next_chapter": "arc1/chapter02",
  "previous_chapter": null
}
```

### Page Definition (`page_XXX.json`)
```json
{
  "image_id": "arc1_ch01_001",
  "arc": 1,
  "chapter": 1,
  "chapter_title": "Awakening in Darkness",
  "page": 1,
  "pov": "howen",
  "prompt": "Flowing prose description following FLUX.2 guide...",
  "caption": "Dialogue or narration text",
  "narration": "Howen's internal monologue",
  "characters": ["howen"],
  "character_refs": ["references/characters/howen.json"],
  "location": "vault",
  "location_refs": ["references/locations/vault.json"],
  "visual_elements": ["element1", "element2"],
  "lighting": "Lighting description",
  "mood": "mysterious",
  "technical_notes": "Additional generation notes"
}
```

### Character Reference (`references/characters/X.json`)
```json
{
  "character_id": "howen",
  "name": "Howen Ashford",
  "type": "persona_weapon",
  "visual_description": "...",
  "reference_prompt": "Full prompt for generating reference image",
  "key_visual_elements": [],
  "emotional_states": {}
}
```

### Location Reference (`references/locations/X.json`)
```json
{
  "location_id": "vault",
  "name": "The Ancient Vault",
  "type": "ancient_danger",
  "visual_description": "...",
  "reference_prompt": "Full prompt for generating reference image",
  "key_visual_elements": [],
  "lighting": {}
}
```

## Generating Images

Use the tool in `/tools/generate_images.py`:

```bash
# List available chapters
python tools/generate_images.py --list-chapters

# List reference files
python tools/generate_images.py --list-references

# Generate all images for a chapter
python tools/generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN

# Generate a specific page
python tools/generate_images.py --chapter arc1/chapter01 --page 5 --token YOUR_HF_TOKEN

# Preview prompts without generating (dry run)
python tools/generate_images.py --chapter arc1/chapter01 --dry-run

# Generate a character reference image
python tools/generate_images.py --generate-reference character:howen --token YOUR_HF_TOKEN

# Generate a location reference image
python tools/generate_images.py --generate-reference location:vault --token YOUR_HF_TOKEN

# Create a new chapter template
python tools/generate_images.py --create-template arc1/chapter03
```

Generated images are saved to `/manga/output/` (gitignored).
