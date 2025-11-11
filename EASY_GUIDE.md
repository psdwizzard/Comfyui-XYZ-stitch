# XYZ Grid - EASY MODE

## The Super Simple Way

Use the **XYZ Auto Collector** - it does everything automatically!

---

## Setup (Do Once)

### 1. Your Workflow Chain

```
XYZ Grid Input → String to Number → Generate Image → XYZ Auto Collector → XYZ Grid Stitch
```

### 2. Connect the Nodes

**XYZ Grid Input:**
- X values: `red, blue, green`
- Y values: `10, 20, 30`
- Z values: (empty)

**Connections:**
- XYZ Grid Input → `total_combinations` → XYZ Auto Collector
- XYZ Grid Input → `y_value` → String to Number → your sampler steps
- XYZ Grid Input → `x_value` → your prompt

**XYZ Auto Collector:**
- Connect generated images → `images`
- Connect `total_combinations` from Grid Input → `total_combinations`

**XYZ Grid Stitch:**
- Connect Auto Collector `images` → Stitch `images`
- Connect Auto Collector `is_complete` → Stitch `is_complete` (IMPORTANT!)
- X labels: `red, blue, green`
- Y labels: `10, 20, 30`
- Z labels: (optional - for 3D grids)
- label_height: `40` (space for labels at top)
- label_width: `80` (space for labels on left)
- gap_size: `4`
- layout_style: `A1111 Style (X blocks)` or `Z Horizontal` (NEW!)

**The is_complete connection is critical!** It tells the Stitch node to only create the grid when all images are collected.

**NEW: A1111 Style!** Choose "A1111 Style (X blocks)" for the classic Automatic1111 layout where each X value gets its own block. See A1111_STYLE_GUIDE.md for details!

---

## Usage (Do This Part)

### Just Run 9 Times (Change Index Each Time)

1. Set index to **0**, Queue Prompt → "Collecting... 1/9"
2. Set index to **1**, Queue Prompt → "Collecting... 2/9"
3. Set index to **2**, Queue Prompt → "Collecting... 3/9"
4. Set index to **3**, Queue Prompt → "Collecting... 4/9"
5. Set index to **4**, Queue Prompt → "Collecting... 5/9"
6. Set index to **5**, Queue Prompt → "Collecting... 6/9"
7. Set index to **6**, Queue Prompt → "Collecting... 7/9"
8. Set index to **7**, Queue Prompt → "Collecting... 8/9"
9. Set index to **8**, Queue Prompt → "✓ Complete! Outputting all 9 images to grid"

**On run #9, it automatically:**
- Detects you've collected all 9 images
- Outputs all 9 to the Stitch node
- Creates your 3x3 grid
- Resets for the next grid

**That's it!** No mode switching, no manual counting, no extra steps.

---

## What You'll See

**During collection (runs 1-8):**
```
Console: [XYZ Auto Collector] Collecting... 3/9
Console: [XYZ Grid Stitch] Skipping - waiting for all images to be collected
Preview: Your individual image (grid not created yet)
```

**On final run (run 9):**
```
Console: [XYZ Auto Collector] ✓ Complete! Outputting all 9 images to grid
Console: [XYZ Grid Stitch] Created grid with 9 images (3x3x1)
Output: Your 3x3 comparison grid!
```

---

## Starting a New Grid

Just start from index 0 again! The Auto Collector automatically resets after outputting.

---

## Troubleshooting

**Q: It keeps saying "Collecting... 10/9, 11/9..."**
A: You ran too many times. Set `reset` to True, run once, then start over from index 0.

**Q: The grid is all the same image**
A: You're not changing the index! Make sure to change it from 0 to 8.

**Q: I want to test different parameters**
A:
- For steps: Put numbers in Y values (10, 20, 30) → connect to String to Number → steps
- For CFG: Put numbers in Z values (5.0, 7.0, 10.0) → connect to String to Number (FLOAT) → cfg
- For prompts: Put text in X values → connect to your prompt

---

## Visual Flow

```
Run 1: Index=0 → Generate "red, 10" → Collect (1/9) → Stitch: Skip
Run 2: Index=1 → Generate "blue, 10" → Collect (2/9) → Stitch: Skip
Run 3: Index=2 → Generate "green, 10" → Collect (3/9) → Stitch: Skip
Run 4: Index=3 → Generate "red, 20" → Collect (4/9) → Stitch: Skip
Run 5: Index=4 → Generate "blue, 20" → Collect (5/9) → Stitch: Skip
Run 6: Index=5 → Generate "green, 20" → Collect (6/9) → Stitch: Skip
Run 7: Index=6 → Generate "red, 30" → Collect (7/9) → Stitch: Skip
Run 8: Index=7 → Generate "blue, 30" → Collect (8/9) → Stitch: Skip
Run 9: Index=8 → Generate "green, 30" → Collect (9/9) COMPLETE! → Stitch: CREATE 3x3 GRID!
```

---

## That's It!

No modes to switch, no manual output step, no complexity. Just:
1. Set up the connections once
2. Run 9 times with different indices
3. Get your grid automatically on the last run

Simple! 🎉
