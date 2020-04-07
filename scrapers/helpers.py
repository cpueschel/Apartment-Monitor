def clean(items):
    cleaner = lambda x: x.strip() if isinstance(x, str) else x
    if isinstance(items, str):
        return cleaner(items)
    elif isinstance(items, list):
        return [clean(item) for item in items]
    elif isinstance(items, dict):
        return {key: clean(items[key]) for key in items.keys()}
    else:
        return items
