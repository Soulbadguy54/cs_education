def custom_key_builder(func, namespace: str, request, response, *args, **kwargs):
    # Используем только filter_query для формирования ключа
    return f"{namespace}:{kwargs['kwargs']['map_name'].value}"
