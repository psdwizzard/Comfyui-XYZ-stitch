# XYZ Grid - Simple Guide (FIX FOR YOUR ISSUES)

## You're Getting 9 Grids Instead of 1 Grid?

**PROBLEM:** The Stitch node is running EVERY time instead of just once at the end.

**SOLUTION:** DON'T connect the Stitch node during collection! Only connect it for the final output.

---

## How to Use XYZ Grid (Step by Step)

### Setup Your Workflow

You need TWO separate parts in your workflow:

#### PART 1: Collection (Run 9 times)
```
XYZ Grid Input → String to Number (NEW!) → KSampler (steps)
              → (also connect to prompts)

KSampler → VAE Decode → Image Collector (mode: "collect")

DO NOT CONNECT STITCH YET!
```

#### PART 2: Grid Creation (Run 1 time)
```
Image Collector (mode: "output_and_reset") → XYZ Grid Stitch → Save Image
```

---

## Fixing the Steps Issue

The Y value is a string like "10", but steps needs an integer. Use the new **XYZ String to Number** node!

### Before (BROKEN):
```
XYZ Grid Input (y_value) → KSampler (steps)
                            ❌ Error: Can't use string as steps
```

### After (WORKING):
```
XYZ Grid Input (y_value) → XYZ String to Number (int_value) → KSampler (steps)
                                                              ✅ Works!
```

---

## Complete Workflow Setup

### Step 1: Add Your Nodes

1. **XYZ Grid Input**
   - X values: `red, blue, green`
   - Y values: `10, 20, 30`
   - Z values: (empty)
   - Index: 0

2. **XYZ String to Number** (NEW NODE!)
   - Connect: XYZ Grid Input (y_value) → text
   - Output type: INT

3. **Your Generation Workflow**
   - Connect: String to Number (int_value) → KSampler (steps)
   - Connect: XYZ Grid Input (x_value) → your prompt

4. **XYZ Image Collector**
   - Mode: `collect`
   - Expected count: 9
   - Collection ID: `my_test`

5. **XYZ Grid Stitch** (DON'T CONNECT YET!)
   - Just add it, leave it disconnected for now

### Step 2: Collect Images (Run 9 Times)

**Your workflow during collection:**
```
[XYZ Grid Input] → [String to Number] → [Generate] → [Image Collector]
                                                       (mode: collect)
```

**Important:** The Stitch node should be DISCONNECTED or MUTED!

1. Set Index to 0, Queue Prompt → "Collected 1/9 images"
2. Set Index to 1, Queue Prompt → "Collected 2/9 images"
3. Set Index to 2, Queue Prompt → "Collected 3/9 images"
4. Continue... up to Index 8 → "Collected 9/9 images - READY TO OUTPUT"

### Step 3: Create the Grid (Run 1 Time)

1. **Change Image Collector:**
   - Mode: `output_and_reset`

2. **Connect the Stitch node NOW:**
   - Image Collector (images) → XYZ Grid Stitch (images)
   - X labels: `red, blue, green`
   - Y labels: `10, 20, 30`
   - Z labels: (empty)

3. **Queue Prompt ONE TIME**
   - You'll get ONE grid with 9 images arranged in 3x3!

---

## Why Are You Getting Gray Boxes?

Gray boxes = 0 steps or no generation happening.

**Cause:** The Y value (string "10") isn't being converted to a number for steps.

**Fix:** Add the **XYZ String to Number** node between XYZ Grid Input and KSampler!

---

## Quick Troubleshooting

### Problem: Getting 9 separate grids
- **Cause:** Stitch node is connected during collection
- **Fix:** Disconnect Stitch during Steps 1-9, only connect for final run

### Problem: Gray boxes / no images
- **Cause:** Steps is receiving string "10" instead of integer 10
- **Fix:** Use XYZ String to Number node to convert

### Problem: Always same image
- **Cause:** Index isn't changing OR X values don't have commas
- **Fix:**
  - Make sure X values have commas: `red, blue, green`
  - Increment Index from 0 to 8 for each run

### Problem: "Collected 11/9 images"
- **Cause:** You collected too many images
- **Fix:** Change mode to `reset_only`, run once, then start over

---

## Example: Testing Steps (10, 20, 30)

### Collection Phase:
```
XYZ Grid Input: X="red, blue, green", Y="10, 20, 30", Index=0
    ↓ y_value = "10"
String to Number: text="10" → int_value=10
    ↓ int_value = 10
KSampler: steps=10
    ↓ image
Image Collector: mode=collect → "Collected 1/9"
```

Repeat 9 times with Index 0-8.

### Grid Creation Phase:
```
Image Collector: mode=output_and_reset → outputs all 9 images
    ↓ 9 images
XYZ Grid Stitch → creates 3x3 grid
    ↓ 1 grid image
Save Image → final output!
```

---

## TL;DR

1. **Restart ComfyUI** to load the new String to Number node
2. Use **XYZ String to Number** to convert Y values to integers for steps
3. **DON'T connect Stitch during collection** (runs 1-9)
4. **Connect Stitch only for final run** (after changing to output_and_reset mode)

That's it!
