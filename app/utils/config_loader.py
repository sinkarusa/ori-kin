import os
import yaml
from pathlib import Path

def load_config(config_file):
    """
    Load a YAML configuration file
    
    Args:
        config_file (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading configuration file {config_file}: {str(e)}")
        # Return default configuration if file can't be loaded
        return {
            'colors': {
                'fold_color_1': 'red',
                'fold_color_2': 'red',
                'radial_color': 'blue'
            },
            'line_widths': {
                'fold_width': 3,
                'radial_width': 3
            },
            'line_styles': {
                'radial_line_style': 'solid'
            }
        }

def get_pseudo_dome_config():
    """
    Get the Pseudo-Dome pattern configuration
    
    Returns:
        dict: Pseudo-Dome configuration dictionary
    """
    # Get the absolute path to the config file
    base_dir = Path(__file__).parent.parent
    config_file = os.path.join(base_dir, 'config', 'pseudo_dome_config.yaml')
    return load_config(config_file)

def get_barrel_vault_config():
    """
    Get the Barrel Vault pattern configuration

    Returns:
        dict: Barrel Vault configuration dictionary
    """
    # Get the absolute path to the config file
    base_dir = Path(__file__).parent.parent
    config_file = os.path.join(base_dir, 'config', 'barrel_vault_config.yaml')
    return load_config(config_file)

def get_double_barrel_vault_config():
    """
    Get the Double Barrel Vault pattern configuration

    Returns:
        dict: Double Barrel Vault configuration dictionary
    """
    # Get the absolute path to the config file
    base_dir = Path(__file__).parent.parent
    config_file = os.path.join(base_dir, 'config', 'double_barrel_vault_config.yaml')
    return load_config(config_file)
