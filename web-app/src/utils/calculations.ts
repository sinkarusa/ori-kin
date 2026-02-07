/**
 * Mathematical calculations for origami pattern generation
 */

/**
 * Calculate parameters for pseudo-dome pattern
 */
export function calculateParameters(r: number, n: number): [number[], number[], number[], number[], number[], [number, number][], number[], number, number, number, number, number] {
  // Convert degrees to radians
  const degreesToRadians = (degrees: number): number => degrees * Math.PI / 180;
  
  // Convert radians to degrees
  const radiansToDegrees = (radians: number): number => radians * 180 / Math.PI;

  const theta1 = degreesToRadians(180 / (n * (n + 1)));
  const theta_l = (Math.PI / n) - theta1;
  const CD = (theta_l - theta1) / (n - 1);
  
  const thetas: number[] = [];
  for (let i = 0; i < n; i++) {
    thetas.push(theta1 + i * CD);
  }
  
  const s: number[] = thetas.map(theta => 2 * r * Math.sin(theta / 2));
  const A: number[] = thetas.map(theta => Math.PI / 2 - theta / 2);
  
  const beta: number[] = [];
  for (let i = 0; i < n - 1; i++) {
    beta.push(A[i] + A[i + 1]);
  }
  
  const a: number[] = [];
  for (let i = 0; i < n - 1; i++) {
    a.push(2 * r * Math.cos((Math.PI - (thetas[i] + thetas[i + 1])) / 2));
  }
  
  const alpha: [number, number][] = [];
  for (let i = 0; i < n - 1; i++) {
    const alpha_i1 = Math.asin(Math.sin(beta[i]) * s[i + 1] / a[i]);
    const alpha_i2 = Math.asin(Math.sin(beta[i]) * s[i] / a[i]);
    alpha.push([alpha_i1, alpha_i2]);
  }
  
  // Calculate heights (h)
  const h: number[] = [s[0] * Math.sin(alpha[0][0])]; // h1 uses alpha11
  for (let i = 1; i < n - 1; i++) {
    h.push(s[i] * Math.sin(alpha[i][0]));
  }
  
  // Calculate last parameters that are special
  const alpha_l1 = Math.PI - (beta[beta.length - 1] + alpha[alpha.length - 2][1]);
  const alpha_l2 = Math.PI / 2 - alpha_l1;
  
  const hl = s[s.length - 1] * Math.sin(alpha_l1);
  alpha.push([alpha_l1, alpha_l2]);
  
  h.push(hl);
  
  // Calculate number of radial segments
  const num_radial_segments = Math.round(360 / (2 * radiansToDegrees(alpha[0][0] / 2)));
  
  return [thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha[0][0], num_radial_segments];
}

/**
 * Calculate segment angle θ using equation 3.1
 */
export function calculateSegmentAngle(omega: number, n: number): number {
  return omega / n;
}

/**
 * Calculate segment length s using equation 3.2
 */
export function calculateSegmentLength(r: number, theta: number): number {
  return 2 * r * Math.sin(degreesToRadians(theta / 2));
}

/**
 * Calculate folding angle α using equation 3.9
 */
export function calculateFoldingAngle(theta: number): number {
  const beta = Math.PI - degreesToRadians(theta); // equation 3.7
  return radiansToDegrees((Math.PI - beta) / 2);
}

/**
 * Calculate height h using equation 3.10
 */
export function calculateHeight(s: number, alpha: number): number {
  return Math.tan(degreesToRadians(alpha)) * (s / 2);
}

/**
 * Helper function to convert degrees to radians
 */
export function degreesToRadians(degrees: number): number {
  return degrees * Math.PI / 180;
}

/**
 * Helper function to convert radians to degrees
 */
export function radiansToDegrees(radians: number): number {
  return radians * 180 / Math.PI;
}

/**
 * Calculate double barrel vault's alpha1 angle using ASKK's equation from notes
 */
export function calculateAlpha1Angle(a: number, r: number, n: number): number {
  return radiansToDegrees(Math.acos(a / (2 * r)) / (2 * n));
}

/**
 * Calculate double barrel vault's alpha2 angle using ASKK's equation from notes
 */
export function calculateAlpha2Angle(beta: number): number {
  return (90 - beta) / 2;
}

/**
 * Calculate double barrel vault's beta angle using ASKK's equation from notes
 */
export function calculateBetaAngle(a: number, r: number, n: number): number {
  const invcos_a2r = Math.acos(a / (2 * r));
  return radiansToDegrees((2 * invcos_a2r) - invcos_a2r / n);
}
