/**
 * Pattern Generator Module
 * Exports all pattern generation functions
 */
import { getPseudoDomeConfig } from './configLoader';
import { calculateParameters } from './calculations';
import { removeDuplicateTraces, calculateSlope } from './common';

// Define interfaces for Plotly-compatible traces
export interface ScatterTrace {
  x: number[];
  y: number[];
  mode: string;
  line?: {
    color: string;
    width: number;
    dash?: string;
  };
  marker?: {
    color: string;
    size: number;
  };
}

/**
 * Generate pattern for the pseudo-dome
 */
export async function generatePattern(
  r: number,
  n: number,
  options?: {
    fold_color_1?: string;
    fold_color_2?: string;
    radial_color?: string;
    fold_width?: number;
    radial_width?: number;
  }
): Promise<ScatterTrace[]> {
  const config = await getPseudoDomeConfig();

  const fold_color_1 = options?.fold_color_1 || config.colors.fold_color_1;
  const fold_color_2 = options?.fold_color_2 || config.colors.fold_color_2;
  const radial_color = options?.radial_color || config.colors.radial_color;
  const fold_width = options?.fold_width || config.line_widths.fold_width;
  const radial_width = options?.radial_width || config.line_widths.radial_width;
  const radial_line_style = config.line_styles.radial_line_style;
  const rounding_decimal = config.general.rounding_decimal;

  const [thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, num_radial_segments] = calculateParameters(r, n);

  const traces: ScatterTrace[] = [];

  function generateHalfPattern(inverse: boolean = false): void {
    let current_x = 0;
    let current_y = 0;
    let current_angle = 0;
    const points: [number, number][] = [];
    const starts_of_radial_segments: [number, number][] = [];

    for (let i = 0; i < s.length; i++) {
      const angle_factor = inverse ? -1 : 1;
      const next_x = current_x + s[i] * Math.cos(angle_factor * current_angle);
      const next_y = current_y + s[i] * Math.sin(angle_factor * current_angle);

      // Match Python: i=0 uses fold_color_1 (green), i>0 uses fold_color_2 (red)
      const color = i > 0 ? fold_color_2 : fold_color_1;

      if ((i === 0) && (current_angle === 0)) {
        starts_of_radial_segments.push([next_x, next_y]);
      }

      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color, width: fold_width }
      });

      current_x = next_x;
      current_y = next_y;

      if (i < s.length - 1) {
        if (i === 0) {
          current_angle += Math.PI - beta[i];
        } else if (i % 2 === 1) {
          current_angle -= Math.PI - beta[i];
        } else {
          current_angle += Math.PI - beta[i];
        }
      }
    }

    points.push([current_x, current_y]);
    starts_of_radial_segments.push([0, 0]);

    if (n % 2 === 0) {
      starts_of_radial_segments.reverse();
    }

    const i = s.length - 1;

    if (inverse) {
      if (i % 2 === 1) {
        current_angle += Math.PI + alpha[alpha.length - 1][1];
      } else {
        current_angle -= Math.PI + alpha[alpha.length - 1][1];
      }
      const next_x = current_x + h[h.length - 1] * Math.cos(-current_angle);
      const next_y = current_y + h[h.length - 1] * Math.sin(-current_angle);

      points.push([next_x, next_y]);

      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: 'black', width: fold_width }
      });
    } else {
      if (i % 2 === 1) {
        current_angle -= Math.PI - alpha[alpha.length - 1][1];
      } else {
        current_angle += Math.PI - alpha[alpha.length - 1][1];
      }
      const next_x = current_x + h[h.length - 1] * Math.cos(current_angle);
      const next_y = current_y + h[h.length - 1] * Math.sin(current_angle);

      points.push([next_x, next_y]);

      traces.push({
        x: [current_x, next_x],
        y: [current_y, next_y],
        mode: 'lines',
        line: { color: 'black', width: fold_width }
      });
    }

    for (let i = 0; i < points.length; i++) {
      const line_dash = radial_line_style;

      if (i < starts_of_radial_segments.length + 1) {
        traces.push({
          x: [starts_of_radial_segments[i][0], points[i][0]],
          y: [starts_of_radial_segments[i][1], points[i][1]],
          mode: 'lines',
          line: {
            color: radial_color,
            width: radial_width,
            dash: line_dash
          }
        });
      }
    }
  }

  generateHalfPattern();
  generateHalfPattern(true);

  let unique_traces = removeDuplicateTraces(traces, rounding_decimal);

  // Generate full radial pattern
  const full_traces = [...unique_traces];

  for (let i = 1; i < Math.floor(num_radial_segments / 2); i++) {
    const rotation = i * 2 * alpha[0][0];
    const cos_rot = Math.cos(rotation);
    const sin_rot = Math.sin(rotation);

    for (const trace of unique_traces) {
      const x = [...trace.x];
      const y = [...trace.y];
      const rotated_x: number[] = [];
      const rotated_y: number[] = [];

      for (let j = 0; j < x.length; j++) {
        rotated_x.push(x[j] * cos_rot - y[j] * sin_rot);
        rotated_y.push(x[j] * sin_rot + y[j] * cos_rot);
      }

      full_traces.push({
        x: rotated_x,
        y: rotated_y,
        mode: trace.mode,
        line: trace.line ? { ...trace.line } : undefined,
        marker: trace.marker ? { ...trace.marker } : undefined
      });
    }
  }

  let final_traces = removeDuplicateTraces(full_traces, rounding_decimal);

  // Add cut line
  let max_x = -Infinity;
  for (const trace of final_traces) {
    if (trace.x.length > 0 && trace.x[trace.x.length - 1] > max_x) {
      max_x = trace.x[trace.x.length - 1];
    }
  }

  final_traces.reverse();

  const lastTrace = final_traces[final_traces.length - 1];
  if (lastTrace) {
    lastTrace.x[lastTrace.x.length - 1] = max_x;

    const cutline_xpositions = [0, lastTrace.x[lastTrace.x.length - 1]];
    const cutline_ypositions = [0, lastTrace.y[lastTrace.y.length - 1]];
    const cutline_slope = parseFloat(calculateSlope(
      cutline_xpositions[0],
      cutline_ypositions[0],
      cutline_xpositions[1],
      cutline_ypositions[1]
    ).toFixed(rounding_decimal));

    // Remove overlapping traces
    for (let i = 0; i < final_traces.length; i++) {
      const trace = final_traces[i];
      if (!trace.x || trace.x.length < 2) continue;

      const x1 = parseFloat(trace.x[0].toFixed(rounding_decimal));
      const y1 = parseFloat(trace.y[0].toFixed(rounding_decimal));
      const x2 = parseFloat(trace.x[trace.x.length - 1].toFixed(rounding_decimal));
      const y2 = parseFloat(trace.y[trace.y.length - 1].toFixed(rounding_decimal));

      const trace_slope = parseFloat(calculateSlope(x1, y1, x2, y2).toFixed(rounding_decimal));

      const endpointMatch =
        (parseFloat(trace.x[1].toFixed(rounding_decimal)) === parseFloat(cutline_xpositions[1].toFixed(rounding_decimal)) &&
         parseFloat(trace.y[1].toFixed(rounding_decimal)) === parseFloat(cutline_ypositions[1].toFixed(rounding_decimal)));

      const isGreenLine = trace.line?.color === fold_color_1;
      const isOnXAxis = Math.abs(y1) < 1e-10 && Math.abs(y2) < 1e-10;

      let overlapsWithCutline = false;
      if (isOnXAxis && isGreenLine) {
        const cutlineEndX = parseFloat(cutline_xpositions[1].toFixed(rounding_decimal));
        const minX = Math.min(x1, x2);
        const maxX = Math.max(x1, x2);
        if (minX >= 0 && maxX <= cutlineEndX) {
          overlapsWithCutline = true;
        }
      }

      if ((!isGreenLine) && (endpointMatch && trace_slope === cutline_slope) || overlapsWithCutline) {
        final_traces.splice(i, 1);
        i--;
      }
    }

    final_traces.push({
      x: cutline_xpositions,
      y: cutline_ypositions,
      mode: 'lines',
      line: { color: fold_color_1, width: fold_width }
    });
  }

  return final_traces;
}
