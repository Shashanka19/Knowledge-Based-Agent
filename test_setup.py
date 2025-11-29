"""
Simple test script for KnowledgeBase Agent components
Run this to verify that all components are working correctly
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test component imports
        from components.vector_store import get_vector_store, VectorStoreFactory
        from components.model_loader import get_model, ModelFactory
        from components.ingest import create_document_processor
        from components.query import create_query_engine
        from components.firebase_db import get_metadata_db
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment configuration...")
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "PINECONE_API_KEY"]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False
    
    print("✅ Required environment variables found!")
    
    # Check optional variables
    found_optional = []
    for var in optional_vars:
        if os.getenv(var):
            found_optional.append(var)
    
    if found_optional:
        print(f"✅ Optional variables found: {found_optional}")
    
    return True

def test_components():
    """Test component initialization"""
    print("\n🧪 Testing component initialization...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Test metadata database
        print("  Testing metadata database...")
        from components.firebase_db import get_metadata_db
        metadata_db = get_metadata_db()
        print("  ✅ Metadata database initialized")
        
        # Test vector store
        print("  Testing vector store...")
        from components.vector_store import get_vector_store
        vector_store = get_vector_store()
        print("  ✅ Vector store initialized")
        
        # Test model loader
        print("  Testing model loader...")
        from components.model_loader import get_model
        model = get_model()
        print(f"  ✅ Model initialized: {model.get_model_name()}")
        
        # Test document processor
        print("  Testing document processor...")
        from components.ingest import create_document_processor
        doc_processor = create_document_processor()
        print("  ✅ Document processor initialized")
        
        # Test query engine
        print("  Testing query engine...")
        from components.query import create_query_engine
        query_engine = create_query_engine()
        print("  ✅ Query engine initialized")
        
        print("✅ All components initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Component initialization error: {e}")
        traceback.print_exc()
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = ["data", "uploads", "src/components"]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        else:
            print(f"✅ Found directory: {dir_path}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🧠 KnowledgeBase Agent - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directories),
        ("Environment Configuration", test_environment),
        ("Module Imports", test_imports),
        ("Component Initialization", test_components)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🚀 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your KnowledgeBase Agent is ready to run.")
        print("Run 'streamlit run main.py' to start the application.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()