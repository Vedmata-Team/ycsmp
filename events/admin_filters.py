from django.contrib.admin import SimpleListFilter
from django.db import models

class CountedSimpleListFilter(SimpleListFilter):
    """Custom filter that shows counts for all options including 'All'"""
    
    def choices(self, changelist):
        """Override to add counts to all choices including 'All'"""
        # Get the original choices
        choices = list(super().choices(changelist))
        
        # Calculate total count for 'All' option
        if choices:
            total_count = sum(choice.get('query_string', '').count('=') for choice in choices[1:])
            if not total_count:
                # If no query strings, count all objects
                total_count = changelist.queryset.count()
            
            # Update the 'All' choice to include count
            choices[0]['display'] = f"All ({total_count})"
        
        return choices