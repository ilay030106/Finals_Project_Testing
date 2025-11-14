"""Menu definitions using the Menu builder system"""
from menus import Menu

# Main menu - labels are used directly as callback_data
MAIN_MENU = Menu("Welcome To The Control Center!\n\nPlease Choose your Action") \
    .add_row(["Monitoring And Status", "Training Control"]) \
    .add_row(["Reporting And Visualization", "Settings"])

# Validate menu on load
MAIN_MENU.validate()

# Legacy dictionary format for backward compatibility
MAIN_MENU_DICT = MAIN_MENU.to_dict()
