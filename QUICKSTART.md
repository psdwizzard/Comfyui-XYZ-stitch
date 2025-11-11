# XYZ Grid Quick Start Guide

## The Problem You're Experiencing

When you run the workflow, each execution only generates ONE image, but the Stitch node needs ALL images to create the grid. You need a way to collect images across multiple workflow runs.

## The Solution: Use the Image Collector Node

The **XYZ Image Collector** node accumulates images across multiple workflow runs, then outputs them all at once for stitching.

## Simple Workflow Setup

### Step 1: Set Up the Generation Chain

```
1. XYZ Grid Input (set index to 0, with your X, Y, Z values)
   ↓ x_value, y_value, z_value
2. Your workflow (prompts, KSampler, VAE Decode, etc.)
   ↓ Generated Image
3. XYZ Image Collector (mode: "collect")
   ↓ (collects images in memory)
4. [Queue this 9 times, changing index from 0 to 8]
```

### Step 2: Output the Grid

After collecting all images:

```
1. XYZ Image Collector (change mode to: "output_and_reset")
   ↓ All collected images
2. XYZ Grid Stitch
   ↓ Final grid image
```

## Detailed Instructions

### Phase 1: Collect Images (Run 9 times)

1. **Add XYZ Grid Input node**
   - X values: `Mergedragon Reward style of A digital artwork of a golden compass`
   - Y values: `10, 20, 30`
   - Z values: `` (leave empty)
   - Index: `0` (you'll change this each run)

2. **Add XYZ Image Collector node**
   - Mode: `collect`
   - Collection ID: `my_grid` (any name you want)
   - Expected count: `9` (3x3 = 9 combinations)

3. **Connect your workflow**
   - XYZ Grid Input → Your prompt/parameters → Generate image → XYZ Image Collector

4. **Run the workflow 9 times**
   - Run 1: Set index to `0`, Queue Prompt
   - Run 2: Set index to `1`, Queue Prompt
   - Run 3: Set index to `2`, Queue Prompt
   - ...continue...
   - Run 9: Set index to `8`, Queue Prompt

5. **Watch the console**
   - You'll see: "Collected 1/9 images", "Collected 2/9 images", etc.
   - When it says "Collected 9/9 images - READY TO OUTPUT", you're done collecting!

### Phase 2: Create the Grid (Run once)

1. **Change the Image Collector mode**
   - Mode: Change from `collect` to `output_and_reset`

2. **Add XYZ Grid Stitch node**
   - Connect the Image Collector's output to the Stitch node's input
   - X labels: Same as your X values
   - Y labels: Same as your Y values
   - Z labels: Leave empty (or same as Z values)

3. **Run the workflow ONE more time**
   - This outputs all 9 collected images to the Stitch node
   - The Stitch node creates your comparison grid!

## Visual Workflow

```
┌─────────────────────┐
│  XYZ Grid Input     │
│  index: 0-8         │
└──────────┬──────────┘
           │ x_value, y_value
           ↓
┌─────────────────────┐
│  Your Workflow      │
│  (Prompt, Generate) │
└──────────┬──────────┘
           │ image
           ↓
┌─────────────────────┐
│ XYZ Image Collector │
│ mode: collect       │  ← Run this 9 times with index 0-8
│ expected: 9         │
└─────────────────────┘

Then change mode and run once more:

┌─────────────────────┐
│ XYZ Image Collector │
│ mode: output_reset  │  ← Run once to output all
└──────────┬──────────┘
           │ all 9 images
           ↓
┌─────────────────────┐
│  XYZ Grid Stitch    │
│  Creates final grid │
└─────────────────────┘
```

## Tips

### Reset the Collection
If you mess up and need to start over:
- Change Image Collector mode to `reset_only`
- Run once
- Change back to `collect` and start again

### Check Progress
The console shows:
- `[XYZ Grid Input]` - which combination is being generated
- `[XYZ Image Collector]` - how many images collected so far

### Multiple Grids
Use different `collection_id` values to collect multiple separate grids at once.

## What Each Mode Does

- **collect**: Adds the current image to the collection (use this while generating)
- **output_and_reset**: Outputs all collected images and clears the collection (use this to stitch the grid)
- **output_only**: Outputs all collected images but keeps them in memory
- **reset_only**: Clears the collection without outputting anything

## Example: 3x3 Grid

For X=["red", "blue", "green"] and Y=["10", "20", "30"]:

1. Run with index 0 → generates red, 10
2. Run with index 1 → generates blue, 10
3. Run with index 2 → generates green, 10
4. Run with index 3 → generates red, 20
5. Run with index 4 → generates blue, 20
6. Run with index 5 → generates green, 20
7. Run with index 6 → generates red, 30
8. Run with index 7 → generates blue, 30
9. Run with index 8 → generates green, 30

Then change mode to output_and_reset, run once → creates 3x3 grid!

## Need Help?

If you're still having issues:
1. Check the console for error messages
2. Make sure you're using the same `collection_id` for all runs
3. Make sure the `expected_count` matches your total combinations
4. Make sure you change the mode to `output_and_reset` before the final run
