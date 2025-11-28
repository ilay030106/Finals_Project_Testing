import inspect
import re 


class CallbackRegistry:
    
    static_handlers = {}
    pattern_handlers = []

    @classmethod
    def register(cls,callback_data):
        def decorator(func):
            cls.static_handlers[callback_data] = func
            return func
        return decorator
    
    @classmethod
    def register_pattern(cls,pattern):

        compiled= re.compile(pattern)

        def decorator(func):
            cls.pattern_handlers.append((compiled,func))
            return func
        return decorator
    
    @classmethod
    def resolve(cls, callback_data: str):
        """
        Returns (handler, extracted_params)
        or (None, None) if no handler is found.
        """

        # 1) Try static handlers first
        if callback_data in cls.static_handlers:
            return cls.static_handlers[callback_data], ()

        # 2) Try dynamic pattern handlers
        for regex, func in cls.pattern_handlers:
            match = regex.fullmatch(callback_data)
            if match:
                return func, match.groups()  # Return params extracted

        return None, None
    
    @classmethod
    async def dispatch(cls, update, context, **dependencies):
        """
        Automatically finds and executes the correct callback handler.
        Injects dependencies into handlers.
        
        Args:
            update: Telegram update
            context: Telegram context
            **dependencies: Dependencies to inject (client, models, etc.)
        """
        callback_data = update.callback_query.data

        handler, params = cls.resolve(callback_data)

        if not handler:
            return False, None

        # Inject dependencies into handler
        if inspect.iscoroutinefunction(handler):
            result = await handler(update, context, *params, **dependencies)
        else:
            result = handler(update, context, *params, **dependencies)
        
        return True, result

