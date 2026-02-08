/**
 * Barrel Vault Pattern Configuration
 */

export interface BarrelVaultConfig {
  colors: {
    mountain_fold_color: string;
    valley_fold_color: string;
    connecting_color: string;
  };
  line_widths: {
    fold_width: number;
    connecting_width: number;
  };
  line_styles: {
    connecting_line_style: string;
  };
  general: {
    rounding_decimal: number;
  };
}

/**
 * Default configuration for barrel vault pattern
 */
export const barrelVaultConfig: BarrelVaultConfig = {
  colors: {
    mountain_fold_color: "rgb(255,0,0)", // red
    valley_fold_color: "rgb(0,0,255)",   // blue
    connecting_color: "black"
  },
  line_widths: {
    fold_width: 1.5,
    connecting_width: 1.5
  },
  line_styles: {
    connecting_line_style: "solid" // Options: "solid", "dash", "dot", "dashdot"
  },
  general: {
    rounding_decimal: 4
  }
};
