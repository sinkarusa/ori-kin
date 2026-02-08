/**
 * Barrel Vault Pattern Generator
 */
import { getBarrelVaultConfig, BarrelVaultConfig } from './configLoader';
import {
  calculateSegmentAngle,
  calculateHeight,
  calculateFoldingAngle,
  calculateSegmentLength
} from './calculations';
import { ScatterTrace } from './pattern_generator';
import { removeDuplicateTraces, ROUNDING_DECIMAL } from './common';

/**
 * Generate barrel vault pattern
 *
 * @param r Radius
 * @param n Number of segments
 * @param m Number of repetitions
 * @param omega Angle
 * @param h Height
 * @param options Optional configuration overrides
 * @returns Array of scatter traces for plotting
 */
export async function generateBarrelVaultPattern(
  r: number,
  n: number,
  m: number,
  omega: number,
  h: number,
  options?: {
    fold_color_1?: string;
    fold_color_2?: string;
    connecting_color?: string;
    fold_width?: number;
    connecting_width?: number;
  }
): Promise<ScatterTrace[]> {
  // Load configuration
  const config = await getBarrelVaultConfig();

  // Use provided values or defaults from config
  const fold_color_1 = options?.fold_color_1 || config.colors.fold_color_1;
  const fold_color_2 = options?.fold_color_2 || config.colors.fold_color_2;
  const connecting_color = options?.connecting_color || config.colors.connecting_color;
  const fold_width = options?.fold_width || config.line_widths.fold_width;
  const connecting_width = options?.connecting_width || config.line_widths.connecting_width;
  const rounding_decimal = config.general.rounding_decimal;

  // Calculate basic parameters
  const theta = calculateSegmentAngle(omega, n);
  const s = calculateSegmentLength(r, theta);
  const alpha = calculateFoldingAngle(theta);
  const h_max = calculateHeight(s, alpha);
  const clipped_h = Math.min(Math.max(h, 0), h_max);

  const [unit_cell_traces, hl_pos, total_length] = await generateBarrelVaultPatternUnitCell(
    s, n, clipped_h, alpha,
    {
      fold_color_1,
      fold_color_2,
      connecting_color,
      fold_width,
      connecting_width
    }
  );

  let full_traces: ScatterTrace[] = [...unit_cell_traces];

  // Generate repeated patterns
  for (let i = 1; i < m; i++) {
    for (const trace of unit_cell_traces) {
      const x = [...trace.x];
      const y = [...trace.y];

      // Translate up
      const y_translated_up = y.map(yVal => yVal + 4 * clipped_h * i);
      full_traces.push({
        x: x,
        y: y_translated_up,
        mode: trace.mode,
        line: trace.line ? { ...trace.line } : undefined,
        marker: trace.marker ? { ...trace.marker } : undefined
      });

      // Translate down
      const y_translated_down = y.map(yVal => yVal - 4 * clipped_h * i);
      full_traces.push({
        x: x,
        y: y_translated_down,
        mode: trace.mode,
        line: trace.line ? { ...trace.line } : undefined,
        marker: trace.marker ? { ...trace.marker } : undefined
      });
    }
  }

  // Remove duplicate traces
  full_traces = removeDuplicateTraces(full_traces, rounding_decimal);

  // Change color of top and bottom most horizontal traces
  const y_bottom = hl_pos[0] * (2 * m - 1);
  const y_top = hl_pos[hl_pos.length - 1] * (2 * m - 1);

  // Remove all traces on top and bottom
  const traces_final: ScatterTrace[] = [];

  for (const trace of full_traces) {
    if (trace.x.length === 2 && trace.y.length === 2) {
      const y1 = trace.y[0];
      const y2 = trace.y[1];

      if ((Math.abs(y1 - y_bottom) < 0.001 && Math.abs(y2 - y_bottom) < 0.001) ||
          (Math.abs(y1 - y_top) < 0.001 && Math.abs(y2 - y_top) < 0.001)) {
        // Skip this trace, we'll add a special one instead
        continue;
      }

      traces_final.push(trace);
    } else {
      traces_final.push(trace);
    }
  }

  // Add horizontal traces at top and bottom
  traces_final.push({
    x: [0, total_length],
    y: [y_bottom, y_bottom],
    mode: 'lines',
    line: { color: connecting_color, width: fold_width, dash: 'solid' }
  });

  traces_final.push({
    x: [0, total_length],
    y: [y_top, y_top],
    mode: 'lines',
    line: { color: connecting_color, width: fold_width, dash: 'solid' }
  });

  return traces_final;
}

/**
 * Generate barrel vault pattern unit cell
 *
 * @param s Segment length
 * @param n Number of segments
 * @param h Height
 * @param alpha Folding angle
 * @param options Optional configuration overrides
 * @returns [Array of scatter traces for plotting, Array of horizontal line positions, Total length]
 */
