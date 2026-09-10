/**
 * ==========================================================================================
 * ANTIGRAV RESEARCH AI // CLIENT CONTROLLER & TELEMETRY ENGINE
 * ==========================================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Engines
  const physics = new RelativisticPhysicsEngine();
  const visualizer = new SpacetimeVisualizer('sim-canvas');

  // Web Audio Context for Sci-Fi Feedback
  let audioCtx = null;
  let warpOscillator = null;
  let warpGain = null;
  let isAudioEnabled = false;

  function initAudio() {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Continuous subtle warp hum
        warpOscillator = audioCtx.createOscillator();
        warpGain = audioCtx.createGain();
        warpOscillator.type = 'sine';
        warpOscillator.frequency.setValueAtTime(55, audioCtx.currentTime);
        warpGain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        warpOscillator.connect(warpGain);
        warpGain.connect(audioCtx.destination);
        warpOscillator.start();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      isAudioEnabled = true;
    } catch (e) {
      console.warn('Audio not available or blocked', e);
    }
  }

  function playBeep(freq = 880, type = 'sine', duration = 0.08, gainVal = 0.08) {
    if (!isAudioEnabled || !audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (err) {}
  }

  function updateWarpAudioPitch(vs) {
    if (!isAudioEnabled || !warpOscillator || !warpGain) return;
    const targetFreq = 40 + vs * 35; // e.g., 2c => 110Hz
    warpOscillator.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.1);
    if (visualizer.mode === 'alcubierre') {
      warpGain.gain.setTargetAtTime(0.03, audioCtx.currentTime, 0.1);
    } else {
      warpGain.gain.setTargetAtTime(0.0001, audioCtx.currentTime, 0.1);
    }
  }

  // User gesture listener to unlock Web Audio
  document.body.addEventListener('click', () => {
    if (!audioCtx) initAudio();
  }, { once: true });

  // 2. Audio Toggle Button
  const audioToggleBtn = document.getElementById('audio-toggle-btn');
  if (audioToggleBtn) {
    audioToggleBtn.addEventListener('click', () => {
      initAudio();
      isAudioEnabled = !isAudioEnabled;
      audioToggleBtn.textContent = isAudioEnabled ? 'AUDIO: ACTIVE 🔊' : 'AUDIO: MUTED 🔇';
      if (!isAudioEnabled && warpGain) {
        warpGain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
      }
      playBeep(1200, 'triangle', 0.05);
    });
  }

  // 3. Tab Navigation
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add('active');

      playBeep(700, 'sine', 0.06);
    });
  });

  // 4. Viewport Mode Switcher (Alcubierre, Bondi, GEM, Casimir)
  const modeBtns = document.querySelectorAll('.mode-btn');
  const controlPanels = {
    alcubierre: document.getElementById('controls-alcubierre'),
    bondi: document.getElementById('controls-bondi'),
    gem: document.getElementById('controls-gem'),
    casimir: document.getElementById('controls-casimir')
  };

  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const mode = btn.getAttribute('data-mode');
      modeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      visualizer.setMode(mode);

      // Toggle visible controls
      Object.keys(controlPanels).forEach(key => {
        if (controlPanels[key]) {
          controlPanels[key].style.display = (key === mode) ? 'block' : 'none';
        }
      });

      updateTelemetry(mode);
      playBeep(900, 'square', 0.07, 0.04);
      if (mode === 'alcubierre') {
        updateWarpAudioPitch(visualizer.params.alcubierre.vs);
      } else if (warpGain && audioCtx) {
        warpGain.gain.setTargetAtTime(0.0001, audioCtx.currentTime, 0.1);
      }
    });
  });

  function updateTelemetry(mode) {
    const modeNameEl = document.getElementById('telemetry-mode-name');
    if (modeNameEl) modeNameEl.textContent = mode.toUpperCase();
  }

  // 5. Parameter Sliders & Dynamic Readouts
  // A. Alcubierre Controls
  const vsSlider = document.getElementById('slider-vs');
  const vsVal = document.getElementById('val-vs');
  const rSlider = document.getElementById('slider-r');
  const rVal = document.getElementById('val-r');
  const sigmaSlider = document.getElementById('slider-sigma');
  const sigmaVal = document.getElementById('val-sigma');
  const statWarpMass = document.getElementById('stat-warp-mass');
  const statWarpEnergy = document.getElementById('stat-warp-energy');

  function updateAlcubierreStats() {
    const vs = parseFloat(vsSlider.value);
    const R = parseFloat(rSlider.value);
    const sigma = parseFloat(sigmaSlider.value);

    visualizer.params.alcubierre.vs = vs;
    visualizer.params.alcubierre.R = R;
    visualizer.params.alcubierre.sigma = sigma;

    vsVal.textContent = `${vs.toFixed(1)} c`;
    rVal.textContent = `${R.toFixed(0)} m`;
    sigmaVal.textContent = sigma.toFixed(2);

    const massData = physics.calculateTotalWarpMassEnergy(vs, R, sigma);
    if (statWarpMass) {
      if (Math.abs(massData.mass_jupiter) >= 0.01) {
        statWarpMass.textContent = `${massData.mass_jupiter.toExponential(2)} M_Jupiter`;
      } else if (Math.abs(massData.mass_earth) >= 0.01) {
        statWarpMass.textContent = `${massData.mass_earth.toExponential(2)} M_Earth`;
      } else {
        statWarpMass.textContent = `${massData.mass_kg.toExponential(2)} kg`;
      }
    }
    if (statWarpEnergy) {
      statWarpEnergy.textContent = `${massData.energy_joules.toExponential(2)} J`;
    }

    updateWarpAudioPitch(vs);
  }

  if (vsSlider) vsSlider.addEventListener('input', updateAlcubierreStats);
  if (rSlider) rSlider.addEventListener('input', updateAlcubierreStats);
  if (sigmaSlider) sigmaSlider.addEventListener('input', updateAlcubierreStats);

  // B. Bondi Dipole Controls
  const m1Slider = document.getElementById('slider-m1');
  const m1Val = document.getElementById('val-m1');
  const m2Slider = document.getElementById('slider-m2');
  const m2Val = document.getElementById('val-m2');
  const btnResetBondi = document.getElementById('btn-reset-bondi');

  function updateBondiParams() {
    const m1 = parseFloat(m1Slider.value);
    const m2 = parseFloat(m2Slider.value);
    visualizer.params.bondi.m1 = m1;
    visualizer.params.bondi.m2 = m2;
    if (visualizer.bondiState) {
      visualizer.bondiState.m1 = m1;
      visualizer.bondiState.m2 = -m2;
    }
    m1Val.textContent = `+${m1.toFixed(1)} kg`;
    m2Val.textContent = `-${m2.toFixed(1)} kg`;
  }

  if (m1Slider) m1Slider.addEventListener('input', updateBondiParams);
  if (m2Slider) m2Slider.addEventListener('input', updateBondiParams);
  if (btnResetBondi) {
    btnResetBondi.addEventListener('click', () => {
      visualizer.resetBondi();
      playBeep(600, 'square', 0.1);
    });
  }

  // C. GEM Controls
  const jSlider = document.getElementById('slider-gem-j');
  const jVal = document.getElementById('val-gem-j');
  const statGemBg = document.getElementById('stat-gem-bg');
  const statGemDensity = document.getElementById('stat-gem-density');

  function updateGEMParams() {
    const J = parseFloat(jSlider.value);
    visualizer.params.gem.J = J;
    jVal.textContent = `${J.toFixed(0)} × 10²⁵ J·s`;

    const bgField = physics.calculateGravitomagneticField(J * 1e25, 5.0);
    const required = physics.calculateRequiredGEMDensity(30.0, 9.81);

    if (statGemBg) statGemBg.textContent = `${bgField.toExponential(2)} s⁻¹`;
    if (statGemDensity) statGemDensity.textContent = `${(required.required_J_density).toExponential(2)} J·s/m³`;
  }

  if (jSlider) jSlider.addEventListener('input', updateGEMParams);

  // D. Casimir Controls
  const gapSlider = document.getElementById('slider-casimir-d');
  const gapVal = document.getElementById('val-casimir-d');
  const statCasimirPressure = document.getElementById('stat-casimir-pressure');
  const statCasimirTau = document.getElementById('stat-casimir-tau');

  function updateCasimirParams() {
    const d_nm = parseFloat(gapSlider.value);
    visualizer.params.casimir.gapDistance = d_nm;
    gapVal.textContent = `${d_nm.toFixed(0)} nm`;

    const res = physics.calculateCasimirPressure(d_nm * 1e-9);
    const tau = physics.calculateFordRomanLimit(res.energyDensity_J_m3);

    if (statCasimirPressure) statCasimirPressure.textContent = `${Math.abs(res.pressure_Pa).toExponential(2)} Pa`;
    if (statCasimirTau) statCasimirTau.textContent = `${tau.toExponential(2)} s (QEI Limit)`;
  }

  if (gapSlider) gapSlider.addEventListener('input', updateCasimirParams);

  // 6. Diagnostic Energy Conditions Engine
  const inputRho = document.getElementById('diag-rho');
  const inputPx = document.getElementById('diag-px');
  const inputPy = document.getElementById('diag-py');
  const inputPz = document.getElementById('diag-pz');
  const btnRunDiag = document.getElementById('btn-run-diag');

  function runDiagnostics() {
    const rho = parseFloat(inputRho.value) || 0;
    const px = parseFloat(inputPx.value) || 0;
    const py = parseFloat(inputPy.value) || 0;
    const pz = parseFloat(inputPz.value) || 0;

    const result = physics.validateEnergyConditions(rho, px, py, pz);

    ['NEC', 'WEC', 'SEC', 'DEC'].forEach(key => {
      const card = document.getElementById(`card-${key.toLowerCase()}`);
      const tag = document.getElementById(`tag-${key.toLowerCase()}`);
      const details = document.getElementById(`details-${key.toLowerCase()}`);

      if (card && tag && details) {
        const satisfied = result[key].satisfied;
        card.className = `condition-card ${satisfied ? 'satisfied' : 'violated'}`;
        tag.className = `status-tag ${satisfied ? 'satisfied' : 'violated'}`;
        tag.textContent = satisfied ? 'SATISFIED' : 'VIOLATED';
        details.textContent = result[key].details;
      }
    });

    playBeep(result.NEC.satisfied ? 1000 : 400, 'sawtooth', 0.1);
  }

  if (btnRunDiag) btnRunDiag.addEventListener('click', runDiagnostics);

  // Preset buttons for Stress-Energy Tensor
  const btnPresetVacuum = document.getElementById('preset-vacuum');
  const btnPresetWarp = document.getElementById('preset-warp');
  const btnPresetDust = document.getElementById('preset-dust');
  const btnPresetCasimir = document.getElementById('preset-casimir');

  if (btnPresetVacuum) {
    btnPresetVacuum.addEventListener('click', () => {
      inputRho.value = 0; inputPx.value = 0; inputPy.value = 0; inputPz.value = 0;
      runDiagnostics();
    });
  }
  if (btnPresetWarp) {
    btnPresetWarp.addEventListener('click', () => {
      inputRho.value = -1e20; inputPx.value = 5e19; inputPy.value = 5e19; inputPz.value = 5e19;
      runDiagnostics();
    });
  }
  if (btnPresetDust) {
    btnPresetDust.addEventListener('click', () => {
      inputRho.value = 1e12; inputPx.value = 0; inputPy.value = 0; inputPz.value = 0;
      runDiagnostics();
    });
  }
  if (btnPresetCasimir) {
    btnPresetCasimir.addEventListener('click', () => {
      inputRho.value = -1300; inputPx.value = 1300; inputPy.value = 1300; inputPz.value = -3900;
      runDiagnostics();
    });
  }

  // 7. Interactive Terminal Engine
  const termBody = document.getElementById('terminal-body');
  const termInput = document.getElementById('terminal-input');

  function appendTermLine(html, type = 'out') {
    if (!termBody) return;
    const line = document.createElement('div');
    line.className = `terminal-line t-${type}`;
    line.innerHTML = html;
    termBody.appendChild(line);
    termBody.scrollTop = termBody.scrollHeight;
  }

  function handleTermCommand(rawCmd) {
    const cmd = rawCmd.trim();
    if (!cmd) return;

    appendTermLine(`<span class="t-prompt">RESEARCH_AI &gt;</span> ${cmd}`, 'out');
    const parts = cmd.split(' ');
    const mainCmd = parts[0].toLowerCase();

    switch (mainCmd) {
      case 'help':
        appendTermLine(`<b>AVAILABLE COMMANDS:</b><br>
  - <b>eval [alcubierre|bondi|gem|casimir|majorana]</b> : Execute rigorous GR/QFT tensor evaluation<br>
  - <b>tensor &lt;rho&gt; &lt;px&gt; &lt;py&gt; &lt;pz&gt;</b> : Test arbitrary T_μν against Energy Conditions<br>
  - <b>qei &lt;negative_density&gt;</b> : Calculate Ford-Roman quantum inequality lifetime bound<br>
  - <b>warp &lt;vs/c&gt; &lt;R_meters&gt;</b> : Calculate integrated mass-energy requirement<br>
  - <b>export</b> : Export formal peer-reviewed evaluation report as Markdown<br>
  - <b>status</b> : Display air-gapped system telemetry & clearance level<br>
  - <b>clear</b> : Clear terminal buffer`, 'sys');
        break;

      case 'eval':
        const target = parts[1] ? parts[1].toLowerCase() : 'alcubierre';
        if (target === 'alcubierre') {
          appendTermLine(`[EVALUATION: ALCUBIERRE WARP METRIC]<br>
• Metric: ds² = -c²dt² + [dx - v_s f(r_s) dt]² + dy² + dz²<br>
• Energy Conditions: <b>NEC VIOLATED, WEC VIOLATED</b> (Eulerian ρ_eff &lt; 0)<br>
• Semiclassical Hazard: Cauchy horizon vacuum polarization divergence (Hawking radiation backreaction)<br>
• Theoretical Feasibility: <b>1/10</b> | TRL: <b>1</b>`, 'err');
        } else if (target === 'bondi') {
          appendTermLine(`[EVALUATION: BONDI NEGATIVE MASS DIPOLE]<br>
• Principle: m_i = m_p = m_a = -m (Strong Equivalence Principle assumed)<br>
• Mechanics: +m is repelled by -m; -m is attracted to +m → Runaway Acceleration<br>
• Conserved Quantities: Net Momentum P = 0, Net Energy E = 0<br>
• Fatal Barrier: Unbounded vacuum state instability (infinite pair creation)<br>
• Theoretical Feasibility: <b>1/10</b> | TRL: <b>0</b>`, 'err');
        } else if (target === 'gem') {
          appendTermLine(`[EVALUATION: GRAVITOMAGNETIC LENSE-THIRRING EFFECT]<br>
• Formulation: Linearized GR: ∇ × B_g = - (16πG/c²) j_m + (1/c) ∂E_g/∂t<br>
• Energy Conditions: <b>SATISFIED (NEC, WEC, SEC, DEC all valid)</b><br>
• Engineering Bottleneck: G/c² coupling requires J/V ~ 10²⁵ J·s/m³ (Neutron star density) to cancel 1g<br>
• Theoretical Feasibility: <b>3/10</b> (Valid Physics, Extreme Engineering) | TRL: <b>1</b>`, 'sys');
        } else if (target === 'casimir') {
          appendTermLine(`[EVALUATION: DYNAMIC CASIMIR QUANTUM VACUUM]<br>
• Formulation: T_00 = - (π² ħ c) / (720 d⁴)<br>
• Constraints: Ford-Roman Bound enforces ∫⟨T_00⟩ dt ≥ - 3ħ / (32π² c³ τ₀⁴)<br>
• Macro-thrust Viability: <b>Zero Net Macroscopic Propulsion</b> (Bounded by compensating positive energy flux)<br>
• Theoretical Feasibility: <b>2/10</b> | TRL: <b>2</b>`, 'sys');
        } else if (target === 'majorana') {
          appendTermLine(`[EVALUATION: MAJORANA GRAVITATIONAL SHIELDING]<br>
• Hypothesis: F = G₀ (1 - h ∫ρ dr) m₁m₂/r²<br>
• Empirical Status: <b>EXPERIMENTALLY FALSIFIED</b> (Lunar Laser Ranging: h ≤ 10⁻¹⁶ m²/kg)<br>
• Theoretical Feasibility: <b>0/10</b> | TRL: <b>0</b>`, 'err');
        } else {
          appendTermLine(`Unknown mechanism '${target}'. Choose alcubierre, bondi, gem, casimir, or majorana.`, 'err');
        }
        break;

      case 'tensor':
        const rho = parseFloat(parts[1]) || 0;
        const px = parseFloat(parts[2]) || 0;
        const py = parseFloat(parts[3]) || 0;
        const pz = parseFloat(parts[4]) || 0;
        const diag = physics.validateEnergyConditions(rho, px, py, pz);
        appendTermLine(`[TENSOR DIAGNOSTIC RESULT]<br>
• NEC: ${diag.NEC.satisfied ? '<span class="t-success">PASS</span>' : '<span class="t-err">FAIL</span>'} (${diag.NEC.details})<br>
• WEC: ${diag.WEC.satisfied ? '<span class="t-success">PASS</span>' : '<span class="t-err">FAIL</span>'}<br>
• SEC: ${diag.SEC.satisfied ? '<span class="t-success">PASS</span>' : '<span class="t-err">FAIL</span>'}<br>
• DEC: ${diag.DEC.satisfied ? '<span class="t-success">PASS</span>' : '<span class="t-err">FAIL</span>'}`, 'sys');
        break;

      case 'qei':
        const rho_neg = parseFloat(parts[1]) || -1e10;
        const tau_limit = physics.calculateFordRomanLimit(rho_neg);
        appendTermLine(`[FORD-ROMAN BOUND EVALUATION]<br>
• Negative Energy Density: ${Math.abs(rho_neg).toExponential(3)} J/m³<br>
• Maximum Allowed Existence Duration τ₀: <b>${tau_limit.toExponential(3)} seconds</b><br>
• Spatial Persistence Limit: Δx ≤ c·τ₀ = <b>${(physics.constants.c * tau_limit).toExponential(3)} meters</b>`, 'sys');
        break;

      case 'warp':
        const vs_w = parseFloat(parts[1]) || 1.0;
        const r_w = parseFloat(parts[2]) || 50.0;
        const w_mass = physics.calculateTotalWarpMassEnergy(vs_w, r_w, 0.05);
        appendTermLine(`[WARP METRIC MASS-ENERGY SCALING]<br>
• Apparent Velocity: ${vs_w} c<br>
• Bubble Radius: ${r_w} m<br>
• Required Negative Mass: <b>${w_mass.mass_kg.toExponential(2)} kg</b> (${w_mass.mass_jupiter.toExponential(2)} Jupiter Masses)<br>
• Required Energy Equivalent: <b>${w_mass.energy_joules.toExponential(2)} J</b>`, 'sys');
        break;

      case 'export':
        triggerReportDownload();
        appendTermLine(`Report exported successfully as Markdown document.`, 't-success');
        break;

      case 'status':
        appendTermLine(`[AIR-GAPPED AI TELEMETRY]<br>
• CLEARANCE: RESEARCH_LEAD (LEVEL-5)<br>
• EFE TENSOR ENGINE: ACTIVE (ADM 3+1)<br>
• SEMICLASSICAL QFT CONSTRAINTS: ENFORCED<br>
• SIMULATION STATUS: 60 FPS NOMINAL`, 't-success');
        break;

      case 'clear':
        termBody.innerHTML = '';
        break;

      default:
        appendTermLine(`Command not recognized: '${cmd}'. Type <b>help</b> for command list.`, 'err');
        break;
    }
  }

  if (termInput) {
    termInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = termInput.value;
        termInput.value = '';
        handleTermCommand(val);
      }
    });
  }

  // 8. Markdown Report Export
  function triggerReportDownload() {
    const reportText = `# TECHNICAL REPORT: QUANTUM-RELATIVISTIC EVALUATION OF FIELD-PROPULSION
**Clearance:** RESEARCH_LEAD // LEVEL-5 AIR-GAPPED
**Generated At:** ${new Date().toISOString()}

## 1. Executive Summary
Evaluation of speculative metric propulsion ("Antigravity") mechanisms under exact Einstein Field Equations ($G_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}$) and Semiclassical Quantum Field Theory.

## 2. Synthesis Matrix
| Mechanism | Physics Paradigm | Governing Metric / Equation | Energy Conditions | Feasibility | TRL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Gravitomagnetism | Linearized GR | ∇ × B_g = - (16πG/c²) j_m | Satisfies All | 3 / 10 | 1 |
| Alcubierre Warp | Exact GR Metric | ds² = -c²dt² + [dx - v_s f dt]² + dy² + dz² | Violates NEC/WEC/SEC/DEC | 1 / 10 | 1 |
| Bondi Dipole | GR Negative Mass | m_i = m_p = m_a < 0 | Violates DEC/WEC | 1 / 10 | 0 |
| Dynamic Casimir | Quantum Field Theory | T_00 = -π²ħc / (720 d⁴) | Bounded by QEI | 2 / 10 | 2 |
| Majorana Shielding | Disproven | F = G₀ (1 - h ∫ρ dr) | Excluded (h ≤ 10⁻¹⁶) | 0 / 10 | 0 |

## 3. Fundamental Physics Bottlenecks
1. Quantum Energy Inequalities (Ford-Roman Bounds): Enforces strict temporal decay on negative energy densities.
2. Trans-Planckian Energy-Mass Scaling: Inverse Einstein constant requires planetary-scale negative mass-energies.
3. Cauchy Horizon Divergence: Quantum vacuum backreaction destabilizes warp envelopes before functional velocities are reached.
`;
    const blob = new Blob([reportText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ANTIGRAV_TECHNICAL_EVALUATION_REPORT.md';
    a.click();
    URL.revokeObjectURL(url);
  }

  const exportBtn = document.getElementById('export-report-btn');
  if (exportBtn) exportBtn.addEventListener('click', triggerReportDownload);

  // 9. Synthesis Matrix Filter
  const matrixFilterBtns = document.querySelectorAll('.matrix-filter-btn');
  const matrixRows = document.querySelectorAll('.matrix-row');

  matrixFilterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.getAttribute('data-filter');
      matrixFilterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      matrixRows.forEach(row => {
        if (filter === 'all' || row.classList.contains(`cat-${filter}`)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
      playBeep(850, 'sine', 0.05);
    });
  });

  // Initial updates
  updateAlcubierreStats();
  updateBondiParams();
  updateGEMParams();
  updateCasimirParams();
  runDiagnostics();

  // Animation Loop for 3D Visualizer
  let lastTime = performance.now();
  function loop(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;
    visualizer.render(dt);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
});
