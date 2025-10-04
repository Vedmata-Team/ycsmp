#!/usr/bin/env python
"""
Create a migration to ensure registration_number uniqueness
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ycs_mp.settings')
django.setup()

def create_migration():
    """Create migration for registration number uniqueness"""
    print("Creating migration for registration number uniqueness...")
    
    migration_content = '''# Generated migration for registration number uniqueness
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_add_approval_tracking'),
    ]

    operations = [
        # First, ensure all registration numbers are unique
        migrations.RunSQL(
            """
            -- Fix any existing duplicate registration numbers
            UPDATE events_eventregistration 
            SET registration_number = CONCAT(
                CASE 
                    WHEN registration_type = 'volunteer' THEN 'YCSV'
                    WHEN registration_type = 'organization_representative' THEN 'YCSO'
                    ELSE 'YCS'
                END,
                '-',
                COALESCE(
                    (SELECT state_code FROM (
                        SELECT 'MP' as state_code WHERE state = 'Madhya Pradesh'
                        UNION SELECT 'UP' as state_code WHERE state = 'Uttar Pradesh'
                        UNION SELECT 'RJ' as state_code WHERE state = 'Rajasthan'
                        UNION SELECT 'GJ' as state_code WHERE state = 'Gujarat'
                        UNION SELECT 'MH' as state_code WHERE state = 'Maharashtra'
                        UNION SELECT 'XX' as state_code
                    ) s LIMIT 1), 'XX'
                ),
                '-',
                UPPER(SUBSTRING(COALESCE(city, 'XXX'), 1, 3)),
                '-',
                LPAD(CAST(EXTRACT(EPOCH FROM NOW()) * 1000 AS BIGINT) % 100000 + id AS TEXT, 5, '0')
            )
            WHERE registration_number IN (
                SELECT registration_number 
                FROM events_eventregistration 
                WHERE registration_number IS NOT NULL
                GROUP BY registration_number 
                HAVING COUNT(*) > 1
            )
            AND id NOT IN (
                SELECT MIN(id) 
                FROM events_eventregistration 
                WHERE registration_number IS NOT NULL
                GROUP BY registration_number
            );
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Add database-level unique constraint if not exists
        migrations.RunSQL(
            """
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'events_eventregistration_registration_number_key'
                ) THEN
                    ALTER TABLE events_eventregistration 
                    ADD CONSTRAINT events_eventregistration_registration_number_key 
                    UNIQUE (registration_number);
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE events_eventregistration DROP CONSTRAINT IF EXISTS events_eventregistration_registration_number_key;"
        ),
    ]
'''
    
    # Write migration file
    migration_file = 'e:\\Divy\\Projects\\GitHub\\ycsmp\\events\\migrations\\0018_fix_registration_number_uniqueness.py'
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print(f"Migration created: {migration_file}")
    print("Run 'python manage.py migrate' to apply the migration")

if __name__ == "__main__":
    create_migration()