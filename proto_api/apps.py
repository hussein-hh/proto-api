from django.apps import AppConfig


class ProtoApiConfig(AppConfig):
    name = 'proto_api'
    verbose_name = 'Proto API'
    
    def ready(self):
        """
        Apply patches when Django is ready.
        This is called by Django during startup after all apps are loaded.
        """
        # Import and apply patches
        try:
            from .explorer_patches import apply_explorer_patches
            apply_explorer_patches()
        except Exception as e:
            # Log the error but continue startup
            import logging
            logging.getLogger(__name__).warning(f"Failed to apply explorer patches: {e}")
            pass 