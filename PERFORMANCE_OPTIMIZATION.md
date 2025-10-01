# YCSMP Performance Optimization Guide

## Overview
This guide provides comprehensive performance optimizations for the YCSMP registration system while preserving all existing features including multi-level approval, document uploads, and export functionality.

## Quick Start

### 1. Run Database Optimization
```bash
python create_indexes.py
```

### 2. Warm Up Caches
```bash
python cache_warmer.py
```

### 3. Monitor Performance
```bash
python monitor_performance.py
```

## Performance Improvements Implemented

### Database Optimizations

#### 1. Indexes Created
- **Approval Status Index**: Fast filtering by approval status
- **State-City Composite Index**: Optimized location-based queries
- **Registration Type Index**: Quick filtering by registration type
- **Date Indexes**: Efficient date-based ordering and filtering
- **Search Indexes**: Fast name, email, and phone searches
- **Composite Indexes**: Multi-column filtering optimization

#### 2. Query Optimizations
- **select_related()**: Reduces database queries for foreign keys
- **Optimized Filtering**: Streamlined approval user filtering logic
- **Cached Lookups**: Upzone and approval user caching

### Admin Interface Optimizations

#### 1. Pagination Settings
```python
list_per_page = 50              # Reduced from default 100
list_max_show_all = 200         # Prevents large result sets
show_full_result_count = False  # Avoids expensive COUNT queries
preserve_filters = True         # Maintains filter state
```

#### 2. Query Optimization
- Foreign key relationships pre-loaded with `select_related()`
- Removed debug print statements
- Optimized approval user filtering logic

### Caching Strategy

#### 1. Upzone Caching
- District-to-upzone mappings cached for 1 hour
- Reduces repeated database queries for upzone lookups

#### 2. Approval User Caching
- User permission data cached for 1 hour
- Faster permission checking in admin interface

#### 3. Options Caching
- Responsibility and Vibhag options cached
- Reduces form loading time

### Settings Optimizations

#### 1. Database Connection Pooling
```python
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {'MAX_CONNS': 20}
```

#### 2. Session Optimization
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

#### 3. Cache Configuration
```python
CACHE_TIMEOUT = 300  # 5 minutes default
```

## Performance Scripts

### 1. create_indexes.py
Creates optimized database indexes for faster queries.

**Usage:**
```bash
python create_indexes.py
```

**Features:**
- Creates 15+ performance indexes
- Analyzes table statistics
- Runs VACUUM ANALYZE for better query planning

### 2. cache_warmer.py
Preloads frequently accessed data into cache.

**Usage:**
```bash
python cache_warmer.py
```

**Caches:**
- Upzone-district mappings
- Approval user permissions
- Responsibility/Vibhag options
- Registration counts
- State-district mappings

### 3. monitor_performance.py
Monitors query performance and provides recommendations.

**Usage:**
```bash
python monitor_performance.py
```

**Monitors:**
- Query execution times
- Cache performance
- Database statistics
- Slow query detection

## Maintenance Schedule

### Daily
- Monitor admin performance
- Check for slow queries

### Weekly
- Run `python cache_warmer.py`
- Monitor `python monitor_performance.py`

### Monthly
- Run `python create_indexes.py` (for new data)
- Review performance metrics
- Optimize based on usage patterns

## Performance Targets

### Query Performance Targets
- Registration count queries: < 100ms
- Pending registrations: < 50ms
- Recent registrations (100 records): < 200ms
- Approval user lookups: < 50ms
- Upzone queries: < 20ms

### Admin Interface Targets
- Page load time: < 2 seconds
- Filter application: < 1 second
- Search results: < 1 second

## Features Preserved

### ✅ All Registration Features Maintained
- Multi-level approval workflow (District → UpZone → State)
- Document upload system for participants
- Registration type permissions
- Bulk user creation and management
- Export system with async processing
- Email notifications
- Campaign and Vibhag selections

### ✅ All Admin Features Maintained
- Permission-based filtering
- Approval buttons and workflow
- Export functionality (CSV, Excel, PDF)
- Search and filtering
- Bulk actions
- Document viewing

### ✅ All User Management Features Maintained
- District, UpZone, and State level approvers
- Registration type restrictions
- MP Central Zone configuration
- Bulk user creation scripts

## Troubleshooting

### Slow Admin Pages
1. Run `python monitor_performance.py`
2. Check if indexes exist: `python create_indexes.py`
3. Warm up caches: `python cache_warmer.py`
4. Reduce `list_per_page` in admin settings

### High Database Load
1. Check for missing indexes
2. Review slow query log
3. Consider connection pooling
4. Optimize complex filters

### Cache Issues
1. Verify Redis/cache backend is running
2. Check cache timeout settings
3. Clear and warm cache: `python cache_warmer.py`

## Advanced Optimizations

### For High Traffic
1. **Database Read Replicas**: Separate read/write databases
2. **CDN**: Static file delivery optimization
3. **Load Balancing**: Multiple application servers
4. **Database Partitioning**: Split large tables by date/region

### For Large Datasets
1. **Archiving**: Move old registrations to archive tables
2. **Pagination**: Implement cursor-based pagination
3. **Background Processing**: Move heavy operations to Celery
4. **Database Sharding**: Split data across multiple databases

## Monitoring and Alerts

### Key Metrics to Monitor
- Average query response time
- Database connection count
- Cache hit ratio
- Admin page load times
- Export processing times

### Recommended Tools
- **PostgreSQL**: pg_stat_statements for query analysis
- **Django Debug Toolbar**: Development query analysis
- **New Relic/DataDog**: Production monitoring
- **Grafana**: Custom dashboards

## Support

For performance issues or questions:
1. Run `python monitor_performance.py` for diagnostics
2. Check the troubleshooting section above
3. Review database logs for errors
4. Consider the advanced optimizations for scaling

---

**Last Updated**: October 2024
**Version**: 1.0
**Compatibility**: Django 5.2+, PostgreSQL 12+