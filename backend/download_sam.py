"""
Script pour télécharger le modèle SAM avec reprise automatique
"""
import os
import urllib.request
from pathlib import Path

def download_file(url: str, filename: str):
    """Télécharge un fichier avec barre de progression"""
    filepath = Path(filename)
    
    # Vérifier si le fichier existe déjà
    if filepath.exists():
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"📁 Fichier existant: {size_mb:.2f} MB")
        
        # Si le fichier est trop petit, le supprimer
        if size_mb < 300:  # Le modèle devrait faire ~375 MB
            print("⚠️  Fichier incomplet détecté, suppression...")
            filepath.unlink()
        else:
            print("✅ Le fichier semble complet!")
            return True
    
    print(f"\n📥 Téléchargement de {filename}...")
    print(f"📍 URL: {url}")
    print("⏳ Cela peut prendre 5-10 minutes selon votre connexion...\n")
    
    try:
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            
            # Barre de progression simple
            bar_length = 40
            filled = int(bar_length * downloaded / total_size)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"\r[{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, filename, reporthook=show_progress)
        print("\n\n✅ Téléchargement terminé avec succès!")
        
        # Vérifier la taille finale
        final_size = filepath.stat().st_size / (1024 * 1024)
        print(f"📊 Taille finale: {final_size:.2f} MB")
        
        if final_size < 300:
            print("⚠️  ATTENTION: Le fichier semble encore incomplet!")
            print("   Réessayez le téléchargement.")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n\n❌ Erreur lors du téléchargement: {e}")
        print("\n💡 Solutions possibles:")
        print("   1. Vérifiez votre connexion internet")
        print("   2. Réessayez plus tard")
        print("   3. Téléchargez manuellement depuis:")
        print("      https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth")
        return False

if __name__ == "__main__":
    url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    filename = "sam_vit_b_01ec64.pth"
    
    print("=" * 60)
    print("🚀 TÉLÉCHARGEMENT DU MODÈLE SAM")
    print("=" * 60)
    print()
    
    success = download_file(url, filename)
    
    if success:
        print("\n✅ Le modèle SAM est prêt!")
        print("   Vous pouvez maintenant redémarrer le backend.")
    else:
        print("\n❌ Le téléchargement a échoué.")
        print("   Le backend fonctionnera sans SAM (segmentation désactivée).")

