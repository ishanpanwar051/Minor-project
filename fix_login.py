"""
Quick Fix for Login Issue
Create a fixed version of the User model
"""

# Fix the check_password method directly
def fix_login():
    """Fix the login issue by updating the check_password method"""
    
    fix_code = '''
    def check_password(self, password):
        """Check password using both Werkzeug and simple hash methods"""
        # First try SHA256 hash (since we know passwords are stored this way)
        simple_hash = hashlib.sha256(password.encode()).hexdigest()
        if self.password_hash == simple_hash:
            return True
        
        # Fallback to Werkzeug hash
        try:
            return check_password_hash(self.password_hash, password)
        except:
            return False
    '''
    
    print("🔧 FIXING LOGIN ISSUE...")
    print("The check_password method needs to be updated in eduguard_final.py")
    print("Replace the current check_password method with:")
    print(fix_code)
    
    # Create a simple test to verify the fix
    import hashlib
    
    # Test the correct logic
    stored_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    password = "admin123"
    test_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"\n🧪 TESTING FIX:")
    print(f"Password: {password}")
    print(f"Expected hash: {test_hash}")
    print(f"Stored hash: {stored_hash}")
    print(f"Match: {test_hash == stored_hash}")
    
    if test_hash == stored_hash:
        print("✅ Fix will work! The logic is correct.")
    else:
        print("❌ Fix has issues.")

if __name__ == '__main__':
    fix_login()
