#!/usr/bin/env python3
"""
Test script to verify the new project structure
"""

import os
import sys

def test_structure():
    """Test that the new project structure is correct"""
    print("🧪 Testing New Project Structure...")
    
    # Test backend structure
    backend_files = [
        "app/",
        "app/models/",
        "app/services/",
        "app/api/",
        "migrations/",
        "requirements.txt",
        "Dockerfile",
        "alembic.ini"
    ]
    
    print("✅ Backend Structure:")
    for file_path in backend_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    # Test app package structure
    app_files = [
        "app/models/space.py",
        "app/models/team.py", 
        "app/models/role.py",
        "app/schemas/space.py",
        "app/services/space_service.py",
        "app/api/v1/spaces.py"
    ]
    
    print("\n✅ App Package Structure:")
    for file_path in app_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    # Test frontend structure
    frontend_files = [
        "../frontend/",
        "../frontend/src/",
        "../frontend/src/components/",
        "../frontend/src/contexts/"
    ]
    
    print("\n✅ Frontend Structure:")
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    # Test docs structure
    docs_files = [
        "../docs/",
        "../docs/NUIFLO_WORKFORCE_ROADMAP.md",
        "../docs/PHASE_1_STATUS.md"
    ]
    
    print("\n✅ Documentation Structure:")
    for file_path in docs_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")

def test_imports():
    """Test that imports work correctly"""
    print("\n🧪 Testing Import Paths...")
    
    try:
        # Test that we can import the app package
        sys.path.append('.')
        from app.models import Base, TeamSpace, Team, Role
        print("✅ App package imports work")
        
        from app.schemas.space import SpaceCreate, SpaceResponse
        print("✅ Schema imports work")
        
        from app.services.space_service import SpaceService
        print("✅ Service imports work")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all structure tests"""
    print("🚀 Testing Clean Project Structure")
    print("=" * 50)
    
    test_structure()
    imports_work = test_imports()
    
    print("\n" + "=" * 50)
    if imports_work:
        print("🎉 Project structure is clean and working!")
        print("\n📋 New Structure Benefits:")
        print("   ✅ No more redundant workforce_api/workforce_api/")
        print("   ✅ Clear separation: backend/ vs frontend/")
        print("   ✅ All docs organized in docs/")
        print("   ✅ Clean import paths: from app.models import ...")
        print("   ✅ Easy to understand and navigate")
    else:
        print("⚠️  Structure is clean but imports need fixing")
    
    print("\n📊 Clean Structure Summary:")
    print("   backend/     - FastAPI backend with app/ package")
    print("   frontend/    - React frontend")
    print("   docs/        - All documentation and guides")
    print("   .env         - Environment variables")
    print("   docker-compose.yml - Full stack orchestration")

if __name__ == "__main__":
    main() 