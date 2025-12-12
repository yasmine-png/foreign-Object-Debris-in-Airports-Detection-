"""
Script pour créer 3 vidéos de test avec effet de piste continue - drone qui monte de bas en haut
Toutes les images sont alignées sur une seule piste verticale
"""
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "backend"

def create_continuous_track_video(output_filename, images_to_use=None, fps=30, speed=100):
    """
    Crée une vidéo où toutes les images sont sur une piste continue
    Le drone monte de bas en haut pour révéler les images
    
    Args:
        output_filename: Nom du fichier vidéo de sortie
        images_to_use: Liste d'images à utiliser (None = toutes les images)
        fps: Images par seconde
        speed: Vitesse de défilement en pixels/seconde
    """
    OUTPUT_VIDEO = OUTPUT_DIR / output_filename
    
    # Lister toutes les images
    all_image_files = sorted(list(IMAGES_DIR.glob("*.png")) + list(IMAGES_DIR.glob("*.jpg")))
    
    if len(all_image_files) == 0:
        print(f"❌ Aucune image trouvée dans {IMAGES_DIR}")
        return False
    
    # Sélectionner les images à utiliser
    if images_to_use is None:
        image_files = all_image_files
    else:
        image_files = images_to_use
    
    print(f"\n📹 Création de '{output_filename}' avec {len(image_files)} images...")
    
    # Lire toutes les images et les redimensionner à la même taille
    images = []
    for img_path in image_files:
        img = cv2.imread(str(img_path))
        if img is not None:
            # Redimensionner à 640x480 pour une meilleure qualité
            img = cv2.resize(img, (640, 480))
            images.append(img)
    
    if len(images) == 0:
        print("❌ Aucune image valide trouvée")
        return False
    
    # Créer la piste continue : toutes les images empilées verticalement
    img_height, img_width = images[0].shape[:2]
    track_height = img_height * len(images)
    track_width = img_width
    
    # Créer la piste complète
    full_track = np.zeros((track_height, track_width, 3), dtype=np.uint8)
    for i, img in enumerate(images):
        y_start = i * img_height
        full_track[y_start:y_start+img_height, :] = img
    
    print(f"📐 Piste créée: {track_width}x{track_height} pixels")
    
    # Dimensions de la vidéo (fenêtre visible)
    video_height = img_height
    video_width = img_width
    
    # Calculer le nombre de frames nécessaires
    # Le drone doit monter de 0 à (track_height - video_height)
    total_distance = track_height - video_height
    total_frames = int((total_distance / speed) * fps)
    duration = total_frames / fps
    
    print(f"⚙️  Configuration:")
    print(f"   - FPS: {fps}")
    print(f"   - Vitesse: {speed} pixels/seconde")
    print(f"   - Frames totales: {total_frames}")
    print(f"   - Durée: {duration:.1f} secondes")
    
    # Créer le writer vidéo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(OUTPUT_VIDEO), fourcc, fps, (video_width, video_height))
    
    if not out.isOpened():
        print(f"❌ Erreur: Impossible de créer le fichier vidéo")
        return False
    
    # Générer chaque frame : la fenêtre monte progressivement
    for frame_num in range(total_frames):
        # Position Y de la fenêtre (de bas en haut)
        progress = frame_num / max(total_frames - 1, 1)
        y_position = int(progress * total_distance)
        
        # Extraire la portion visible de la piste
        frame = full_track[y_position:y_position+video_height, :video_width].copy()
        
        out.write(frame)
        
        # Afficher la progression
        if (frame_num + 1) % 30 == 0:
            percent = int((frame_num + 1) / total_frames * 100)
            print(f"   Progression: {percent}%", end='\r')
    
    out.release()
    
    if OUTPUT_VIDEO.exists():
        file_size_mb = OUTPUT_VIDEO.stat().st_size / (1024 * 1024)
        print(f"\n✅ Vidéo créée avec succès!")
        print(f"📁 Fichier: {OUTPUT_VIDEO}")
        print(f"📊 Taille: {file_size_mb:.2f} MB")
        print(f"⏱️  Durée: {duration:.1f} secondes")
        return True
    else:
        print(f"\n❌ Erreur: La vidéo n'a pas été créée")
        return False

def create_3_test_videos():
    """
    Crée 3 vidéos de test avec des configurations différentes
    """
    # Lister toutes les images disponibles
    all_image_files = sorted(list(IMAGES_DIR.glob("*.png")) + list(IMAGES_DIR.glob("*.jpg")))
    
    if len(all_image_files) == 0:
        print(f"❌ Aucune image trouvée dans {IMAGES_DIR}")
        return
    
    print(f"📸 {len(all_image_files)} images trouvées")
    print("=" * 60)
    
    # Vidéo 1: Rapide - toutes les images, vitesse élevée
    print("\n🎬 VIDÉO 1: Rapide (toutes les images, vitesse élevée)")
    success1 = create_continuous_track_video(
        output_filename="test_video_1_rapide.mp4",
        images_to_use=all_image_files,
        fps=30,
        speed=150  # Vitesse rapide
    )
    
    # Vidéo 2: Lente - toutes les images, vitesse faible
    print("\n🎬 VIDÉO 2: Lente (toutes les images, vitesse faible)")
    success2 = create_continuous_track_video(
        output_filename="test_video_2_lente.mp4",
        images_to_use=all_image_files,
        fps=30,
        speed=50  # Vitesse lente
    )
    
    # Vidéo 3: Moyenne - sélection d'images (une sur deux)
    selected_images = all_image_files[::2]  # Prendre une image sur deux
    print(f"\n🎬 VIDÉO 3: Moyenne (sélection de {len(selected_images)} images, vitesse moyenne)")
    success3 = create_continuous_track_video(
        output_filename="test_video_3_moyenne.mp4",
        images_to_use=selected_images,
        fps=30,
        speed=100  # Vitesse moyenne
    )
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES VIDÉOS CRÉÉES:")
    print("=" * 60)
    if success1:
        print("✅ test_video_1_rapide.mp4 - Vidéo rapide")
    if success2:
        print("✅ test_video_2_lente.mp4 - Vidéo lente")
    if success3:
        print("✅ test_video_3_moyenne.mp4 - Vidéo moyenne")
    print("\n🎉 Toutes les vidéos sont prêtes pour les tests!")

if __name__ == "__main__":
    create_3_test_videos()
