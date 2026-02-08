/**
 * Common utility functions shared across pattern generators and export functions.
 */

import { ScatterTrace } from './pattern_generator';

// Default rounding precision for coordinate comparison
export const ROUNDING_DECIMAL = 4;

/**
 * Remove duplicate traces based on rounded endpoint coordinates.
 *
 * Two traces are considered duplicates if they have the same start and end points
 * (within rounding precision), regardless of direction.
 *
 * @param traces - List of traces
 * @param roundingDecimal - Number of decimal places to round coordinates to
 * @returns List of unique traces
 */
export function removeDuplicateTraces(
  traces: ScatterTrace[],
  roundingDecimal: number = ROUNDING_DECIMAL
): ScatterTrace[] {
  const uniqueTraces: ScatterTrace[] = [];
  const uniqueCoords = new Set<string>();

  for (const trace of traces) {
    const x = trace.x;
    const y = trace.y;

    // Create coordinate tuple for comparison
    const x0 = Number(x[0].toFixed(roundingDecimal));
    const y0 = Number(y[0].toFixed(roundingDecimal));
    const x1 = Number(x[x.length - 1].toFixed(roundingDecimal));
    const y1 = Number(y[y.length - 1].toFixed(roundingDecimal));

    // Check both forward and reverse directions
    const traceCoords = `${x0},${y0},${x1},${y1}`;
    const reverseCoords = `${x1},${y1},${x0},${y0}`;

    if (!uniqueCoords.has(traceCoords) && !uniqueCoords.has(reverseCoords)) {
      uniqueCoords.add(traceCoords);
      uniqueTraces.push(trace);
    }
  }

  return uniqueTraces;
}

/**
 * Calculate slope between two points
 * Returns Infinity if horizontal (x2 - x1 === 0)
 */
export function calculateSlope(x1: number, y1: number, x2: number, y2: number): number {
  if (x2 - x1 === 0) {
    return Infinity;
  } else {
    return (y2 - y1) / (x2 - x1);
  }
}

/**
 * Clamp a value between min and max
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
