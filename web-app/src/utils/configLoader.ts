/**
 * Configuration loader for JSON config files
 */

export interface PseudoDomeConfig {
  colors: {
    fold_color_1: string;
    fold_color_2: string;
    radial_color: string;
  };
  line_widths: {
    fold_width: number;
    radial_width: number;
  };
  line_styles: {
    radial_line_style: 'solid' | 'dash' | 'dot' | 'dashdot';
  };
  general: {
    rounding_decimal: number;
  };
}

export interface BarrelVaultConfig {
  colors: {
    fold_color_1: string;
    fold_color_2: string;
    connecting_color: string;
  };
  line_widths: {
    fold_width: number;
    connecting_width: number;
  };
  line_styles: {
    connecting_line_style: 'solid' | 'dash' | 'dot' | 'dashdot';
  };
  general: {
    rounding_decimal: number;
  };
}

export interface DoubleBarrelVaultConfig {
  colors: {
    fold_color_1: string;
    fold_color_2: string;
    connecting_color: string;
  };
  line_widths: {
    fold_width: number;
    connecting_width: number;
  };
  line_styles: {
    connecting_line_style: 'solid' | 'dash' | 'dot' | 'dashdot';
  };
  general: {
    rounding_decimal: number;
  };
}

// Default configurations (fallback if fetch fails)
export const pseudoDomeDefaults: PseudoDomeConfig = {
  colors: {
    fold_color_1: "rgb(0,255,0)",
    fold_color_2: "rgb(255,0,0)",
    radial_color: "rgb(0,0,255)"
  },
  line_widths: {
    fold_width: 1.5,
    radial_width: 1.5
  },
  line_styles: {
    radial_line_style: "solid"
  },
  general: {
    rounding_decimal: 4
  }
};

export const barrelVaultDefaults: BarrelVaultConfig = {
  colors: {
    fold_color_1: "rgb(255,0,0)",
    fold_color_2: "rgb(0,0,255)",
    connecting_color: "black"
  },
  line_widths: {
    fold_width: 1.5,
    connecting_width: 1.5
  },
  line_styles: {
    connecting_line_style: "solid"
  },
  general: {
    rounding_decimal: 4
  }
};

export const doubleBarrelVaultDefaults: DoubleBarrelVaultConfig = {
  colors: {
    fold_color_1: "rgb(255,0,0)",
    fold_color_2: "rgb(0,0,255)",
    connecting_color: "black"
  },
  line_widths: {
    fold_width: 1.5,
    connecting_width: 1.5
  },
  line_styles: {
    connecting_line_style: "solid"
  },
  general: {
    rounding_decimal: 4
  }
};

// Cache for loaded configs
let pseudoDomeConfigCache: PseudoDomeConfig | null = null;
let barrelVaultConfigCache: BarrelVaultConfig | null = null;
let doubleBarrelVaultConfigCache: DoubleBarrelVaultConfig | null = null;

/**
 * Fetch and parse JSON config file
 */
async function fetchConfig<T>(path: string, defaults: T): Promise<T> {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      console.warn(`Failed to load config from ${path}, using defaults`);
      return defaults;
    }
    const config = await response.json();
    return { ...defaults, ...config };
  } catch (error) {
    console.warn(`Error loading config from ${path}, using defaults:`, error);
    return defaults;
  }
}

/**
 * Get pseudo-dome configuration
 */
export async function getPseudoDomeConfig(): Promise<PseudoDomeConfig> {
  if (!pseudoDomeConfigCache) {
    pseudoDomeConfigCache = await fetchConfig('/config/pseudo_dome_config.json', pseudoDomeDefaults);
  }
  return pseudoDomeConfigCache;
}

/**
 * Get barrel vault configuration
 */
export async function getBarrelVaultConfig(): Promise<BarrelVaultConfig> {
  if (!barrelVaultConfigCache) {
    barrelVaultConfigCache = await fetchConfig('/config/barrel_vault_config.json', barrelVaultDefaults);
  }
  return barrelVaultConfigCache;
}

/**
 * Get double barrel vault configuration
 */
export async function getDoubleBarrelVaultConfig(): Promise<DoubleBarrelVaultConfig> {
  if (!doubleBarrelVaultConfigCache) {
    doubleBarrelVaultConfigCache = await fetchConfig('/config/double_barrel_vault_config.json', doubleBarrelVaultDefaults);
  }
  return doubleBarrelVaultConfigCache;
}

/**
 * Clear config cache (useful for testing or reloading)
 */
export function clearConfigCache(): void {
  pseudoDomeConfigCache = null;
  barrelVaultConfigCache = null;
  doubleBarrelVaultConfigCache = null;
}
