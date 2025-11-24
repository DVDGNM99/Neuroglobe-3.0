# Neuroglobe Project Context Document
**Project Root Directory:** `C:\Allen_for_Brainglobe\Neuroglobe`
**GitHub Repository:** `https://github.com/DVDGNM99/Neuroglobe.git`

## 1. Project Overview & Core Philosophy
Neuroglobe is a tool designed to bridge the Allen Institute Mouse Connectivity Atlas data with the BrainGlobe visualization ecosystem (specifically brainrender).

**Key Architectural Principle:** Strict Decoupled Architecture. We operate two separate, isolated domains to solve "dependency hell" common in scientific Python (specifically conflicts between AllenSDK and VTK/Qt used by BrainGlobe).

* **Domain A (Miner):** Extracts and processes data using `allensdk`.
* **Domain B (Viewer):** Renders data using `brainrender` and a GUI based on `dearpygui`.

**Handover:** These domains communicate **only via files** (CSV/JSON) located in the `data/` directory. They never import each other's code.

## 2. Execution History (Current Status)
We have successfully completed Phase 0 (Foundation), Phase 1 (The Miner), and Phase 2 (The Viewer).
**Current Phase: Phase 3 (Interactivity & Persistence).** The viewer has been upgraded with advanced camera controls, HUD, and automated screenshot/metadata saving.

### Major Achievements:
* **Environment Stability:** Rigid layout with pinned environments (Python 3.10/NumPy 1.23.5) on Windows.
* **Data Pipeline:** Robust fetching, ontology mapping, and "Black Brain" occlusion filtering.
* **Interactive Viewer:**
    * **Hybrid Engine:** Uses `brainrender` for data loading but bypasses wrappers to use `vedo` directly for callbacks.
    * **HUD & Colorbar:** On-screen instructions and Plasma scalar bar added via `vedo.Text2D` and `vedo.Sphere`.
    * **Snap Views:** Implemented hard-coded VTK camera positioning for standard views.
    * **Structured Saving:** Pressing 'S' saves transparent screenshots and experiment metadata (YAML) into timestamped folders.

## 3. Current Directory Structure & File Contents

### Root Files
* `.gitignore`: Configured to ignore raw/processed data and system files.
* `ROADMAP.md`: Documentation and planning file.

### Directory: `configs/` (User Control Panels)
* `mining_config.yaml`: Parameters for extraction (Seed acronym, metrics, custom targets).
* `visual_config.yaml`: Settings for rendering appearance.
* `regions.json`: JSON ontology used by the Viewer GUI.

### Directory: `data/` (The Handover Zone)
* `raw/`: Managed by AllenSDK.
* `processed/`: Contains CSV outputs (`<seed>_connectivity.csv`, `<seed>_demo_filtered.csv`).

### Directory: `scenes/` (New - Output Zone)
* Generated automatically by the Viewer.
* Structure: `scenes/<Seed>_<Timestamp>/`
    * `screenshot_HHMMSS.png`: Transparent high-res capture.
    * `metadata.yml`: Contains experiment seed, timestamp, regions rendered, and camera state.

### Directory: `envs/` (Conda Specifications)
* `allensdk.yml`: Environment for Domain A.
* `brainglobe_render.yml`: Environment for Domain B.

### Directory: `src/` (Source Code)

#### Subdirectory: `src/miner/` (Domain A - Stable)
* `fetch.py`: Connects to Allen API to retrieve Experiment IDs.
* `aggregate.py`: Downloads `structure_unionize` data, builds ontology map manually, and flags the Injection Seed.
* `filter_for_demo.py`: Post-processing. Removes generic parents (root, Isocortex) and applies Custom or Top-5 filtering logic.

#### Subdirectory: `src/viewer/` (Domain B - Enhanced)
* `logic.py`: Handles CSV parsing and color normalization.
* **`rendering.py` (The Engine):**
    * **Direct Vedo Integration:** Uses `scene.plotter.add_callback` to handle input.
    * **Camera Logic:** Manually sets VTK camera position relative to Bregma coordinates.
    * **Controls:**
        * **`X`**: Side View (Sagittal).
        * **`Y`**: Front View (Coronal).
        * **`Z`**: Top View (Dorsal).
        * **`S`**: Save Scene (Screenshot + Metadata).
        * **`1-9`**: Native Vedo style/color toggles.
    * **IMPORTANT NOTE:** Due to VTK window focus behavior, **keys X, Y, and Z must be pressed TWICE** to trigger the camera snap.
* **`main.py` (The Orchestrator):**
    * Manages the Dear PyGui Interface.
    * Prepares filesystem (creates `scenes/` subfolders).
    * Passes metadata contexts to the rendering engine.
    * Displays absolute paths in the console for easy file location.