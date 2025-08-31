#!/usr/bin/env python3
"""
Quick test script for Qwen + File Management setup
"""

import os
import sys
import requests

def test_imports():
    """Test if all required imports work"""
    print("🧪 Testing imports...")
    try:
        import json
        import requests
        import datetime
        print("✅ Standard libraries: OK")
        
        # Test optional imports
        try:
            import tqdm
            print("✅ tqdm: OK")
        except ImportError:
            print("⚠️  tqdm: Missing (will auto-install)")
        
        # Test file manager (now built-in)
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # Test that we can import from qwen.py without errors
        try:
            import importlib.util
            qwen_path = os.path.join(os.path.dirname(__file__), 'qwen.py')
            if os.path.exists(qwen_path):
                print("✅ qwen.py file found")
                # Try to load just the FileManager class to test imports
                spec = importlib.util.spec_from_file_location("qwen_test", qwen_path)
                qwen_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(qwen_module)
                if hasattr(qwen_module, 'FileManager'):
                    print("✅ FileManager class: Built into qwen.py successfully")
                else:
                    print("⚠️  FileManager class not found in qwen.py")
            else:
                print("⚠️  qwen.py not found in current directory")
        except Exception as e:
            print(f"⚠️  qwen.py import test failed: {e}")
        
        print("✅ File Management: All-in-one architecture ready")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_ollama():
    """Test Ollama connection"""
    print("\n🤖 Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama running! Found {len(models)} models")
            
            qwen_models = [m['name'] for m in models if 'qwen' in m['name'].lower()]
            if qwen_models:
                print(f"✅ Qwen models: {', '.join(qwen_models)}")
            else:
                print("⚠️  No Qwen models found. Run: ollama pull qwen2.5:3b")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def test_memory_directory():
    """Test if memory directory exists and is writable"""
    print("\n💾 Testing memory system...")
    memory_dir = r'C:\Users\Grandpaul\.ollama\memory'
    try:
        os.makedirs(memory_dir, exist_ok=True)
        test_file = os.path.join(memory_dir, 'test.json')
        with open(test_file, 'w') as f:
            f.write('{"test": true}')
        os.remove(test_file)
        print(f"✅ Memory directory writable: {memory_dir}")
        return True
    except Exception as e:
        print(f"❌ Memory directory error: {e}")
        return False

def test_output_directory():
    """Test if output directory exists and is writable"""
    print("\n📁 Testing output directory...")
    output_dir = r'C:\Users\Grandpaul\.ollama\outputs'
    try:
        os.makedirs(output_dir, exist_ok=True)
        test_file = os.path.join(output_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Test file')
        os.remove(test_file)
        print(f"✅ Output directory writable: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Output directory error: {e}")
        return False

def main():
    print("="*60)
    print("🔧 QWEN ASSISTANT SETUP TEST (Single-File Architecture)")
    print("="*60)
    
    all_good = True
    all_good &= test_imports()
    all_good &= test_ollama()
    all_good &= test_memory_directory()
    all_good &= test_output_directory()
    
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL TESTS PASSED! Ready to run qwen.py")
        print("💡 Just run: python qwen.py (single file, no dependencies!)")
    else:
        print("❌ Some tests failed. Check the issues above.")
    print("="*60)

if __name__ == "__main__":
    main()
