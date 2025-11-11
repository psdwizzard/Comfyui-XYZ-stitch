# XYZ Grid - Understanding the Axes

## How the Axes Work

Think of it like this:
- **X axis** = Columns (left to right)
- **Y axis** = Rows (top to bottom)
- **Z axis** = Separate grids (side by side)

## Visual Layout

### With X and Y only (2D Grid):
```
        X1      X2      X3
Y1      img1    img2    img3
Y2      img4    img5    img6
Y3      img7    img8    img9
```
Result: One 3x3 grid

### With X, Y, and Z (3D Grid):
```
Z1:                         Z2:
        X1      X2                  X1      X2
Y1      img1    img2        Y1      img5    img6
Y2      img3    img4        Y2      img7    img8
```
Result: Two separate 2x2 grids shown side by side

## Common Use Cases

### Testing Prompts and Steps
```
X values: red car, blue car, green car
Y values: 10, 20, 30  (steps)
Z values: (empty)
```
Result: 3x3 grid showing 9 combinations
- Columns show different prompts
- Rows show different step counts

### Testing CFG Scale and Steps
```
X values: 10, 20, 30  (steps)
Y values: 5.0, 7.0, 10.0  (CFG scale)
Z values: (empty)
```
Result: 3x3 grid showing 9 combinations
- Columns show different step counts
- Rows show different CFG values

### Testing Multiple Samplers with Prompts and Steps
```
X values: red, blue  (prompts)
Y values: 10, 20  (steps)
Z values: euler, dpm++, ddim  (samplers)
```
Result: Three 2x2 grids (one for each sampler)
- Each grid shows combinations of prompts (columns) and steps (rows)
- Each Z value creates a separate grid

## Label Positions

- **X labels** (white text): Top of each column
- **Y labels** (white text): Left side of each row
- **Z labels** (white text): Very top, centered over each grid

## Your Current Setup

Looking at your console output:
```
X=red, Y=10, Z=5
X=blue, Y=20, Z=6
```

You have:
- X: red, blue → 2 columns
- Y: 10, 20 → 2 rows
- Z: 5, 6 → 2 separate grids

**If 5 and 6 are CFG values**, you should move them to the Y axis instead:
```
X values: red, blue
Y values: 5, 6  (CFG)
Z values: (empty)
```

This will give you one 2x2 grid with:
- Columns: red, blue (prompts)
- Rows: 5, 6 (CFG values)

## Tips

1. **Use X for the thing you want to compare horizontally** (usually prompts or styles)
2. **Use Y for the parameter you want to test vertically** (usually numeric values like steps, CFG)
3. **Use Z only if you need a third dimension** (like testing multiple samplers or models)
4. **Leave Z empty for simpler 2D grids** - most use cases only need X and Y

## Examples

### Example 1: Prompt Comparison
```
X: "photo of a cat", "painting of a cat", "3D render of a cat"
Y: 7.0, 8.5, 10.0  (CFG)
Z: (empty)
```
Result: 3x3 grid comparing prompts at different CFG values

### Example 2: Parameter Sweep
```
X: 10, 15, 20, 25, 30  (steps)
Y: 6.0, 7.0, 8.0, 9.0  (CFG)
Z: (empty)
```
Result: 5x4 = 20 image grid for parameter optimization

### Example 3: Multi-Model Comparison
```
X: positive prompt variations
Y: negative prompt variations
Z: model1, model2, model3
```
Result: Three separate grids, one for each model

## Fixing Your Current Issue

Based on your console output showing Z=5,6:

**If these should be CFG values:**
1. Move "5, 6" from Z values to Y values
2. Clear Z values (leave empty)
3. Now you'll get one grid instead of two

**If these are actually meant to be Z values:**
- Keep them as is
- But make sure you understand you're getting 2 separate grids side by side
- Each grid will have its own X and Y labels
