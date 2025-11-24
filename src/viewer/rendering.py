import yaml
import numpy as np
from pathlib import Path
from datetime import datetime
from brainglobe_atlasapi import BrainGlobeAtlas
from brainrender import Scene, settings, actors

# Importiamo Text2D e Sphere direttamente da vedo
from vedo import Text2D, Sphere

# --- CONFIGURAZIONE ESTETICA ---
settings.SHOW_AXES = False 
settings.WHOLE_SCREEN = False
settings.BACKGROUND_COLOR = "white"
settings.SCREENSHOT_TRANSPARENT_BACKGROUND = True 

# Coordinate approssimative del centro del cervello (Allen CCFv3)
# Servono per dire alla telecamera dove guardare.
BREGMA_CENTER = [6500, 3800, 5600] 

class RenderEngine:
    def __init__(self, atlas_name="allen_mouse_25um"):
        print(f"Initializing Atlas: {atlas_name}...")
        self.atlas = BrainGlobeAtlas(atlas_name)
        self.atlas_name = atlas_name

    def validate_regions(self, regions: list) -> tuple:
        valid = []
        invalid = []
        for r in regions:
            try:
                _ = self.atlas.structure_from_acronym(r)
                valid.append(r)
            except Exception:
                invalid.append(r)
        return valid, invalid

    def render_scene(self, region_config: list, alpha=0.5, output_dir: Path = None, metadata: dict = None):
        """
        Render engine con telecamera programmata manualmente (VTK logic).
        """
        scene = Scene(atlas_name=self.atlas_name, title="")
        
        # --- 1. Regioni ---
        print(f"Building scene with {len(region_config)} regions...")
        missing_meshes = []

        for item in region_config:
            acr = item['acronym']
            col = item['color']
            try:
                scene.add_brain_region(acr, alpha=alpha, color=col)
            except Exception as e:
                missing_meshes.append(acr)

        # --- 2. HUD ---
        legend_text = (
            "CONTROLS:\n"
            "[X] Side View (Sagittal)\n"
            "[Y] Front View (Coronal)\n"
            "[Z] Top View (Dorsal)\n"
            "-----------------\n"
            "[S] Save Scene"
        )
        
        hud = Text2D(legend_text, pos="bottom-left", s=0.9, c="black", font="Calco")
        scene.add(hud)

        # --- 3. Colorbar ---
        try:
            dummy_mesh = Sphere(r=0, res=20).pos(0,0,0).alpha(0)
            dummy_mesh.cmap("plasma", list(range(dummy_mesh.npoints)))
            scene.add(dummy_mesh)
            scene.plotter.add_scalar_bar(
                dummy_mesh, title="Density", pos=(0.85, 0.05),
                nlabels=3, c="black", fmt="High"
            )
        except Exception:
            pass

        # --- 4. LOGICA CALLBACK (Telecamera Manuale) ---
        def on_keypress(event):
            key = event.keypress
            if not key: return

            # Otteniamo la telecamera VTK direttamente
            # Questo bypassa qualsiasi blocco di brainrender
            cam = scene.plotter.camera
            
            # [Z] TOP VIEW (Dorsal)
            # Guarda dall'alto (asse Y negativo in Allen CCF spesso)
            if key == 'z':
                print("[CAM] View: Top (Z)")
                # Posizioniamo la camera molto in alto sopra il centro
                cam.SetPosition(BREGMA_CENTER[0], -10000, BREGMA_CENTER[2])
                cam.SetFocalPoint(BREGMA_CENTER[0], BREGMA_CENTER[1], BREGMA_CENTER[2])
                # Orientiamo l'"alto" della camera lungo l'asse X
                cam.SetViewUp(1, 0, 0)
                scene.plotter.reset_camera()

            # [X] SIDE VIEW (Sagittal)
            # Guarda dal lato (asse Z)
            elif key == 'x':
                print("[CAM] View: Side (X)")
                cam.SetPosition(BREGMA_CENTER[0], BREGMA_CENTER[1], 20000)
                cam.SetFocalPoint(BREGMA_CENTER[0], BREGMA_CENTER[1], BREGMA_CENTER[2])
                cam.SetViewUp(0, -1, 0)
                scene.plotter.reset_camera()

            # [Y] FRONT VIEW (Coronal)
            # Guarda da davanti (asse X)
            elif key == 'y':
                print("[CAM] View: Front (Y)")
                cam.SetPosition(20000, BREGMA_CENTER[1], BREGMA_CENTER[2])
                cam.SetFocalPoint(BREGMA_CENTER[0], BREGMA_CENTER[1], BREGMA_CENTER[2])
                cam.SetViewUp(0, -1, 0)
                scene.plotter.reset_camera()
            
            # [S] SAVE
            elif key == 's':
                if output_dir and metadata:
                    timestamp_shot = datetime.now().strftime("%H%M%S")
                    shot_name = f"screenshot_{timestamp_shot}.png"
                    shot_path = output_dir / shot_name
                    print(f"\n[NEUROGLOBE] Saving: {shot_path}")
                    scene.screenshot(name=str(shot_path))
                    
                    meta_path = output_dir / "metadata.yml"
                    try:
                        with open(meta_path, 'w') as f:
                            yaml.dump(metadata, f, sort_keys=False)
                        print("[NEUROGLOBE] Metadata saved.")
                    except Exception as e:
                         print(f"Error saving YAML: {e}")
                else:
                    print("[ERROR] Save dir missing.")

        # Aggancio al motore
        scene.plotter.add_callback('keypress', on_keypress)

        print("\n--- RENDER LOOP STARTED ---")
        print("Use keys [X, Y, Z] to snap view. [S] to save.")
        scene.render()
        
        return missing_meshes