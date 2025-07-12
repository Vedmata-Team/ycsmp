# Registration Approval System Setup

## Overview
The system now filters registrations based on user assignments:
- **Non-MP States**: Users see registrations only from their assigned state
- **MP State**: Users see registrations only from their assigned districts

## Setup Instructions

### 1. Run Migration
```bash
python manage.py migrate
```

### 2. Create Approval Users
In Django Admin, go to "अप्रूवल यूजर" (Approval Users) section:

#### For Non-MP States:
1. Select the user
2. Choose the state code (e.g., 'UP', 'RJ', etc.)
3. Check "राज्य अप्रूवर" (State Approver)
4. Save

#### For MP State (District-wise):
1. Select the user
2. Choose state code 'MP'
3. Check "जिला अप्रूवर" (District Approver)
4. Select the districts this user should handle
5. Save

### 3. User Permissions
- **Superusers**: Can see all registrations
- **Approval Users**: See only registrations from their assigned state/districts
- **Regular Users**: See no registrations (unless they're approval users)

## How It Works

### Registration Filtering
- When a user logs into admin, the system checks their `ApprovalUser` profile
- For MP users: Shows registrations where `city` matches assigned districts
- For other states: Shows registrations where `state` matches assigned state
- Superusers see everything

### State Code Matching
- System uses CSV files in `static/csv/states.csv` to match state names to codes
- Registration's state field is matched against CSV data to get state code
- This code is then compared with user's assigned state code

## Example Scenarios

### Scenario 1: UP State Approver
- User assigned to state code 'UP'
- Will see all registrations where state = "Uttar Pradesh" (or UP variations)

### Scenario 2: MP District Approver
- User assigned to MP with districts ['Bhopal', 'Indore']
- Will see registrations where city = 'Bhopal' OR city = 'Indore'

### Scenario 3: Superuser
- Sees all registrations regardless of state/district

## Troubleshooting

### User sees no registrations
1. Check if user has `ApprovalUser` profile created
2. Verify state code matches CSV data
3. For MP users, ensure districts are properly assigned
4. Check if registrations exist for the assigned area

### State matching issues
1. Verify `static/csv/states.csv` has correct state names
2. Check for spelling variations in registration data
3. Ensure state codes are consistent