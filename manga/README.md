# Manga Chapters

This directory contains the JSON definitions for each manga chapter of "The Time I Reincarnated as a Hoe."

## POV Guidelines

**All chapters are told from Howen's perspective** (the sentient hoe). This means:

1. The camera/viewpoint is always from Howen's position
2. When being held, this is from waist/hip level looking up at Cora or around
3. When lying on the ground, this is low-angle perspective
4. Howen cannot see behind her or places she cannot sense
5. Howen's internal monologue drives all captions
6. Other characters are seen as Howen sees them

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

Each chapter JSON includes:
- `title`: Chapter title
- `arc`: Arc identifier
- `chapter_number`: 1-12
- `pov`: Always "howen"
- `summary`: Brief synopsis from Howen's perspective
- `images`: Array of 24 image definitions

Each image definition includes:
- `page`: Page number (1-24)
- `description`: Scene description for image generation
- `caption`: Narration/dialogue text
- `characters`: Characters present
- `location`: Location reference
- `mood`: Emotional tone
- `visual_elements`: Specific elements to include
- `reference_images`: Paths to reference for consistency

## Generating Images

Use the tool in `/tools/generate_images.py`:

```bash
# Generate all images for a chapter
python tools/generate_images.py --chapter arc1/chapter01 --token YOUR_HF_TOKEN

# Preview prompts without generating
python tools/generate_images.py --chapter arc1/chapter01 --dry-run
```

Generated images are saved to `/manga/output/`.
