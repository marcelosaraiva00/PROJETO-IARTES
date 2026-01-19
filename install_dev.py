"""
Script de instalação em modo desenvolvimento
"""
import subprocess
import sys

def main():
    """Instala o pacote em modo editável"""
    print("=" * 70)
    print("INSTALAÇÃO DO IARTES EM MODO DESENVOLVIMENTO")
    print("=" * 70)
    print()
    
    print("📦 Instalando pacote em modo editável...")
    try:
        # Instalar em modo editável (-e flag)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Instalação concluída com sucesso!")
        print()
        print("Agora você pode importar de qualquer lugar:")
        print("  from src.models.test_case import TestCase")
        print()
        print("Execute o teste:")
        print("  python test_install.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