export async function generateBarrelVaultPatternUnitCell(
  s: number,
  n: number,
  h: number,
  alpha: number,
  options?: {
    fold_color_1?: string;
    fold_color_2?: string;
    connecting_color?: string;
    fold_width?: number;
    connecting_width?: number;
  }
): Promise<[ScatterTrace[], number[], number]> {
  // Load configuration
  const config = await getBarrelVaultConfig();
  const fold_color_1 = options?.fold_color_1 || config.colors.fold_color_1;
  const fold_color_2 = options?.fold_color_2 || config.colors.fold_color_2;
  const connecting_color = options?.connecting_color || config.colors.connecting_color;
  const fold_width = options?.fold_width || config.line_widths.fold_width;
  const connecting_width = options?.connecting_width || config.line_widths.connecting_width;
  const connecting_line_style = config.line_styles.connecting_line_style;
  const rounding_decimal = config.general.rounding_decimal;

  // Calculate basic parameters
  const s_angled = Math.abs(2 * h / Math.tan(alpha * Math.PI / 180));
  const traces: ScatterTrace[] = [];

  // Generate horizontal segment at the beginning
  let current_x = 0;
  let current_y = 0;
  const first_flat_segment_length = s - s_angled / 2;
  let next_x = current_x + first_flat_segment_length;
  let next_y = current_y;

  // Horizontal segment
  traces.push({
    x: [current_x, next_x],
    y: [current_y, next_y],
    mode: 'lines',
    line: { color: fold_color_1, width: fold_width }
  });

  // Valley folds start and end points
  const valley_fold_traces: [number, number][][] = [];
  valley_fold_traces.push([[next_x, next_y]]);

  const n_reps = n % 2 ? Math.floor(n / 2) : Math.floor(n / 2) - 1;
  const current_x_sym_org = next_x;
  const current_y_sym_org = next_y;

  // For both +y and -y directions
  for (let j = 0; j < 2; j++) {
    const y_dir = j === 0 ? 1 : -1;
    current_x = current_x_sym_org;
    current_y = current_y_sym_org;

    // Center valley fold
    const upper_and_lower_valley_fold_start: [number, number] = [0, y_dir * 2 * h];
    let center_valley_fold_start: [number, number] = [current_x, current_y];
    let center_valley_fold_end: [number, number] = [current_x, current_y];

    for (let i = 0; i < n_reps; i++) {
      next_x = current_x + s_angled;
      next_y = current_y + y_dir * 2 * h;
      center_valley_fold_start = [current_x, current_y];

      // Upper diagonal
      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: fold_color_1, width: fold_width }
      });

      current_x = next_x;
      current_y = next_y;

      // Add upper valley fold
      traces.push({
        x: [upper_and_lower_valley_fold_start[0], next_x],
        y: [upper_and_lower_valley_fold_start[1], upper_and_lower_valley_fold_start[1]],
        mode: 'lines',
        line: { color: fold_color_2, width: fold_width, dash: 'solid' }
      });

      next_x = current_x + s - s_angled;
      next_y = current_y;

      if (next_x > current_x) {
        // Trapezoid straight section
        traces.push({
          x: [current_x, next_x],
          y: [current_y, next_y],
          mode: 'lines',
          line: { color: fold_color_1, width: fold_width }
        });
      }

      upper_and_lower_valley_fold_start[0] = next_x;
      upper_and_lower_valley_fold_start[1] = next_y;

      // Lower diagonal
      current_x = next_x;
      current_y = next_y;
      next_x = current_x + s_angled;
      next_y = current_y - y_dir * 2 * h;
      center_valley_fold_end = [next_x, next_y];

      // Lower diagonal
      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: fold_color_1, width: fold_width }
      });

      current_x = next_x;
      current_y = next_y;

      // Add center valley fold
      traces.push({
        x: [center_valley_fold_start[0], center_valley_fold_end[0]],
        y: [center_valley_fold_start[1], center_valley_fold_end[1]],
        mode: 'lines',
        line: { color: fold_color_2, width: fold_width, dash: 'solid' }
      });

      next_x = current_x + s - s_angled;
      next_y = current_y;

      if ((n % 2 === 1) && (i === n_reps - 1)) {
        next_x = current_x + first_flat_segment_length;
      }

      // Trapezoid straight section
      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: fold_color_1, width: fold_width }
      });

      current_x = next_x;
      current_y = next_y;
    }

    // Handle even n (outside the loop)
    if (n % 2 === 0) {
      // Then we do one diagonal step only
      center_valley_fold_start[0] = current_x;
      next_x = current_x + s_angled;
      next_y = current_y + y_dir * 2 * h;

      // Upper diagonal
      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: fold_color_1, width: fold_width }
      });

      current_x = next_x;
      current_y = next_y;

      next_x = current_x + s - s_angled / 2;
      next_y = current_y;

      // Trapezoid straight section
      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: fold_color_1, width: fold_width }
      });

      traces.push({
        x: [center_valley_fold_start[0], next_x],
        y: [center_valley_fold_start[1], center_valley_fold_end[1]],
        mode: 'lines',
        line: { color: fold_color_2, width: fold_width, dash: 'solid' }
      });

      // Update current position
      current_x = next_x;
      current_y = next_y;
    }

    // Add valley fold (after all handling)
    traces.push({
      x: [upper_and_lower_valley_fold_start[0], current_x],
      y: [upper_and_lower_valley_fold_start[1], upper_and_lower_valley_fold_start[1]],
      mode: 'lines',
      line: { color: fold_color_2, width: fold_width, dash: 'solid' }
    });
  }

  // Horizontal lines positions
  const hl_pos = [-2 * h, 0, 2 * h];
  const total_length = n * s;

  // Vertical lines
  const vl_pos = [0, total_length];
  for (const vlp of vl_pos) {
    traces.push({
      x: [vlp, vlp],
      y: [Math.min(...hl_pos), Math.max(...hl_pos)],
      mode: 'lines',
      line: {
        color: connecting_color,
        width: connecting_width,
        dash: connecting_line_style
      }
    });
  }

  // Remove duplicate traces
  const unique_traces = removeDuplicateTraces(traces, rounding_decimal);

  return [unique_traces, hl_pos, total_length];
}
