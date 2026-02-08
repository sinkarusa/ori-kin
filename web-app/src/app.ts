/**
 * Ori-Kin Main Application
 * Browser-based origami pattern generator with routing
 */
// @ts-ignore
import * as Plotly from 'plotly.js-dist-min';
import {
  generatePattern,
  generateBarrelVaultPattern,
  generateDoubleBarrelVaultPattern,
  createSvg,
  createBarrelVaultSvg,
  createDoubleBarrelVaultSvg,
  saveSvgToFile,
  calculateParameters,
  calculateSegmentAngle,
  calculateFoldingAngle,
  calculateSegmentLength,
  calculateHeight,
  ScatterTrace
} from './index';

// App state
let currentPattern: 'pseudo-dome' | 'barrel-vault' | 'double-barrel-vault' = 'pseudo-dome';

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', () => {
  setupStyles();
  setupRouter();
});

/**
 * Set up CSS styles
 */
function setupStyles(): void {
  const style = document.createElement('style');
  style.textContent = `
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: #f5f5f5;
      color: #333;
    }

    /* Landing Page */
    .landing-page {
      text-align: center;
      padding: 40px 20px;
      max-width: 1200px;
      margin: 0 auto;
    }
    .landing-page h1 {
      font-size: 2.5rem;
      margin-bottom: 40px;
      color: #2c3e50;
    }
    .pattern-cards {
      display: flex;
      justify-content: center;
      gap: 30px;
      flex-wrap: wrap;
      margin-bottom: 60px;
    }
    .pattern-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      width: 280px;
    }
    .pattern-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    .pattern-card img {
      width: 100%;
      height: 180px;
      object-fit: contain;
      border-radius: 8px;
      margin-bottom: 15px;
      background: #f9f9f9;
    }
    .pattern-card h3 {
      font-size: 1.2rem;
      color: #2c3e50;
    }
    .footer {
      text-align: center;
      padding: 20px;
      border-top: 1px solid #ddd;
      color: #666;
      font-size: 0.9rem;
    }
    .footer a {
      color: #3498db;
      text-decoration: none;
    }
    .footer a:hover {
      text-decoration: underline;
    }
    .github-link {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-left: 10px;
    }
    .github-icon {
      width: 20px;
      height: 20px;
    }

    /* Generator Page Layout */
    .generator-page {
      max-width: 1400px;
      margin: 0 auto;
      padding: 20px;
    }
    .generator-page h1 {
      text-align: center;
      margin-bottom: 20px;
      font-size: 1.8rem;
    }
    .back-link {
      display: inline-block;
      margin-bottom: 20px;
      color: #3498db;
      text-decoration: none;
    }
    .back-link:hover {
      text-decoration: underline;
    }

    /* Three Column Layout */
    .three-column-layout {
      display: flex;
      gap: 20px;
      align-items: flex-start;
    }
    .left-panel {
      width: 20%;
      min-width: 200px;
    }
    .center-panel {
      width: 50%;
      flex: 1;
    }
    .right-panel {
      width: 25%;
      min-width: 250px;
    }

    /* Input Controls */
    .control-group {
      margin-bottom: 15px;
    }
    .control-label {
      display: flex;
      align-items: center;
      font-weight: 600;
      margin-bottom: 5px;
      font-size: 0.9rem;
    }
    .help-button {
      background: none;
      border: none;
      color: #3498db;
      cursor: pointer;
      margin-left: 5px;
      font-size: 14px;
      padding: 0;
      width: 20px;
      height: 20px;
    }
    .help-button:hover {
      color: #2980b9;
    }
    input[type="number"] {
      width: 100%;
      padding: 8px 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 0.95rem;
    }
    input[type="number"]:focus {
      outline: none;
      border-color: #3498db;
    }
    .button-group {
      display: flex;
      gap: 10px;
      margin-top: 20px;
      justify-content: center;
    }
    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: background 0.2s;
    }
    .btn-primary {
      background: #4CAF50;
      color: white;
    }
    .btn-primary:hover {
      background: #45a049;
    }
    .btn-secondary {
      background: #2196F3;
      color: white;
    }
    .btn-secondary:hover {
      background: #1976D2;
    }

    /* Plot Container */
    #plot-container {
      width: 100%;
      height: 600px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Parameter Display */
    .parameter-display {
      background: white;
      padding: 15px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .parameter-display h3 {
      margin-bottom: 15px;
      font-size: 1.1rem;
      color: #2c3e50;
    }
    .parameter-section {
      margin-bottom: 15px;
    }
    .parameter-section h4 {
      font-size: 0.85rem;
      color: #666;
      margin-bottom: 8px;
      text-transform: uppercase;
    }
    .parameter-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      font-size: 0.9rem;
    }
    .parameter-label {
      color: #555;
    }
    .parameter-value {
      font-weight: 500;
      color: #2c3e50;
    }

    /* Help Modal */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 1000;
      justify-content: center;
      align-items: center;
    }
    .modal-overlay.active {
      display: flex;
    }
    .modal-content {
      background: white;
      border-radius: 8px;
      max-width: 800px;
      max-height: 90vh;
      overflow: auto;
      position: relative;
    }
    .modal-header {
      padding: 15px 20px;
      border-bottom: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-header h2 {
      font-size: 1.2rem;
      margin: 0;
    }
    .modal-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #666;
    }
    .modal-body {
      padding: 20px;
    }
    .modal-body img {
      max-width: 100%;
      height: auto;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .three-column-layout {
        flex-direction: column;
      }
      .left-panel, .center-panel, .right-panel {
        width: 100%;
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * Set up simple router based on URL hash
 */
function setupRouter(): void {
  const app = document.getElementById('app') || document.body;

  function render() {
    const hash = window.location.hash.slice(1) || '/';

    if (hash === '/') {
      renderLandingPage(app);
    } else if (hash === '/pseudo-dome') {
      currentPattern = 'pseudo-dome';
      renderGeneratorPage(app, 'pseudo-dome');
    } else if (hash === '/barrel-vault') {
      currentPattern = 'barrel-vault';
      renderGeneratorPage(app, 'barrel-vault');
    } else if (hash === '/double-barrel-vault') {
      currentPattern = 'double-barrel-vault';
      renderGeneratorPage(app, 'double-barrel-vault');
    } else {
      window.location.hash = '/';
    }
  }

  window.addEventListener('hashchange', render);
  render();
}

/**
 * Render landing page
 */
function renderLandingPage(container: HTMLElement): void {
  container.innerHTML = `
    <div class="landing-page">
      <h1>ORI-KIN</h1>
      <div class="pattern-cards">
        <div class="pattern-card" data-route="/pseudo-dome">
          <img src="/assets/pseudo_dome.png" alt="Pseudo-Dome" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22180%22><rect fill=%22%23f0f0f0%22 width=%22200%22 height=%22180%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22>Pseudo-Dome</text></svg>'">
          <h3>Pseudo-Dome</h3>
        </div>
        <div class="pattern-card" data-route="/barrel-vault">
          <img src="/assets/single_center_barrel_vault.png" alt="Single-center Barrel Vault" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22180%22><rect fill=%22%23f0f0f0%22 width=%22200%22 height=%22180%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22>Single Barrel Vault</text></svg>'">
          <h3>Single-center Barrel Vault</h3>
        </div>
        <div class="pattern-card" data-route="/double-barrel-vault">
          <img src="/assets/double_center_barrel_vault.png" alt="Double-center Barrel Vault" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22180%22><rect fill=%22%23f0f0f0%22 width=%22200%22 height=%22180%22/><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22>Double Barrel Vault</text></svg>'">
          <h3>Double-center Barrel Vault</h3>
        </div>
      </div>
      <div class="footer">
        <p>
          Copyright © 2024-2025
          <a href="https://askk-arch.com.tr" target="_blank">Andrée Sonad Karaveli Kartal</a>,
          <a href="https://github.com/sinkarusa" target="_blank">Sinan Karaveli</a>
          <a href="https://github.com/sinkarusa/ori-kin" target="_blank" class="github-link">
            <img src="/assets/github-mark.png" alt="GitHub" class="github-icon" onerror="this.style.display='none'">
          </a>
        </p>
      </div>
    </div>
  `;

  // Add click handlers
  container.querySelectorAll('.pattern-card').forEach(card => {
    card.addEventListener('click', () => {
      const route = card.getAttribute('data-route');
      if (route) window.location.hash = route;
    });
  });
}

/**
 * Render generator page based on pattern type
 */
function renderGeneratorPage(container: HTMLElement, patternType: 'pseudo-dome' | 'barrel-vault' | 'double-barrel-vault'): void {
  const titles: Record<string, string> = {
    'pseudo-dome': 'Pseudo-Dome Pattern Generator',
    'barrel-vault': 'Barrel Vault Pattern Generator',
    'double-barrel-vault': 'Double Barrel Vault Pattern Generator'
  };

  container.innerHTML = `
    <div class="generator-page">
      <a href="#/" class="back-link">← Back to patterns</a>
      <h1>${titles[patternType]}</h1>
      <div class="three-column-layout">
        <div class="left-panel" id="controls-panel"></div>
        <div class="center-panel">
          <div id="plot-container"></div>
        </div>
        <div class="right-panel">
          <div class="parameter-display" id="parameter-display"></div>
        </div>
      </div>
    </div>
    <div class="modal-overlay" id="help-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Pattern Information</h2>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body" id="modal-body"></div>
      </div>
    </div>
  `;

  // Setup modal close
  const modal = container.querySelector('#help-modal') as HTMLElement;
  const modalClose = container.querySelector('.modal-close') as HTMLElement;
  modalClose?.addEventListener('click', () => modal?.classList.remove('active'));
  modal?.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('active');
  });

  // Render appropriate controls
  if (patternType === 'pseudo-dome') {
    renderPseudoDomeControls(container);
  } else if (patternType === 'barrel-vault') {
    renderBarrelVaultControls(container, false);
  } else {
    renderBarrelVaultControls(container, true);
  }
}

/**
 * Render Pseudo-Dome controls
 */
function renderPseudoDomeControls(container: HTMLElement): void {
  const controlsPanel = container.querySelector('#controls-panel') as HTMLElement;
  controlsPanel.innerHTML = `
    <div class="control-group">
      <div class="control-label">
        Radius (r):
        <button class="help-button" data-help="radius">?</button>
      </div>
      <input type="number" id="radius-input" value="5" min="1" step="0.1">
    </div>
    <div class="control-group">
      <div class="control-label">
        Segments (n):
        <button class="help-button" data-help="segments">?</button>
      </div>
      <input type="number" id="segments-input" value="5" min="3" step="1">
    </div>
    <div class="button-group">
      <button class="btn btn-primary" id="export-svg">Export SVG</button>
    </div>
  `;

  // Add help handlers
  container.querySelectorAll('.help-button').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = container.querySelector('#help-modal') as HTMLElement;
      const modalBody = container.querySelector('#modal-body') as HTMLElement;
      modalBody.innerHTML = `<img src="/assets/dome_information_panel.png" alt="Information" onerror="this.outerHTML='<p>Information panel image not available</p>'">`;
      modal.classList.add('active');
    });
  });

  // Input handlers
  const radiusInput = container.querySelector('#radius-input') as HTMLInputElement;
  const segmentsInput = container.querySelector('#segments-input') as HTMLInputElement;
  const exportBtn = container.querySelector('#export-svg') as HTMLButtonElement;

  const updatePattern = async () => {
    const r = parseFloat(radiusInput.value) || 5;
    const n = parseInt(segmentsInput.value) || 5;

    try {
      const traces = await generatePattern(r, n);
      plotTraces(traces, 'Pseudo-Dome Pattern');
      updatePseudoDomeParameters(r, n, container);
    } catch (err) {
      console.error('Error generating pattern:', err);
    }
  };

  radiusInput.addEventListener('input', updatePattern);
  segmentsInput.addEventListener('input', updatePattern);

  exportBtn.addEventListener('click', async () => {
    const r = parseFloat(radiusInput.value) || 5;
    const n = parseInt(segmentsInput.value) || 5;
    const svg = await createSvg(r, n);
    saveSvgToFile(svg, `pseudo_dome_r${r}_n${n}.svg`);
  });

  // Initial render
  updatePattern();
}

/**
 * Render Barrel Vault controls (single or double)
 */
function renderBarrelVaultControls(container: HTMLElement, isDouble: boolean): void {
  const controlsPanel = container.querySelector('#controls-panel') as HTMLElement;
  const title = isDouble ? 'Double Barrel Vault' : 'Single Barrel Vault';
  const helpImg = isDouble ? 'double_center_barrel_vault.png' : 'single_barrel_vault_information_panel.png';

  controlsPanel.innerHTML = `
    <div class="control-group">
      <div class="control-label">
        Radius (r):
        <button class="help-button" data-help="radius">?</button>
      </div>
      <input type="number" id="radius-input" value="2" min="1" step="0.1">
    </div>
    <div class="control-group">
      <div class="control-label">
        Segments (n):
        <button class="help-button" data-help="segments">?</button>
      </div>
      <input type="number" id="segments-input" value="6" min="3" max="20" step="1">
    </div>
    <div class="control-group">
      <div class="control-label">
        Tiles (m):
        <button class="help-button" data-help="tiles">?</button>
      </div>
      <input type="number" id="tiles-input" value="1" min="1" max="20" step="1">
    </div>
    <div class="control-group">
      <div class="control-label">
        Omega (°):
        <button class="help-button" data-help="omega">?</button>
      </div>
      <input type="number" id="omega-input" value="180" min="1" max="360" step="1">
    </div>
    ${isDouble ? `
    <div class="control-group">
      <div class="control-label">
        Distance (a):
        <button class="help-button" data-help="distance">?</button>
      </div>
      <input type="number" id="distance-input" value="1" min="0" step="0.01">
    </div>
    ` : `
    <div class="control-group">
      <div class="control-label">
        Height (h):
        <span id="height-label">(max: <span id="h-max">-</span>)</span>
        <button class="help-button" data-help="height">?</button>
      </div>
      <input type="number" id="height-input" value="1" min="0" step="0.001">
    </div>
    `}
    <div class="button-group">
      <button class="btn btn-primary" id="export-svg">Export SVG</button>
    </div>
  `;

  // Add help handlers
  container.querySelectorAll('.help-button').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = container.querySelector('#help-modal') as HTMLElement;
      const modalBody = container.querySelector('#modal-body') as HTMLElement;
      modalBody.innerHTML = `<img src="/assets/${helpImg}" alt="Information" onerror="this.outerHTML='<p>Information panel image not available</p>'">`;
      modal.classList.add('active');
    });
  });

  // Input handlers
  const radiusInput = container.querySelector('#radius-input') as HTMLInputElement;
  const segmentsInput = container.querySelector('#segments-input') as HTMLInputElement;
  const tilesInput = container.querySelector('#tiles-input') as HTMLInputElement;
  const omegaInput = container.querySelector('#omega-input') as HTMLInputElement;
  const exportBtn = container.querySelector('#export-svg') as HTMLButtonElement;

  const updatePattern = async () => {
    const r = parseFloat(radiusInput.value) || 2;
    const n = parseInt(segmentsInput.value) || 6;
    const m = parseInt(tilesInput.value) || 1;
    const omega = parseFloat(omegaInput.value) || 180;

    try {
      if (isDouble) {
        const distanceInput = container.querySelector('#distance-input') as HTMLInputElement;
        const a = parseFloat(distanceInput?.value) || 1;
        const traces = await generateDoubleBarrelVaultPattern(r, n, m, omega, a);
        plotTraces(traces, 'Double Barrel Vault Pattern');
        updateDoubleBarrelVaultParameters(r, n, m, omega, a, container);
      } else {
        const heightInput = container.querySelector('#height-input') as HTMLInputElement;
        const hMaxEl = container.querySelector('#h-max') as HTMLElement;

        const theta = calculateSegmentAngle(omega, n);
        const s = calculateSegmentLength(r, theta);
        const alpha = calculateFoldingAngle(theta);
        const hMax = calculateHeight(s, alpha);
        if (hMaxEl) hMaxEl.textContent = hMax.toFixed(2);

        let h = parseFloat(heightInput?.value) || 1;
        h = Math.min(Math.max(h, 0), hMax);
        if (heightInput && parseFloat(heightInput.value) > hMax) {
          heightInput.value = h.toString();
        }

        const traces = await generateBarrelVaultPattern(r, n, m, omega, h);
        plotTraces(traces, 'Barrel Vault Pattern');
        updateBarrelVaultParameters(r, n, m, omega, h, container);
      }
    } catch (err) {
      console.error('Error generating pattern:', err);
    }
  };

  [radiusInput, segmentsInput, tilesInput, omegaInput].forEach(el => {
    el?.addEventListener('input', updatePattern);
  });

  if (!isDouble) {
    const heightInput = container.querySelector('#height-input') as HTMLInputElement;
    heightInput?.addEventListener('input', updatePattern);
  } else {
    const distanceInput = container.querySelector('#distance-input') as HTMLInputElement;
    distanceInput?.addEventListener('input', updatePattern);
  }

  exportBtn.addEventListener('click', async () => {
    const r = parseFloat(radiusInput.value) || 2;
    const n = parseInt(segmentsInput.value) || 6;
    const m = parseInt(tilesInput.value) || 1;
    const omega = parseFloat(omegaInput.value) || 180;

    if (isDouble) {
      const distanceInput = container.querySelector('#distance-input') as HTMLInputElement;
      const a = parseFloat(distanceInput?.value) || 1;
      const svg = await createDoubleBarrelVaultSvg(r, n, m, omega, a);
      saveSvgToFile(svg, `double_barrel_vault_r${r}_n${n}_m${m}_o${omega}_a${a}.svg`);
    } else {
      const heightInput = container.querySelector('#height-input') as HTMLInputElement;
      const h = parseFloat(heightInput?.value) || 1;
      const svg = await createBarrelVaultSvg(r, n, m, omega, h);
      saveSvgToFile(svg, `barrel_vault_r${r}_n${n}_m${m}_o${omega}_h${h}.svg`);
    }
  });

  // Initial render
  updatePattern();
}

/**
 * Plot traces using Plotly
 */
function plotTraces(traces: ScatterTrace[], title: string): void {
  const plotContainer = document.getElementById('plot-container');
  if (!plotContainer) return;

  const plotlyTraces = traces.map(trace => ({
    x: trace.x,
    y: trace.y,
    mode: 'lines',
    line: {
      color: trace.line?.color || 'black',
      width: trace.line?.width || 1,
      dash: trace.line?.dash || 'solid'
    },
    type: 'scatter'
  }));

  const layout = {
    title,
    showlegend: false,
    hovermode: false,
    xaxis: { scaleanchor: 'y', scaleratio: 1 },
    margin: { l: 50, r: 50, t: 50, b: 50 }
  };

  // @ts-ignore
  Plotly.newPlot(plotContainer, plotlyTraces, layout, { responsive: true });
}

/**
 * Update pseudo-dome parameter display
 */
function updatePseudoDomeParameters(r: number, n: number, container: HTMLElement): void {
  const [thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha11, numRadialSegments] = calculateParameters(r, n);
  const display = container.querySelector('#parameter-display') as HTMLElement;

  const formatArr = (arr: number[], decimals = 2) => arr.map(v => v.toFixed(decimals)).join(', ');
  const formatArrDeg = (arr: number[], decimals = 2) => arr.map(v => (v * 180 / Math.PI).toFixed(decimals) + '°').join(', ');
  const formatTupleArr = (arr: [number, number][], decimals = 2) =>
    arr.map(v => `(${v.map(x => (x * 180 / Math.PI).toFixed(decimals)).join(', ')})`).join(', ');

  display.innerHTML = `
    <h3>Calculated Parameters</h3>
    <div class="parameter-section">
      <h4>Input Parameters</h4>
      <div class="parameter-row"><span class="parameter-label">Radius (r):</span><span class="parameter-value">${r.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">Segments (n):</span><span class="parameter-value">${n}</span></div>
    </div>
    <div class="parameter-section">
      <h4>Segment Angles (θ)</h4>
      <div class="parameter-value">${formatArrDeg(thetas)}</div>
    </div>
    <div class="parameter-section">
      <h4>Segment Lengths (s)</h4>
      <div class="parameter-value">${formatArr(s)}</div>
    </div>
    <div class="parameter-section">
      <h4>Folding Angles (α)</h4>
      <div class="parameter-value">${formatTupleArr(alpha)}</div>
    </div>
    <div class="parameter-section">
      <h4>Heights (h)</h4>
      <div class="parameter-value">${formatArr(h)}</div>
    </div>
    <div class="parameter-section">
      <h4>Properties</h4>
      <div class="parameter-row"><span class="parameter-label">Radial segments:</span><span class="parameter-value">${numRadialSegments}</span></div>
    </div>
  `;
}

/**
 * Update barrel vault parameter display
 */
function updateBarrelVaultParameters(r: number, n: number, m: number, omega: number, h: number, container: HTMLElement): void {
  const theta = calculateSegmentAngle(omega, n);
  const s = calculateSegmentLength(r, theta);
  const alpha = calculateFoldingAngle(theta);
  const hMax = calculateHeight(s, alpha);
  const totalWidth = n * s;
  const totalHeight = h * (2 * m - 1);

  const display = container.querySelector('#parameter-display') as HTMLElement;
  display.innerHTML = `
    <h3>Calculated Parameters</h3>
    <div class="parameter-section">
      <h4>Input Parameters</h4>
      <div class="parameter-row"><span class="parameter-label">Radius (r):</span><span class="parameter-value">${r.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">Segments (n):</span><span class="parameter-value">${n}</span></div>
      <div class="parameter-row"><span class="parameter-label">Tiles (m):</span><span class="parameter-value">${m}</span></div>
      <div class="parameter-row"><span class="parameter-label">Omega (Ω):</span><span class="parameter-value">${omega.toFixed(2)}°</span></div>
    </div>
    <div class="parameter-section">
      <h4>Calculated</h4>
      <div class="parameter-row"><span class="parameter-label">θ:</span><span class="parameter-value">${theta.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">s:</span><span class="parameter-value">${s.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">α:</span><span class="parameter-value">${alpha.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">h:</span><span class="parameter-value">${h.toFixed(2)} (max: ${hMax.toFixed(2)})</span></div>
    </div>
    <div class="parameter-section">
      <h4>Pattern Properties</h4>
      <div class="parameter-row"><span class="parameter-label">Total Width:</span><span class="parameter-value">${totalWidth.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">Total Height:</span><span class="parameter-value">${totalHeight.toFixed(2)}</span></div>
    </div>
  `;
}

/**
 * Update double barrel vault parameter display
 */
async function updateDoubleBarrelVaultParameters(r: number, n: number, m: number, omega: number, a: number, container: HTMLElement): Promise<void> {
  const { calculateAlpha1Angle, calculateAlpha2Angle, calculateBetaAngle } = await import('./utils/calculations');
  const theta = calculateSegmentAngle(omega, n);
  const s = calculateSegmentLength(r, theta);
  const alpha1 = calculateAlpha1Angle(a, r, n);
  const beta = calculateBetaAngle(a, r, n);
  const alpha2 = calculateAlpha2Angle(beta);
  const h = calculateHeight(s, alpha1);
  const totalWidth = n * s;
  const totalHeight = h * (2 * m - 1);

  const display = container.querySelector('#parameter-display') as HTMLElement;
  display.innerHTML = `
    <h3>Calculated Parameters</h3>
    <div class="parameter-section">
      <h4>Input Parameters</h4>
      <div class="parameter-row"><span class="parameter-label">Radius (r):</span><span class="parameter-value">${r.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">Segments (n):</span><span class="parameter-value">${n}</span></div>
      <div class="parameter-row"><span class="parameter-label">Tiles (m):</span><span class="parameter-value">${m}</span></div>
      <div class="parameter-row"><span class="parameter-label">Omega (Ω):</span><span class="parameter-value">${omega.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">Distance (a):</span><span class="parameter-value">${a.toFixed(2)}</span></div>
    </div>
    <div class="parameter-section">
      <h4>Calculated</h4>
      <div class="parameter-row"><span class="parameter-label">θ:</span><span class="parameter-value">${theta.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">s:</span><span class="parameter-value">${s.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">α1:</span><span class="parameter-value">${alpha1.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">α2:</span><span class="parameter-value">${alpha2.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">β:</span><span class="parameter-value">${beta.toFixed(2)}°</span></div>
      <div class="parameter-row"><span class="parameter-label">h:</span><span class="parameter-value">${h.toFixed(2)}</span></div>
    </div>
    <div class="parameter-section">
      <h4>Pattern Properties</h4>
      <div class="parameter-row"><span class="parameter-label">Total Width:</span><span class="parameter-value">${totalWidth.toFixed(2)}</span></div>
      <div class="parameter-row"><span class="parameter-label">Total Height:</span><span class="parameter-value">${totalHeight.toFixed(2)}</span></div>
    </div>
  `;
}
