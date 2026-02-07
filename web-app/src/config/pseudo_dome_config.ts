/**
 * Pseudo-Dome Pattern Configuration
 */

export interface PseudoDomeConfig {
  colors: {
    cut_line_color: string;
    mountain_fold_color: string;
    valley_fold_color: string;
  };
  line_widths: {
    fold_width: number;
    radial_width: number;
  };
  line_styles: {
    radial_line_style: string;
  };
  general: {
    rounding_decimal: number;
  };
}

/**
 * Default configuration for pseudo dome pattern
 */
export const pseudoDomeConfig: PseudoDomeConfig = {
  colors: {
    cut_line_color: "rgb(0,255,0)",    // green
    mountain_fold_color: "rgb(255,0,0)", // red
    valley_fold_color: "rgb(0,0,255)"    // blue
  },
  line_widths: {
    fold_width: 1.5,
    radial_width: 1.5
  },
  line_styles: {
    radial_line_style: "solid" // Options: "solid", "dash", "dot", "dashdot"
  },
  general: {
    rounding_decimal: 4
  }
};
