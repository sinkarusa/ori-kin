/**
 * Export utilities for origami patterns
 */
import { ScatterTrace } from './pattern_generator';
import { getPseudoDomeConfig, getBarrelVaultConfig, getDoubleBarrelVaultConfig } from './configLoader';

/**
 * Create SVG from traces
 */
function createSvgFromTraces(
  traces: ScatterTrace[],
  metadata: {
    radius: number;
    segments: number;
    tiles?: number;
    omega?: number;
    height?: number;
    distance?: number;
    roundingDecimal: number;
  }
): string {
  const svgLines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800px" height="800px" viewBox="0 0 0 0" preserveAspectRatio="xMidYMid meet">',
    '<!-- Pattern dimensions in meters -->',
    '<!-- Units: All measurements are in meters -->',
  ];

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const trace of traces) {
    const x = trace.x;
    const y = trace.y;
    const color = trace.line?.color || '';
    const width = trace.line?.width || 1;
    const dash = trace.line?.dash || 'solid';

    if (x.length === 2 && x.every(coord => coord !== null) && y.every(coord => coord !== null)) {
      const x1 = x[0];
      const y1 = y[0];
      const x2 = x[1];
      const y2 = y[1];

      minX = Math.min(minX, x1, x2);
      maxX = Math.max(maxX, x1, x2);
      minY = Math.min(minY, y1, y2);
      maxY = Math.max(maxY, y1, y2);

      let strokeDasharray = 'none';
      if (dash === 'dash') strokeDasharray = '5,5';
      else if (dash === 'dot') strokeDasharray = '1,3';
      else if (dash === 'dashdot') strokeDasharray = '5,2,1,2';

      const scaledWidth = width * 0.01;

      const line = `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${scaledWidth}" stroke-dasharray="${strokeDasharray}" />`;
      svgLines.push(line);
    }
  }

  svgLines.push('</svg>');

  const patternWidth = maxX - minX;
  const patternHeight = maxY - minY;
  const paddingX = patternWidth * 0.1;
  const paddingY = patternHeight * 0.1;
  const viewboxX = minX - paddingX;
  const viewboxY = minY - paddingY;
  const viewboxWidth = patternWidth + (2 * paddingX);
  const viewboxHeight = patternHeight + (2 * paddingY);

  let metadataXml = '<metadata>\n  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n    <rdf:Description>\n';
  metadataXml += '      <units>meters</units>\n';
  metadataXml += `      <radius>${metadata.radius}</radius>\n`;
  metadataXml += `      <segments>${metadata.segments}</segments>\n`;
  if (metadata.tiles !== undefined) metadataXml += `      <tiles>${metadata.tiles}</tiles>\n`;
  if (metadata.omega !== undefined) metadataXml += `      <omega>${metadata.omega}</omega>\n`;
  if (metadata.height !== undefined) metadataXml += `      <height>${metadata.height}</height>\n`;
  if (metadata.distance !== undefined) metadataXml += `      <distance>${metadata.distance}</distance>\n`;
  metadataXml += '    </rdf:Description>\n  </rdf:RDF>\n</metadata>';

  svgLines.splice(3, 0, metadataXml);

  const viewboxStr = `${viewboxX} ${viewboxY} ${viewboxWidth} ${viewboxHeight}`;
  let svgContent = svgLines.join('\n');
  svgContent = svgContent.replace('viewBox="0 0 0 0"', `viewBox="${viewboxStr}"`);

  return svgContent;
}

/**
 * Create SVG for pseudo-dome pattern
 */
export async function createSvg(
  r: number,
  n: number,
  options?: {
    fold_color_1?: string;
    fold_color_2?: string;
    radial_color?: string;
    fold_width?: number;
    radial_width?: number;
  }
): Promise<string> {
  const { generatePattern } = await import('./pattern_generator');
  const config = await getPseudoDomeConfig();

  const traces = await generatePattern(r, n, {
    fold_color_1: options?.fold_color_1,
    fold_color_2: options?.fold_color_2,
    radial_color: options?.radial_color,
    fold_width: options?.fold_width,
    radial_width: options?.radial_width
  });

  return createSvgFromTraces(traces, {
    radius: r,
    segments: n,
    roundingDecimal: config.general.rounding_decimal
  });
}

/**
 * Create SVG for barrel vault pattern
 */
export async function createBarrelVaultSvg(
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
): Promise<string> {
  const { generateBarrelVaultPattern } = await import('./barrel_vault');
  const config = await getBarrelVaultConfig();

  const traces = await generateBarrelVaultPattern(r, n, m, omega, h, {
    fold_color_1: options?.fold_color_1,
    fold_color_2: options?.fold_color_2,
    connecting_color: options?.connecting_color,
    fold_width: options?.fold_width,
    connecting_width: options?.connecting_width
  });

  return createSvgFromTraces(traces, {
    radius: r,
    segments: n,
    tiles: m,
    omega,
    height: h,
    roundingDecimal: config.general.rounding_decimal
  });
}

/**
 * Create SVG for double barrel vault pattern
 */
export async function createDoubleBarrelVaultSvg(
  r: number,
  n: number,
  m: number,
  omega: number,
  a: number,
  options?: {
    fold_color_1?: string;
    fold_color_2?: string;
    connecting_color?: string;
    fold_width?: number;
    connecting_width?: number;
  }
): Promise<string> {
  const { generateDoubleBarrelVaultPattern } = await import('./double_barrel_vault');
  const config = await getDoubleBarrelVaultConfig();

  const traces = await generateDoubleBarrelVaultPattern(r, n, m, omega, a, {
    fold_color_1: options?.fold_color_1,
    fold_color_2: options?.fold_color_2,
    connecting_color: options?.connecting_color,
    fold_width: options?.fold_width,
    connecting_width: options?.connecting_width
  });

  return createSvgFromTraces(traces, {
    radius: r,
    segments: n,
    tiles: m,
    omega,
    distance: a,
    roundingDecimal: config.general.rounding_decimal
  });
}

/**
 * Save SVG content to a file (browser version)
 */
export function saveSvgToFile(svgContent: string, filename: string): void {
  const blob = new Blob([svgContent], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();

  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
}
