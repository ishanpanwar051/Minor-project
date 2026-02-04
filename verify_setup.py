from app_factory import create_app
import sys

try:
    print("Attempting to create app...")
    app = create_app('testing')
    print("App created successfully.")
    
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}")
        
    print("\nVerification successful!")
except Exception as e:
    print(f"\nVerification FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
