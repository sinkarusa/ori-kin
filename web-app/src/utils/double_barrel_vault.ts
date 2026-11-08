import { getDoubleBarrelVaultConfig } from './configLoader';
import { calculateHeight, calculateSegmentLength, calculateAlpha1Angle, calculateAlpha2Angle, calculateBetaAngle } from './calculations';
import { ScatterTrace } from './pattern_generator';
import { removeDuplicateTraces } from './common';

type Options = {
  fold_color_1?: string;
  fold_color_2?: string;
  connecting_color?: string;
  fold_width?: number;
  connecting_width?: number;
};

/** n is the number of segments per arc. omega is retained for API compatibility:
 * the double-centered arch's angle is determined by a and r, not by omega. */
export async function generateDoubleBarrelVaultPattern(
  r: number, n: number, m: number, omega: number, a: number, options?: Options
): Promise<ScatterTrace[]> {
  if (!Number.isFinite(r) || r <= 0 || !Number.isFinite(a) || a < 0 || a >= 2 * r ||
      !Number.isInteger(n) || n < 2 || !Number.isInteger(m) || m < 1) {
    throw new Error('Double barrel vault requires r > 0, 0 ≤ a < 2r, at least 2 segments per arc, and a positive integer m.');
  }
  void omega;
  const alpha1 = calculateAlpha1Angle(a, r, n);
  const beta = calculateBetaAngle(a, r, n);
  const alpha2 = calculateAlpha2Angle(beta);
  const s = calculateSegmentLength(r, 2 * alpha1);
  const h = Math.min(calculateHeight(s, alpha1), calculateHeight(s, alpha2));
  const [cell, , width] = await generateDoubleBarrelVaultUnitCell(s, 2 * n, h, alpha1, alpha2, beta, a, options);
  const config = await getDoubleBarrelVaultConfig();
  const traces: ScatterTrace[] = [];
  for (let i = -(m - 1); i <= m - 1; i++) {
    for (const trace of cell) {
      traces.push({ ...trace, x: [...trace.x], y: trace.y.map(y => y + 4 * h * i) });
    }
  }
  const bottom = -2 * h * (2 * m - 1);
  const top = -bottom;
  const result = removeDuplicateTraces(traces, config.general.rounding_decimal).filter(trace =>
    !(trace.y.length === 2 && Math.abs(trace.y[0] - trace.y[1]) < 1e-9 &&
      (Math.abs(trace.y[0] - bottom) < 1e-9 || Math.abs(trace.y[0] - top) < 1e-9))
  );
  for (const y of [bottom, top]) result.push({
    x: [0, width], y: [y, y], mode: 'lines',
    line: { color: options?.connecting_color ?? config.colors.connecting_color, width: options?.fold_width ?? config.line_widths.fold_width, dash: 'solid' }
  });
  return result;
}

/** Draw one cell. Here n is the total number of segments, with the apex at n/2. */
export async function generateDoubleBarrelVaultUnitCell(
  s: number, n: number, h: number, alpha1: number, alpha2: number, beta: number, a: number, options?: Options
): Promise<[ScatterTrace[], number[], number]> {
  void beta;
  void a;
  if (!Number.isInteger(n) || n < 4 || n % 2 !== 0 || !Number.isFinite(s) || s <= 0 ||
      !Number.isFinite(h) || h <= 0 || !Number.isFinite(alpha1) || alpha1 <= 0 ||
      !Number.isFinite(alpha2) || alpha2 <= 0) {
    throw new Error('Invalid double barrel vault unit cell geometry.');
  }
  const config = await getDoubleBarrelVaultConfig();
  const fold1 = options?.fold_color_1 ?? config.colors.fold_color_1;
  const fold2 = options?.fold_color_2 ?? config.colors.fold_color_2;
  const connecting = options?.connecting_color ?? config.colors.connecting_color;
  const foldWidth = options?.fold_width ?? config.line_widths.fold_width;
  const connectingWidth = options?.connecting_width ?? config.line_widths.connecting_width;
  const width = n * s;
  const traces: ScatterTrace[] = [];
  const line = (x1: number, y1: number, x2: number, y2: number, color: string, lineWidth: number, dash?: string) => {
    if (Math.hypot(x2 - x1, y2 - y1) < 1e-10) return;
    traces.push({ x: [x1, x2], y: [y1, y2], mode: 'lines', line: { color, width: lineWidth, ...(dash ? { dash } : {}) } });
  };
  const offsets = [alpha1, alpha2].map(alpha => 2 * h / Math.tan(alpha * Math.PI / 180));
  if (offsets.some(d => !Number.isFinite(d) || d > s + 1e-9)) throw new Error('Row height causes intersecting creases.');
  for (const direction of [1, -1]) {
    let x = 0;
    let y = 0;
    const last = [0, 0];
    for (let k = 1; k < n; k++) {
      const d = offsets[k === n / 2 ? 1 : 0];
      const left = k * s - d / 2;
      const right = k * s + d / 2;
      line(x, y, left, y, fold1, foldWidth);
      const nextY = y === 0 ? direction * 2 * h : 0;
      line(left, y, right, nextY, fold1, foldWidth);
      line(last[nextY === 0 ? 0 : 1], nextY, right, nextY, fold2, foldWidth, 'solid');
      last[y === 0 ? 0 : 1] = left;
      x = right;
      y = nextY;
    }
    line(x, y, width, y, fold1, foldWidth);
    const otherY = y === 0 ? direction * 2 * h : 0;
    line(last[otherY === 0 ? 0 : 1], otherY, width, otherY, fold2, foldWidth, 'solid');
  }
  for (const x of [0, width]) line(x, -2 * h, x, 2 * h, connecting, connectingWidth, config.line_styles.connecting_line_style);
  return [removeDuplicateTraces(traces, config.general.rounding_decimal), [-2 * h, 0, 2 * h], width];
}
