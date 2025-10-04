# Registration Number Duplicate Fix - Solution Guide

यह guide आपको registration number duplicate error को ठीक करने के लिए step-by-step process बताती है।

## समस्या का विवरण

Error: `duplicate key value violates unique constraint "events_eventregistration_registration_number_key"`

यह error तब आती है जब:
1. Same registration number multiple registrations को assign हो जाता है
2. Database में unique constraint violation होती है
3. Registration approval के दौरान race condition होती है

## समाधान Steps

### Step 1: Current State Analysis
पहले current state को analyze करें:

```bash
python verify_registration_integrity.py
```

यह script बताएगी:
- कितने duplicate registration numbers हैं
- कौन से approved registrations में registration number नहीं है
- Format consistency issues
- Overall health report

### Step 2: Fix Existing Issues
सभी existing issues को fix करें:

```bash
python comprehensive_registration_fix.py
```

यह script:
- सभी duplicate registration numbers को fix करेगी
- Approved registrations को missing registration numbers देगी
- सभी तीन registration types को handle करेगी:
  - Participant (YCS-XX-XXX-0001)
  - Volunteer (YCSV-XX-XXX-0001)  
  - Organization Representative (YCSO-XX-XXX-0001)

### Step 3: Add Database Constraints
Future issues को prevent करने के लिए database constraints add करें:

```bash
python add_registration_constraints.py
```

यह script:
- Unique constraint add करेगी
- Performance indexes add करेगी
- Database integrity ensure करेगी

### Step 4: Final Verification
सब कुछ ठीक है या नहीं verify करें:

```bash
python verify_registration_integrity.py
```

## Code Changes Made

### 1. Model Improvements (`events/models.py`)

#### Enhanced `generate_registration_number()` method:
- Added proper database locking with `select_for_update()`
- Added retry logic for race conditions
- Added timestamp-based fallback for unique number generation
- Better error handling

#### Enhanced `save()` method:
- Added retry logic for IntegrityError
- Better handling of duplicate registration number errors
- Automatic regeneration on constraint violations

### 2. Database Constraints

#### Added constraints:
- Unique constraint on `registration_number` field
- Performance indexes for faster queries
- Partial indexes for approved registrations

## Registration Number Format

### Format Pattern:
```
{PREFIX}-{STATE_CODE}-{CITY_PREFIX}-{SERIAL_NUMBER}
```

### Prefixes by Type:
- **Participant**: `YCS-MP-BHO-0001`
- **Volunteer**: `YCSV-MP-BHO-0001`
- **Organization Representative**: `YCSO-MP-BHO-0001`

### Components:
- **PREFIX**: Registration type identifier
- **STATE_CODE**: 2-letter state code (MP, UP, RJ, etc.)
- **CITY_PREFIX**: First 3 letters of city name (uppercase)
- **SERIAL_NUMBER**: 4-digit sequential number

## Prevention Measures

### 1. Database Level:
- Unique constraint on registration_number
- Proper indexing for performance
- Transaction isolation

### 2. Application Level:
- Retry logic for race conditions
- Proper error handling
- Atomic transactions

### 3. Monitoring:
- Regular integrity checks
- Health monitoring scripts
- Error logging

## Troubleshooting

### If duplicate error still occurs:

1. **Check database constraints**:
   ```sql
   SELECT constraint_name FROM information_schema.table_constraints 
   WHERE table_name = 'events_eventregistration' AND constraint_type = 'UNIQUE';
   ```

2. **Manual fix for specific registration**:
   ```python
   from events.models import EventRegistration
   reg = EventRegistration.objects.get(id=REGISTRATION_ID)
   reg.registration_number = None
   reg.save()  # This will regenerate the number
   ```

3. **Check for race conditions**:
   - Multiple simultaneous approvals
   - High traffic during approval process
   - Database connection issues

### Common Issues:

1. **Migration not applied**: Run `python manage.py migrate`
2. **Database constraints missing**: Run `python add_registration_constraints.py`
3. **Old duplicates remain**: Run `python comprehensive_registration_fix.py`

## Monitoring Commands

### Daily Health Check:
```bash
python verify_registration_integrity.py
```

### Check for new duplicates:
```bash
python -c "
from events.models import EventRegistration
from django.db.models import Count
duplicates = EventRegistration.objects.values('registration_number').annotate(count=Count('id')).filter(count__gt=1)
print(f'Duplicates found: {duplicates.count()}')
"
```

### Performance monitoring:
```bash
python -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) FROM events_eventregistration WHERE registration_number IS NOT NULL')
    print(f'Total with reg numbers: {cursor.fetchone()[0]}')
"
```

## Files Created/Modified

### New Scripts:
- `comprehensive_registration_fix.py` - Main fix script
- `add_registration_constraints.py` - Database constraints
- `verify_registration_integrity.py` - Verification script
- `fix_duplicate_registration_numbers.py` - Simple duplicate fix
- `create_registration_uniqueness_migration.py` - Migration creator

### Modified Files:
- `events/models.py` - Enhanced registration number generation

## Success Criteria

✅ **All checks should pass:**
- No duplicate registration numbers
- All approved registrations have registration numbers
- Correct format for all registration numbers
- Database constraints in place
- Performance indexes active

## Support

अगर कोई issue आती है तो:
1. Error logs check करें
2. Database connectivity verify करें  
3. Migration status check करें: `python manage.py showmigrations`
4. Scripts को step by step run करें

---

**Note**: सभी scripts को production environment में run करने से पहले backup ले लें।