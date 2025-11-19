from django import template

register = template.Library()

@register.filter
def custom_replace(value, arg):
    """
    Replaces all occurrences of the first argument 
    in the value string with the second argument.
    Usage: {{ value|custom_replace:"old_string|new_string" }}
    """
    if '|' not in arg:
        # Simple replace: replaces arg with a single space.
        # This covers your case: key|custom_replace:"_"
        return value.replace(arg, ' ')
    
    # Complex replace: handles "old_str|new_str"
    try:
        old, new = arg.split('|')
        return value.replace(old, new)
    except ValueError:
        # Handle cases where the argument isn't formatted correctly
        return value