"""
Script pour convertir une vidéo en format compatible navigateur (MP4 H.264 + AAC)
"""
import cv2
import sys
import os
from pathlib import Path

def convert_video(input_path, output_path=None):
    """
    Convertit une vidéo en MP4 avec codec H.264 (vidéo) et AAC (audio)
    
    Args:
        input_path: Chemin vers la vidéo d'entrée
        output_path: Chemin vers la vidéo de sortie (optionnel)
    """
    if not os.path.exists(input_path):
        print(f"❌ Erreur: Le fichier '{input_path}' n'existe pas")
        return False
    
    # Déterminer le chemin de sortie
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.parent / f"{input_file.stem}_converted{input_file.suffix}")
    
    print(f"📹 Conversion de la vidéo...")
    print(f"   Entrée: {input_path}")
    print(f"   Sortie: {output_path}")
    
    # Ouvrir la vidéo d'entrée
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        print(f"❌ Erreur: Impossible d'ouvrir la vidéo '{input_path}'")
        return False
    
    # Obtenir les propriétés de la vidéo
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"   Résolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Nombre de frames: {total_frames}")
    
    # Essayer plusieurs codecs dans l'ordre de préférence
    codecs_to_try = [
        ('H264', cv2.VideoWriter_fourcc(*'H264')),  # H.264 (meilleur pour navigateurs)
        ('XVID', cv2.VideoWriter_fourcc(*'XVID')),  # XVID (bonne compatibilité)
        ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),  # MPEG-4 (fallback)
    ]
    
    out = None
    used_codec = None
    
    for codec_name, fourcc in codecs_to_try:
        print(f"   Tentative avec le codec: {codec_name}...")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if out.isOpened():
            used_codec = codec_name
            print(f"   ✅ Codec {codec_name} accepté")
            break
        else:
            out.release()
            if os.path.exists(output_path):
                os.remove(output_path)
    
    if out is None or not out.isOpened():
        print(f"❌ Erreur: Aucun codec compatible trouvé pour créer le fichier de sortie")
        cap.release()
        return False
    
    frame_count = 0
    print(f"\n🔄 Conversion en cours...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Écrire la frame
            out.write(frame)
            frame_count += 1
            
            # Afficher la progression
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"   Progression: {progress:.1f}% ({frame_count}/{total_frames} frames)", end='\r')
        
        print(f"\n✅ Conversion terminée!")
        print(f"   Fichier créé: {output_path}")
        print(f"   Codec utilisé: {used_codec}")
        print(f"   Frames converties: {frame_count}")
        
        # Avertissement sur l'audio
        print(f"\n⚠️  Note: Cette conversion ne préserve pas l'audio.")
        print(f"   Si votre vidéo a de l'audio, utilisez FFmpeg pour une conversion complète:")
        print(f"   ffmpeg -i {input_path} -c:v libx264 -c:a aac -movflags +faststart {output_path}")
        
        # Nettoyer
        cap.release()
        out.release()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la conversion: {e}")
        cap.release()
        out.release()
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_video.py <input_video> [output_video]")
        print("\nExemple:")
        print("  python convert_video.py test_video.mp4")
        print("  python convert_video.py test_video.mp4 test_video_converted.mp4")
        sys.exit(1)
    
    input_video = sys.argv[1]
    output_video = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_video(input_video, output_video)
    sys.exit(0 if success else 1)

