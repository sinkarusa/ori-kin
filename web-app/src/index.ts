/**
 * Ori-Kin - Origami Pattern Generator
 * 
 * This is the main entry point for the Ori-Kin TypeScript library.
 * It exports all pattern generation and export functionality.
 */

// Re-export pattern generators
export * from './utils/pattern_generator';
export * from './utils/barrel_vault';
export * from './utils/double_barrel_vault';

// Re-export export utilities
export * from './utils/export';

// Re-export calculation utilities
export * from './utils/calculations';

// Re-export config loader
export * from './utils/configLoader';

// Re-export common utilities
export * from './utils/common';

// Version information
export const VERSION = '1.0.0';
export const DESCRIPTION = 'Ori-Kin - Origami Pattern Generator';

/**
 * Library information
 */
export const info = {
  name: 'Ori-Kin',
  version: VERSION,
  description: DESCRIPTION,
  patterns: ['Pseudo Dome', 'Barrel Vault', 'Double Barrel Vault']
};

// Log library initialization
console.log(`${info.name} v${info.version} initialized`);
console.log(`Available patterns: ${info.patterns.join(', ')}`);
