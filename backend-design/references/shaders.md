# Shaders and GPU Pipeline (Concise Reference)

Purpose: Provide a compact mental model of the GPU shader pipeline, shader types, and key graphics concepts for cross-domain architecture discussions.

## Core ideas
- A shader is a program that runs in parallel on the GPU to compute per-vertex or per-fragment outputs.
- GPUs optimize throughput (many simple cores) rather than latency (few powerful cores).
- Shader instances cannot share mutable state; they receive per-invocation inputs plus shared constants (uniforms).

## Graphics pipeline (simplified)
1. Vertex shading: transform each vertex (model -> world -> view -> projection) and emit varyings.
2. Rasterization: convert primitives (usually triangles) into fragments, interpolate varyings.
3. Fragment shading: compute final pixel color (lighting, textures, materials).
4. Tests and output: depth/stencil tests, blending, write to framebuffer.

## Key shader concepts
- Uniforms: constant inputs for all shader invocations in a draw call.
- Varyings: values passed from vertex to fragment stages (interpolated).
- Vertex vs fragment shaders: vertex transforms geometry; fragment computes pixel color.
- Compute shaders: general GPU compute outside the rendering pipeline; can feed results into graphics stages.

## Lighting and shading (high level)
- Ambient: baseline light contribution.
- Diffuse: brightness based on angle between surface normal and light direction.
- Specular: highlights based on view direction and reflection vector.

## APIs and languages (high level)
- OpenGL / WebGL: legacy but common; GLSL for shaders.
- Vulkan / WebGPU: modern; WebGPU replaces WebGL in browsers.
- Metal (Apple), Direct3D (Microsoft), CUDA (NVIDIA compute).

## Practical architecture implications
- GPU-friendly work is embarrassingly parallel with minimal branching and no cross-invocation dependencies.
- CPU handles orchestration and data upload; GPU handles bulk parallel compute.
- Shader pipelines are deterministic given inputs; performance depends on vertex/fragment counts and memory bandwidth.

