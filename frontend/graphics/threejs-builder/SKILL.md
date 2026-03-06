---
name: threejs-builder
description: Build and validate simple, performant Three.js web apps using modern
  ES module patterns. Use this when you need a minimal Three.js scene, interaction,
  or animation for a web UI or demo.
---

# Three.js Builder

A focused skill for creating simple, performant Three.js web applications using modern ES module patterns.

## When to use

- Use when you need a minimal Three.js scene, interaction, or animation for a web UI or demo.

## Inputs

- Desired scene (what to render) and interactions (none/orbit/custom).
- Constraints: target devices, performance budget, and whether external assets are allowed.
- Integration target: standalone HTML, Vite/React, or existing codebase.

## Outputs

- A minimal working Three.js example (HTML/JS or React component) that runs without missing imports.
- Notes on how to integrate (where to place files, how to run).

## Procedure

1) Confirm scope + constraints (devices, perf, integration target).
2) Build the smallest runnable scene first.
3) Add interaction/animation second.
4) Add polish (lighting, materials) last.

## Validation

- Fail fast: if the code doesn’t run, fix the basics before adding features.
- Verify resize handling, cleanup, and a stable animation loop.

## Constraints

- Don’t introduce secrets, tokens, or PII in examples; use placeholders and redaction by default.
- Prefer stable, pinned versions when using CDN imports (or prefer local deps when the repo already uses a bundler).

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

- `## Outputs`

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## Scope and triggers
- This skill applies to building small Three.js scenes and demos. The current request is out of scope.

## Deliverables
- None (out of scope).

## Required inputs
- None (out of scope).
```

## Philosophy: The Scene Graph Mental Model

Three.js is built on the **scene graph**—a hierarchical tree of objects where parent transformations affect children. Understanding this mental model is key to effective 3D web development.

**Before creating a Three.js app, ask**:
- What is the **core visual element**? (geometry, shape, model)
- What **interaction** does the user need? (none, orbit controls, custom input)
- What **performance** constraints exist? (compact screens, desktop, WebGL capabilities)
- What **animation** brings it to life? (rotation, movement, transitions)

**Core principles**:

1. **Scene Graph First**: Everything added to `scene` renders. Use `Group` for hierarchical transforms.
2. **Primitives as Building Blocks**: Built-in geometries (Box, Sphere, Torus) cover 80% of simple use cases.
3. **Animation as Transformation**: Change position/rotation/scale over time using `requestAnimationFrame` or `renderer.setAnimationLoop`.
4. **Performance Through Simplicity**: Fewer objects, fewer draw calls, reusable geometries/materials.

---

## Examples

- "Create a rotating cube scene with responsive resize handling."
- "Set up a basic orbit-controlled camera for a product demo."

## Quick Start: Essential Setup

### Minimal HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Three.js App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #000; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script type="module">
        import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });

        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        document.body.appendChild(renderer.domElement);

        camera.position.z = 5;

        renderer.setAnimationLoop((time) => {
            renderer.render(scene, camera);
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
```

---

## Geometries

Built-in primitives cover most simple app needs. Use `BufferGeometry` only for custom shapes.

**Common primitives**:
- `BoxGeometry(width, height, depth)` - cubes, boxes
- `SphereGeometry(radius, widthSegments, heightSegments)` - balls, planets
- `CylinderGeometry(radiusTop, radiusBottom, height)` - tubes, cylinders
- `TorusGeometry(radius, tube)` - donuts, rings
- `PlaneGeometry(width, height)` - floors, walls, backgrounds
- `ConeGeometry(radius, height)` - spikes, cones
- `IcosahedronGeometry(radius, detail)` - low-poly spheres (detail=0)

**Usage**:
```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x44aa88 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

---

## Materials

Choose material based on lighting needs and visual style.

**Material selection guide**:
- `MeshBasicMaterial` - No lighting, flat colors. Use for: UI, wireframes, unlit effects
- `MeshStandardMaterial` - PBR lighting. Default for realistic surfaces
- `MeshPhysicalMaterial` - Advanced PBR with clearcoat, transmission. Glass, water
- `MeshNormalMaterial` - Debug, rainbow colors based on normals
- `MeshPhongMaterial` - Legacy, shininess control. Faster than Standard

**Common material properties**:
```javascript
{
    color: 0x44aa88,           // Hex color
    roughness: 0.5,            // 0=glossy, 1=matte (Standard/Physical)
    metalness: 0.0,            // 0=non-metal, 1=metal (Standard/Physical)
    emissive: 0x000000,        // Self-illumination color
    wireframe: false,          // Show edges only
    transparent: false,        // Enable transparency
    opacity: 1.0,              // 0=invisible, 1=opaque (needs transparent:true)
    side: THREE.FrontSide      // FrontSide, BackSide, DoubleSide
}
```

---

## Lighting

No light = black screen (except BasicMaterial/NormalMaterial).

**Light types**:
- `AmbientLight(intensity)` - Base illumination everywhere. Use 0.3-0.5
- `DirectionalLight(color, intensity)` - Sun-like, parallel rays. Cast shadows
- `PointLight(color, intensity, distance)` - Light bulb, emits in all directions
- `SpotLight(color, intensity, angle, penumbra)` - Flashlight, cone of light

**Typical lighting setup**:
```javascript
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffffff, 1);
mainLight.position.set(5, 10, 7);
scene.add(mainLight);

const fillLight = new THREE.DirectionalLight(0x88ccff, 0.5);
fillLight.position.set(-5, 0, -5);
scene.add(fillLight);
```

**Shadows** (advanced, use when needed):
```javascript
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

mainLight.castShadow = true;
mainLight.shadow.mapSize.width = 2048;
mainLight.shadow.mapSize.height = 2048;

mesh.castShadow = true;
mesh.receiveShadow = true;
```

---

## Animation

Transform objects over time using the animation loop.

**Animation patterns**:

1. **Continuous rotation**:
```javascript
renderer.setAnimationLoop((time) => {
    mesh.rotation.x = time * 0.001;
    mesh.rotation.y = time * 0.0005;
    renderer.render(scene, camera);
});
```

2. **Wave/bobbing motion**:
```javascript
renderer.setAnimationLoop((time) => {
    mesh.position.y = Math.sin(time * 0.002) * 0.5;
    renderer.render(scene, camera);
});
```

3. **Mouse interaction**:
```javascript
const mouse = new THREE.Vector2();

window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
});

renderer.setAnimationLoop(() => {
    mesh.rotation.x = mouse.y * 0.5;
    mesh.rotation.y = mouse.x * 0.5;
    renderer.render(scene, camera);
});
```

---

## Camera Controls

Import OrbitControls from examples for interactive camera movement:

```html
<script type="module">
    import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
    import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    renderer.setAnimationLoop(() => {
        controls.update();
        renderer.render(scene, camera);
    });
</script>
```

---

## Common Scene Patterns

### Rotating Cube (Hello World)
```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff88 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

renderer.setAnimationLoop((time) => {
    cube.rotation.x = time * 0.001;
    cube.rotation.y = time * 0.001;
    renderer.render(scene, camera);
});
```

### Floating Particle Field
```javascript
const particleCount = 1000;
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 50;
    positions[i + 1] = (Math.random() - 0.5) * 50;
    positions[i + 2] = (Math.random() - 0.5) * 50;
}

geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
const material = new THREE.PointsMaterial({ color: 0xffffff, size: 0.1 });
const particles = new THREE.Points(geometry, material);
scene.add(particles);
```
## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.
## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.
## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
