class AppContext:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
            cls._instance._callback_registry = {}
        return cls._instance
    
    def __getitem__(self, key):
        return self._data.get(key)
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def clear(self):
        self._data.clear()
    
    def register_callback(self, callback_data, method):
        """Register a callback handler method for a specific callback_data string"""
        self._callback_registry[callback_data] = method
    
    def get_callback_handler(self, callback_data):
        """Get the handler method for a specific callback_data string"""
        return self._callback_registry.get(callback_data)
    
    def get_all_callbacks(self):
        """Get all registered callback handlers"""
        return self._callback_registry.copy()

# Global instance
app_context = AppContext()
