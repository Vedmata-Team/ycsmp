#!/usr/bin/env python
"""
Add database constraints and indexes to prevent future registration number issues
"""
import os
import sys
import django
from django.db import connection

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def add_database_constraints():
    """Add database-level constraints and indexes"""
    print("Adding database constraints and indexes...")
    
    with connection.cursor() as cursor:
        try:
            # Check if unique constraint already exists
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'events_eventregistration' 
                AND constraint_type = 'UNIQUE' 
                AND constraint_name LIKE '%registration_number%'
            """)
            
            existing_constraints = cursor.fetchall()
            
            if existing_constraints:
                print(f"Found existing constraints: {existing_constraints}")
                # Drop existing constraint if it exists
                for constraint in existing_constraints:
                    constraint_name = constraint[0]
                    print(f"Dropping existing constraint: {constraint_name}")
                    cursor.execute(f"ALTER TABLE events_eventregistration DROP CONSTRAINT IF EXISTS {constraint_name}")
            
            # Add unique constraint with proper handling of NULL values
            print("Adding unique constraint for registration_number...")
            cursor.execute("""
                ALTER TABLE events_eventregistration 
                ADD CONSTRAINT events_eventregistration_registration_number_unique 
                UNIQUE (registration_number)
            """)
            print("✓ Unique constraint added successfully")
            
            # Add partial index for better performance on approved registrations
            print("Adding performance indexes...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_eventregistration_approved_with_number 
                ON events_eventregistration (approval_status, registration_number) 
                WHERE approval_status = 'approved' AND registration_number IS NOT NULL
            """)
            print("✓ Performance index added")
            
            # Add index for registration type and city combination
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_eventregistration_type_city 
                ON events_eventregistration (registration_type, city, approval_status)
            """)
            print("✓ Type-city index added")
            
            # Add index for phone number lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_eventregistration_phone 
                ON events_eventregistration (phone)
            """)
            print("✓ Phone index added")
            
        except Exception as e:
            print(f"Error adding constraints: {e}")
            return False
    
    return True

def verify_constraints():
    """Verify that constraints are properly added"""
    print("\nVerifying database constraints...")
    
    with connection.cursor() as cursor:
        # Check unique constraint
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'events_eventregistration' 
            AND constraint_type = 'UNIQUE'
        """)
        
        constraints = cursor.fetchall()
        print(f"Unique constraints: {constraints}")
        
        # Check indexes
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'events_eventregistration'
            AND indexname LIKE 'idx_%'
        """)
        
        indexes = cursor.fetchall()
        print(f"Custom indexes: {len(indexes)}")
        for index in indexes:
            print(f"  - {index[0]}")
    
    return True

if __name__ == "__main__":
    print("Setting up database constraints for registration numbers...")
    
    if add_database_constraints():
        print("✅ Database constraints added successfully")
        verify_constraints()
    else:
        print("❌ Failed to add database constraints")
    
    print("\nDone!")