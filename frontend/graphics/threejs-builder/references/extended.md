# Extended guidance

### Animated Background with Foreground Object
```javascript
const gridHelper = new THREE.GridHelper(50, 50, 0x444444, 0x222222); // Background grid
scene.add(gridHelper);

const mainGeometry = new THREE.IcosahedronGeometry(1, 0); // Foreground object
const mainMaterial = new THREE.MeshStandardMaterial({
    color: 0xff6600,
    flatShading: true
});
const mainMesh = new THREE.Mesh(mainGeometry, mainMaterial);
scene.add(mainMesh);
```

---

## Colors

Three.js uses hexadecimal color format: `0xRRGGBB`

Common hex colors:
- Black: `0x000000`, White: `0xffffff`
- Red: `0xff0000`, Green: `0x00ff00`, Blue: `0x0000ff`
- Cyan: `0x00ffff`, Magenta: `0xff00ff`, Yellow: `0xffff00`
- Orange: `0xff8800`, Purple: `0x8800ff`, Pink: `0xff0088`

---

## Anti-Patterns to Avoid

### Basic Setup Mistakes

❌ **Not importing OrbitControls from correct path**
Why bad: Controls won't load, `THREE.OrbitControls` is undefined in modern Three.js
Better: Use `import { OrbitControls } from 'three/addons/controls/OrbitControls.js'` or unpkg examples/jsm path

❌ **Forgetting to add object to scene**
Why bad: Object won't render, silent failure
Better: Always call `scene.add(object)` after creating meshes/lights

❌ **Using old `requestAnimationFrame` pattern instead of `setAnimationLoop`**
Why bad: More verbose, doesn't handle XR/WebXR automatically
Better: `renderer.setAnimationLoop((time) => { ... })`

### Performance Issues

❌ **Creating new geometries in animation loop**
Why bad: Massive memory allocation, frame rate collapse
Better: Create geometry once, reuse it. Transform only position/rotation/scale

❌ **Using too many segments on primitives**
Why bad: Unnecessary vertices, GPU overhead
Better: Default segments are usually fine. `SphereGeometry(1, 32, 16)` not `SphereGeometry(1, 128, 64)`

❌ **Not setting pixelRatio cap**
Why bad: 4K/5K displays run at full resolution, poor performance
Better: `Math.min(window.devicePixelRatio, 2)`

### Code Organization

❌ **Everything in one giant function**
Why bad: Hard to modify, hard to debug
Better: Separate setup into functions: `createScene()`, `createLights()`, `createMeshes()`

❌ **Hardcoding all values**
Why bad: Difficult to tweak and experiment
Better: Define constants at top: `const CONFIG = { color: 0x00ff88, speed: 0.001 }`

---

## Variation Guidance

**IMPORTANT**: Each Three.js app should feel unique and context-appropriate.

**Vary by scenario**:
- **Portfolio/showcase**: Elegant, smooth animations, muted colors
- **Game/interactive**: Bright colors, snappy controls, particle effects
- **Data visualization**: Clean lines, grid helpers, clear labels
- **Background effect**: Subtle, slow movement, dark/gradient backgrounds
- **Product viewer**: Realistic lighting, PBR materials, smooth orbit

**Vary visual elements**:
- **Geometry choice**: Not everything needs to be a cube. Explore spheres, tori, icosahedra
- **Material style**: Mix flat shaded, glossy, metallic, wireframe
- **Color palettes**: Use complementary, analogous, or monochromatic schemes
- **Animation style**: Rotation, oscillation, wave motion, mouse tracking

**Avoid converging on**:
- Default green cube as first example every time
- Same camera angle (front-facing, z=5)
- Identical lighting setup (always directional light at 1,1,1)

---

## Remember

**Three.js is a tool for interactive 3D on the web.**

Effective Three.js apps:
- Start with the scene graph mental model
- Use primitives as building blocks
- Keep animations simple and performant
- Vary visual style based on purpose
- Import from modern ES module paths

**Modern Three.js (r150+) uses ES modules from `three` package or CDN.** CommonJS patterns and global `THREE` variable are legacy.

For advanced topics (GLTF models, shaders, post-processing), see references/advanced-topics.md.

**Claude is capable of creating elegant, performant 3D web experiences. These patterns guide the way—they don't limit the result.**

---

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

---

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
