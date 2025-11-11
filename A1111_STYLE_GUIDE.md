# XYZ Grid - A1111 Style Layout

## What is A1111 Style?

The A1111 (Automatic1111) style creates a grid layout where each X value gets its own labeled block, and within each block you see all Y×Z combinations. This makes it easy to compare different X values (like prompts) while testing Y and Z parameters.

## Visual Example

For X=red,blue,green | Y=10,20 | Z=5,6:

```
┌──────────────────────────────┐
│ X: red                       │
│       Z=5     Z=6            │
│ Y=10  [img1]  [img2]         │
│ Y=20  [img3]  [img4]         │
└──────────────────────────────┘

┌──────────────────────────────┐
│ X: blue                      │
│       Z=5     Z=6            │
│ Y=10  [img5]  [img6]         │
│ Y=20  [img7]  [img8]         │
└──────────────────────────────┘

┌──────────────────────────────┐
│ X: green                     │
│       Z=5     Z=6            │
│ Y=10  [img9]  [img10]        │
│ Y=20  [img11] [img12]        │
└──────────────────────────────┘
```

## How to Use It

1. **In XYZ Grid Stitch node:**
   - Set `layout_style` to **"A1111 Style (X blocks)"**

2. **Configure your axes:**
   - **X values**: The main thing you want to compare (prompts, styles, models)
   - **Y values**: First parameter to test (steps, denoise, etc.)
   - **Z values**: Second parameter to test (CFG, samplers, etc.)

3. **Run your workflow** and get a beautifully organized grid!

## Layout Details

- **X labels**: Displayed vertically on the left side of each block (rotated 90°)
- **Y labels**: Displayed on the left within each block (row labels)
- **Z labels**: Displayed at the top within each block (column labels)
- **Blocks**: Stacked vertically, one for each X value

## Common Use Cases

### Use Case 1: Prompt Comparison with Parameter Testing
```
X: "photo of a cat", "painting of a cat", "3D render of a cat"
Y: 10, 20, 30  (steps)
Z: 5.0, 7.0, 10.0  (CFG)
```

Result: 3 blocks (one per prompt), each showing a 3×3 grid of steps vs CFG

### Use Case 2: Style Testing
```
X: "realistic", "anime", "oil painting"
Y: 0.5, 0.75, 1.0  (denoise)
Z: "euler", "dpm++"  (samplers)
```

Result: 3 blocks (one per style), each showing denoise vs sampler combinations

### Use Case 3: Model Comparison
```
X: "model_A", "model_B", "model_C"
Y: 7.0, 9.0  (CFG)
Z: 20, 40  (steps)
```

Result: 3 blocks (one per model), each showing CFG vs steps combinations

## Why Use A1111 Style?

### Advantages:
1. **Clear organization**: Each X value is clearly separated
2. **Easy comparison**: Scan down the page to see how different X values perform
3. **Compact for 3D**: Better use of space when you have 3 variables
4. **Familiar**: If you're coming from A1111, this feels natural

### When to Use:
- When X is your primary variable of interest (prompts, models, styles)
- When you want to test 3 parameters (X, Y, Z)
- When you want vertical scanning of results

### When NOT to Use:
- When you only have 2 parameters (X, Y) - use regular 2D grid
- When Z has many values (blocks can get very wide)

## Comparison with Z Horizontal Style

### A1111 Style (X blocks):
```
X: red
    Z1  Z2
Y1  img img
Y2  img img

X: blue
    Z1  Z2
Y1  img img
Y2  img img
```
✅ Best for comparing X values
✅ Vertical layout
✅ Familiar from A1111

### Z Horizontal Style:
```
    Z1 Grid          Z2 Grid
    X1  X2           X1  X2
Y1  img img      Y1  img img
Y2  img img      Y2  img img
```
✅ Best for comparing Z values
✅ Horizontal layout
✅ Traditional grid style

## Tips

1. **Keep Z values reasonable**: 2-3 Z values work best. More than 4 makes blocks very wide.

2. **X is for major comparisons**: Put your main variable (prompts, models) in X.

3. **Y and Z for parameters**: Put numeric parameters (steps, CFG, denoise) in Y and Z.

4. **Adjust label sizes**:
   - `label_height`: Controls Z label area at top (default 40)
   - `label_width`: Controls Y label area on left (default 80)
   - Increase if labels are cut off

5. **Use descriptive X labels**: Since X labels are prominent, make them clear!

## Example Workflow

```
1. XYZ Grid Input:
   X: red car, blue car, green car
   Y: 10, 20, 30
   Z: 5, 7

2. Connect to generators with:
   - x_value → prompt
   - y_value → String to Number → steps
   - z_value → String to Number → CFG

3. XYZ Grid Stitch:
   - layout_style: "A1111 Style (X blocks)"
   - X labels: red car, blue car, green car
   - Y labels: 10, 20, 30
   - Z labels: 5, 7

4. Result: 3 blocks showing each car color,
           with all combinations of steps and CFG!
```

## That's It!

The A1111 style gives you that familiar organized layout from Automatic1111, making it easy to compare prompts and parameters at a glance!
