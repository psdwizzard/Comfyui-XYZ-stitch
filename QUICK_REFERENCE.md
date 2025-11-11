# XYZ Grid - Quick Reference

## The 4 Nodes You Need

1. **XYZ Grid Input** - Generates combinations
2. **XYZ String to Number** - Converts strings to numbers
3. **XYZ Auto Collector** - Automatically collects images
4. **XYZ Grid Stitch** - Creates the final grid

## Required Connections

```
┌─────────────────────┐
│  XYZ Grid Input     │
│  X: red,blue,green  │
│  Y: 10,20,30        │
│  Z: (empty)         │
│  Index: 0-8         │
└──────┬──────────────┘
       │
       ├─ x_value ────────────→ Your Prompt
       │
       ├─ y_value ───→ ┌──────────────────┐
       │               │ String to Number │
       │               └────┬─────────────┘
       │                    └─ int_value ──→ KSampler (steps)
       │
       └─ total_combinations ──┐
                                │
       ┌────────────────────────┘
       │
       ↓
┌─────────────────────────────┐
│     Generated Image         │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│   XYZ Auto Collector        │
│   total_combinations: ←─────┼─── (from Grid Input)
│   collection_id: default    │
└──────────┬──────────────────┘
           │
           ├─ images ─────────┐
           │                  │
           └─ is_complete ─┐  │
                           │  │
                ┌──────────┘  │
                │             │
                ↓             ↓
┌─────────────────────────────┐
│   XYZ Grid Stitch           │
│   is_complete: ←────────────┼─── (IMPORTANT!)
│   images: ←─────────────────┘
│   X labels: red,blue,green  │
│   Y labels: 10,20,30        │
└──────────┬──────────────────┘
           │
           ↓
     [Final 3x3 Grid]
```

## Critical Connection

**XYZ Auto Collector `is_complete` → XYZ Grid Stitch `is_complete`**

Without this, the Stitch node will create a grid every single run instead of waiting until all images are collected!

## How to Use

1. **Set up connections once** (as shown above)
2. **Run 9 times**, changing index from 0 to 8
3. **On run 9**, the grid automatically appears!

## What Happens Each Run

| Run | Index | X Value | Y Value | Status | Grid Created? |
|-----|-------|---------|---------|--------|---------------|
| 1   | 0     | red     | 10      | Collecting 1/9 | ❌ No (skipped) |
| 2   | 1     | blue    | 10      | Collecting 2/9 | ❌ No (skipped) |
| 3   | 2     | green   | 10      | Collecting 3/9 | ❌ No (skipped) |
| 4   | 3     | red     | 20      | Collecting 4/9 | ❌ No (skipped) |
| 5   | 4     | blue    | 20      | Collecting 5/9 | ❌ No (skipped) |
| 6   | 5     | green   | 20      | Collecting 6/9 | ❌ No (skipped) |
| 7   | 6     | red     | 30      | Collecting 7/9 | ❌ No (skipped) |
| 8   | 7     | blue    | 30      | Collecting 8/9 | ❌ No (skipped) |
| 9   | 8     | green   | 30      | ✓ Complete! | ✅ YES! 3x3 grid |

## Console Output

**Runs 1-8:**
```
[XYZ Grid] Combination X/9: X=..., Y=...
[XYZ Auto Collector] Collecting... X/9
[XYZ Grid Stitch] Skipping - waiting for all images to be collected
```

**Run 9:**
```
[XYZ Grid] Combination 9/9: X=green, Y=30
[XYZ Auto Collector] ✓ Complete! Outputting all 9 images to grid
[XYZ Grid Stitch] Created grid with 9 images (3x3x1)
```

## Tips

- **Don't forget the is_complete connection!** This is what prevents the grid from being created on every run.
- **Change the index manually** from 0 to 8 for each run
- **The Auto Collector auto-resets** after outputting, so you can immediately start a new grid by going back to index 0
- **No individual images are saved during collection** - The Auto Collector outputs a tiny placeholder during collection to prevent your Save Image nodes from saving each individual image. Only the final grid gets saved!
- **Adjust label_width if Y labels are cut off** - Default is 80 pixels. Increase if your Y labels are long.

That's it! Simple and automatic. 🎉
