/**
 * ==========================================================================================
 * ANTIGRAV RESEARCH AI // 3D SPACETIME & QUANTUM VACUUM VISUALIZATION ENGINE
 * High-performance 3D Canvas / WebGL Simulation Renderer with Full Camera Controls
 * ==========================================================================================
 */

class SpacetimeVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) throw new Error(`Canvas #${canvasId} not found`);
    this.ctx = this.canvas.getContext('2d');

    this.engine = new RelativisticPhysicsEngine();
    this.mode = 'alcubierre'; // 'alcubierre' | 'bondi' | 'gem' | 'casimir'
    
    // Camera & Projection State
    this.camera = {
      rotX: 0.65,       // Elevation pitch
      rotY: -0.75,      // Azimuth yaw
      zoom: 1.0,
      panX: 0,
      panY: 0,
      dist: 550
    };

    // User Interaction State
    this.isDragging = false;
    this.isPanning = false;
    this.lastMouse = { x: 0, y: 0 };

    // Simulation Parameters
    this.params = {
      alcubierre: {
        vs: 2.0,         // v_s / c (multiples of lightspeed)
        R: 45.0,         // Radius (grid units)
        sigma: 0.08,     // Wall steepness
        gridSize: 32,    // Grid resolution (NxN)
        spacing: 12,     // Distance between grid vertices
        showVectorField: true,
        showEnergyDensity: true,
        showShip: true,
        animateFlow: true
      },
      bondi: {
        m1: 1.0,         // Positive mass (+m)
        m2: -1.0,        // Negative mass (-m)
        separation: 120, // Initial separation distance
        G_eff: 2500,     // Scaled G for smooth visual frame
        trailLength: 120,
        running: true
      },
      gem: {
        J: 50.0,         // Angular momentum parameter
        v_test: 30.0,    // Test particle speed
        cylinderRadius: 40,
        numParticles: 150,
        precessionSpeed: 1.0
      },
      casimir: {
        gapDistance: 35, // Distance between plates
        vibrate: true,
        frequency: 2.5,
        numVacuumModes: 40
      }
    };

    // Simulation Dynamic States
    this.simTime = 0;
    this.particles = [];
    this.bondiState = null;
    this.bondiTrails = { p1: [], p2: [] };
    this.gemParticles = [];
    this.flowFieldParticles = [];

    this.initEventListeners();
    this.initSimulationData();
    this.resize();

    // Auto resize handling
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height || 540;

    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.canvas.style.width = `${this.width}px`;
    this.canvas.style.height = `${this.height}px`;
    
    this.ctx.scale(dpr, dpr);
  }

  initEventListeners() {
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.isPanning = e.button === 2 || e.shiftKey;
      this.lastMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      const dx = e.clientX - this.lastMouse.x;
      const dy = e.clientY - this.lastMouse.y;

      if (this.isPanning) {
        this.camera.panX += dx;
        this.camera.panY += dy;
      } else {
        this.camera.rotY += dx * 0.008;
        this.camera.rotX = Math.max(-1.4, Math.min(1.4, this.camera.rotX + dy * 0.008));
      }

      this.lastMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
      this.isPanning = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.camera.zoom = Math.max(0.3, Math.min(3.5, this.camera.zoom * zoomFactor));
    }, { passive: false });

    // Prevent context menu on right click for panning
    this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  setMode(newMode) {
    if (['alcubierre', 'bondi', 'gem', 'casimir'].includes(newMode)) {
      this.mode = newMode;
      this.initSimulationData();
    }
  }

  initSimulationData() {
    this.simTime = 0;

    // 1. Alcubierre flow field particles
    this.flowFieldParticles = [];
    for (let i = 0; i < 200; i++) {
      this.flowFieldParticles.push({
        x: (Math.random() - 0.5) * 360,
        y: (Math.random() - 0.5) * 80,
        z: (Math.random() - 0.5) * 360,
        speed: 1 + Math.random() * 2,
        life: Math.random()
      });
    }

    // 2. Bondi Initial State
    this.bondiState = {
      x1: -this.params.bondi.separation / 2,
      y1: 0,
      vx1: 0,
      vy1: 0,
      m1: Math.abs(this.params.bondi.m1),
      x2: this.params.bondi.separation / 2,
      y2: 0,
      vx2: 0,
      vy2: 0,
      m2: -Math.abs(this.params.bondi.m2)
    };
    this.bondiTrails = { p1: [], p2: [] };

    // 3. GEM Particles
    this.gemParticles = [];
    for (let i = 0; i < this.params.gem.numParticles; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = 60 + Math.random() * 120;
      this.gemParticles.push({
        angle,
        radius,
        z: (Math.random() - 0.5) * 160,
        speed: 0.01 + Math.random() * 0.03,
        color: `hsl(${180 + Math.random() * 60}, 100%, 70%)`
      });
    }
  }

  resetBondi() {
    this.initSimulationData();
  }

  // ========================================================================================
  // 3D PROJECTION & TRANSFORMATION UTILS
  // ========================================================================================
  
  project(x, y, z) {
    // 1. Rotation around Y-axis (Yaw)
    const cosY = Math.cos(this.camera.rotY);
    const sinY = Math.sin(this.camera.rotY);
    const x1 = x * cosY - z * sinY;
    const z1 = x * sinY + z * cosY;

    // 2. Rotation around X-axis (Pitch)
    const cosX = Math.cos(this.camera.rotX);
    const sinX = Math.sin(this.camera.rotX);
    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;

    // 3. Perspective Projection
    const fov = 600 * this.camera.zoom;
    const depth = z2 + this.camera.dist;
    if (depth < 10) return null; // Behind camera

    const scale = fov / depth;
    const projX = (this.width / 2) + this.camera.panX + x1 * scale;
    const projY = (this.height / 2) + this.camera.panY + y2 * scale;

    return { x: projX, y: projY, zIndex: depth, scale };
  }

  // ========================================================================================
  // RENDER MODES
  // ========================================================================================
  
  render(dt = 0.016) {
    this.simTime += dt;
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Background Space Grid & Ambient Glow
    this.renderStarfieldBackdrop();

    switch (this.mode) {
      case 'alcubierre':
        this.renderAlcubierreMetric(dt);
        break;
      case 'bondi':
        this.renderBondiDipole(dt);
        break;
      case 'gem':
        this.renderGEMFrameDragging(dt);
        break;
      case 'casimir':
        this.renderCasimirCavity(dt);
        break;
    }

    this.renderHUDOverlay();
  }

  renderStarfieldBackdrop() {
    // Sci-fi deep background with subtle radial grid
    const gradient = this.ctx.createRadialGradient(
      this.width / 2, this.height / 2, 50,
      this.width / 2, this.height / 2, Math.max(this.width, this.height) * 0.8
    );
    gradient.addColorStop(0, '#0d1322');
    gradient.addColorStop(0.6, '#080b12');
    gradient.addColorStop(1, '#030508');

    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.width, this.height);

    // Subtle coordinate rings in center
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.04)';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.arc(this.width / 2 + this.camera.panX, this.height / 2 + this.camera.panY, 120 * this.camera.zoom, 0, Math.PI * 2);
    this.ctx.arc(this.width / 2 + this.camera.panX, this.height / 2 + this.camera.panY, 240 * this.camera.zoom, 0, Math.PI * 2);
    this.ctx.stroke();
    this.ctx.restore();
  }

  // ----------------------------------------------------------------------------------------
  // 1. ALCUBIERRE WARP METRIC RENDERER
  // ----------------------------------------------------------------------------------------
  renderAlcubierreMetric(dt) {
    const p = this.params.alcubierre;
    const N = p.gridSize;
    const spacing = p.spacing;
    const half = (N * spacing) / 2;

    // Calculate dynamic 3D heightmap for spacetime curvature
    // Height y = - expansion_scalar * scale
    const grid = [];
    for (let i = 0; i <= N; i++) {
      grid[i] = [];
      const z = i * spacing - half;
      for (let j = 0; j <= N; j++) {
        const x = j * spacing - half;
        const r = Math.sqrt(x * x + z * z);
        
        // Alcubierre Expansion Scalar theta = -vs (x/r) df/dr
        const df_dr = this.engine.alcubierreShapingDerivative(r, p.R, p.sigma);
        const theta = (r > 1e-3) ? - (p.vs) * (x / r) * df_dr : 0;
        
        // Height deflection in 3D visualization:
        // Forward (x > 0): theta < 0 -> Space contracts (depression/well)
        // Backward (x < 0): theta > 0 -> Space expands (elevation/crest)
        const y = theta * 65.0; 

        // Energy density rho_eff
        const rho_eff = - Math.pow(p.vs, 2) * (z * z / (r * r + 1)) * Math.pow(df_dr, 2) * 500;

        grid[i][j] = {
          x, y, z,
          theta,
          rho_eff,
          proj: this.project(x, y, z)
        };
      }
    }

    // 1. Draw Quads / Mesh lines with depth sorting
    this.ctx.save();
    this.ctx.lineWidth = 1.2;

    // Draw Grid Lines in X and Z directions
    for (let i = 0; i <= N; i++) {
      for (let j = 0; j <= N; j++) {
        const pt = grid[i][j];
        if (!pt.proj) continue;

        // Line to next J (X direction)
        if (j < N && grid[i][j + 1].proj) {
          const ptNext = grid[i][j + 1];
          const avgTheta = (pt.theta + ptNext.theta) / 2;
          
          this.ctx.strokeStyle = this.getWarpColor(avgTheta, pt.rho_eff);
          this.ctx.beginPath();
          this.ctx.moveTo(pt.proj.x, pt.proj.y);
          this.ctx.lineTo(ptNext.proj.x, ptNext.proj.y);
          this.ctx.stroke();
        }

        // Line to next I (Z direction)
        if (i < N && grid[i + 1][j].proj) {
          const ptNext = grid[i + 1][j];
          const avgTheta = (pt.theta + ptNext.theta) / 2;

          this.ctx.strokeStyle = this.getWarpColor(avgTheta, pt.rho_eff);
          this.ctx.beginPath();
          this.ctx.moveTo(pt.proj.x, pt.proj.y);
          this.ctx.lineTo(ptNext.proj.x, ptNext.proj.y);
          this.ctx.stroke();
        }
      }
    }

    // 2. Render Warp Envelope Horizon Rings (Bubble boundary r = R)
    this.renderWarpBubbleBoundary(p.R, p.sigma);

    // 3. Render Geodesic Flow Vector Particles
    if (p.animateFlow) {
      this.renderAlcubierreFlowParticles(p, dt);
    }

    // 4. Render Payload Capsule in Flat Center (r < R, g_uv = eta_uv)
    if (p.showShip) {
      this.renderPayloadShip();
    }

    this.ctx.restore();
  }

  getWarpColor(theta, rho_eff) {
    if (Math.abs(theta) < 0.005) {
      return 'rgba(0, 180, 255, 0.25)'; // Flat undisturbed spacetime
    } else if (theta < 0) {
      // Contraction ahead (Cyan / Blue Shift)
      const intensity = Math.min(1.0, Math.abs(theta) * 1.5);
      return `rgba(0, 240, 255, ${0.3 + intensity * 0.7})`;
    } else {
      // Expansion behind (Magenta / Amber Red Shift)
      const intensity = Math.min(1.0, theta * 1.5);
      return `rgba(255, 0, 110, ${0.3 + intensity * 0.7})`;
    }
  }

  renderWarpBubbleBoundary(R, sigma) {
    const numPoints = 64;
    const ringPts = [];
    for (let i = 0; i < numPoints; i++) {
      const angle = (i / numPoints) * Math.PI * 2;
      const x = Math.cos(angle) * R;
      const z = Math.sin(angle) * R;
      const proj = this.project(x, 0, z);
      if (proj) ringPts.push(proj);
    }

    if (ringPts.length > 2) {
      this.ctx.save();
      this.ctx.strokeStyle = 'rgba(255, 230, 0, 0.8)';
      this.ctx.lineWidth = 2.0;
      this.ctx.setLineDash([4, 4]);
      this.ctx.beginPath();
      this.ctx.moveTo(ringPts[0].x, ringPts[0].y);
      for (let i = 1; i < ringPts.length; i++) {
        this.ctx.lineTo(ringPts[i].x, ringPts[i].y);
      }
      this.ctx.closePath();
      this.ctx.stroke();

      // Label
      const topPt = this.project(0, -15, -R);
      if (topPt) {
        this.ctx.fillStyle = '#ffe600';
        this.ctx.font = '10px "Space Grotesk", sans-serif';
        this.ctx.fillText(`WARP HORIZON (R = ${R.toFixed(0)}m)`, topPt.x - 50, topPt.y - 8);
      }
      this.ctx.restore();
    }
  }

  renderAlcubierreFlowParticles(p, dt) {
    this.ctx.save();
    for (let pt of this.flowFieldParticles) {
      // Particles stream from front (x > 0) towards back (x < 0)
      pt.x -= pt.speed * p.vs * 40 * dt;
      if (pt.x < -180) {
        pt.x = 180;
        pt.z = (Math.random() - 0.5) * 360;
      }

      const r = Math.sqrt(pt.x * pt.x + pt.z * pt.z);
      const df_dr = this.engine.alcubierreShapingDerivative(r, p.R, p.sigma);
      const theta = (r > 1e-3) ? - (p.vs) * (pt.x / r) * df_dr : 0;
      const y = theta * 65.0;

      const proj = this.project(pt.x, y - 5, pt.z);
      if (proj) {
        const glow = (pt.x > 0) ? 'rgba(0, 240, 255, 0.8)' : 'rgba(255, 0, 110, 0.8)';
        this.ctx.fillStyle = glow;
        this.ctx.beginPath();
        this.ctx.arc(proj.x, proj.y, Math.max(1, 2.5 * proj.scale), 0, Math.PI * 2);
        this.ctx.fill();
      }
    }
    this.ctx.restore();
  }

  renderPayloadShip() {
    const origin = this.project(0, 0, 0);
    if (!origin) return;

    this.ctx.save();
    // Payload vessel indicator
    const size = 12 * origin.scale;
    this.ctx.fillStyle = '#00ff9d';
    this.ctx.shadowColor = '#00ff9d';
    this.ctx.shadowBlur = 15;

    this.ctx.beginPath();
    this.ctx.arc(origin.x, origin.y, size, 0, Math.PI * 2);
    this.ctx.fill();

    // Zero-g flat spacetime label
    this.ctx.fillStyle = '#00ff9d';
    this.ctx.font = '11px "Space Grotesk", monospace';
    this.ctx.fillText("PAYLOAD (ZERO PROPER G: a_local = 0)", origin.x + 18, origin.y - 12);

    this.ctx.restore();
  }

  // ----------------------------------------------------------------------------------------
  // 2. BONDI NEGATIVE MASS DIPOLE RENDERER
  // ----------------------------------------------------------------------------------------
  renderBondiDipole(dt) {
    const p = this.params.bondi;
    
    if (p.running && this.bondiState) {
      // Step the Runge Kutta 4 physics
      const result = this.engine.stepBondiDipoleRK4(this.bondiState, dt * 1.5, p.G_eff);
      this.bondiState = result.nextState;

      // Keep within bounds or wrap around
      if (this.bondiState.x1 > 350) {
        const offset = this.bondiState.x1 + 350;
        this.bondiState.x1 -= offset;
        this.bondiState.x2 -= offset;
        this.bondiTrails.p1 = [];
        this.bondiTrails.p2 = [];
      }

      // Record trails
      this.bondiTrails.p1.push({ x: this.bondiState.x1, y: this.bondiState.y1 });
      this.bondiTrails.p2.push({ x: this.bondiState.x2, y: this.bondiState.y2 });
      if (this.bondiTrails.p1.length > p.trailLength) this.bondiTrails.p1.shift();
      if (this.bondiTrails.p2.length > p.trailLength) this.bondiTrails.p2.shift();
    }

    const s = this.bondiState;
    if (!s) return;

    // 1. Draw Reference Baseline Grid
    this.renderFlatGrid2D();

    // 2. Render Trajectory Trails
    this.renderTrails(this.bondiTrails.p1, 'rgba(0, 180, 255, 0.6)');
    this.renderTrails(this.bondiTrails.p2, 'rgba(255, 40, 40, 0.6)');

    // 3. Render Pos Mass (+m1)
    const p1Proj = this.project(s.x1, 0, s.y1);
    if (p1Proj) {
      this.ctx.save();
      this.ctx.fillStyle = '#00e5ff';
      this.ctx.shadowColor = '#00e5ff';
      this.ctx.shadowBlur = 20;
      this.ctx.beginPath();
      this.ctx.arc(p1Proj.x, p1Proj.y, 14 * p1Proj.scale, 0, Math.PI * 2);
      this.ctx.fill();

      // Velocity Vector Arrow
      this.renderVectorArrow(p1Proj, s.vx1 * 0.4, s.vy1 * 0.4, '#00e5ff', `v+ = ${Math.hypot(s.vx1, s.vy1).toFixed(1)} c`);

      this.ctx.fillStyle = '#ffffff';
      this.ctx.font = '12px "Space Grotesk", sans-serif';
      this.ctx.fillText(`+m (Positive Mass: ${s.m1.toFixed(1)} kg)`, p1Proj.x - 40, p1Proj.y - 25);
      this.ctx.restore();
    }

    // 4. Render Neg Mass (-m2)
    const p2Proj = this.project(s.x2, 0, s.y2);
    if (p2Proj) {
      this.ctx.save();
      this.ctx.fillStyle = '#ff0055';
      this.ctx.shadowColor = '#ff0055';
      this.ctx.shadowBlur = 20;
      this.ctx.beginPath();
      this.ctx.arc(p2Proj.x, p2Proj.y, 14 * p2Proj.scale, 0, Math.PI * 2);
      this.ctx.fill();

      // Velocity Vector Arrow
      this.renderVectorArrow(p2Proj, s.vx2 * 0.4, s.vy2 * 0.4, '#ff0055', `v- = ${Math.hypot(s.vx2, s.vy2).toFixed(1)} c`);

      this.ctx.fillStyle = '#ffffff';
      this.ctx.font = '12px "Space Grotesk", sans-serif';
      this.ctx.fillText(`-m (Negative Mass: ${s.m2.toFixed(1)} kg)`, p2Proj.x - 40, p2Proj.y - 25);
      this.ctx.restore();
    }

    // 5. Draw Coupling Attraction/Repulsion Force Field Lines
    if (p1Proj && p2Proj) {
      this.ctx.save();
      this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      this.ctx.setLineDash([3, 3]);
      this.ctx.beginPath();
      this.ctx.moveTo(p1Proj.x, p1Proj.y);
      this.ctx.lineTo(p2Proj.x, p2Proj.y);
      this.ctx.stroke();

      // Center of mass indicator
      const comX = (s.m1 * s.x1 + s.m2 * s.x2) / (s.m1 + s.m2 || 1);
      const comProj = this.project(comX, 0, (s.y1 + s.y2)/2);
      if (comProj) {
        this.ctx.fillStyle = '#ffbb00';
        this.ctx.beginPath();
        this.ctx.arc(comProj.x, comProj.y, 4, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillText("RUNAWAY ACCEL VECTOR →", comProj.x + 10, comProj.y + 4);
      }
      this.ctx.restore();
    }
  }

  renderTrails(trailArray, color) {
    if (trailArray.length < 2) return;
    this.ctx.save();
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2.0;
    this.ctx.beginPath();
    for (let i = 0; i < trailArray.length; i++) {
      const proj = this.project(trailArray[i].x, 0, trailArray[i].y);
      if (proj) {
        if (i === 0) this.ctx.moveTo(proj.x, proj.y);
        else this.ctx.lineTo(proj.x, proj.y);
      }
    }
    this.ctx.stroke();
    this.ctx.restore();
  }

  renderVectorArrow(originProj, vx, vy, color, label) {
    const endProj = { x: originProj.x + vx, y: originProj.y + vy };
    this.ctx.save();
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2.5;
    this.ctx.beginPath();
    this.ctx.moveTo(originProj.x, originProj.y);
    this.ctx.lineTo(endProj.x, endProj.y);
    this.ctx.stroke();

    // Arrowhead
    const angle = Math.atan2(vy, vx);
    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.moveTo(endProj.x, endProj.y);
    this.ctx.lineTo(endProj.x - 8 * Math.cos(angle - Math.PI / 6), endProj.y - 8 * Math.sin(angle - Math.PI / 6));
    this.ctx.lineTo(endProj.x - 8 * Math.cos(angle + Math.PI / 6), endProj.y - 8 * Math.sin(angle + Math.PI / 6));
    this.ctx.closePath();
    this.ctx.fill();

    if (label && Math.hypot(vx, vy) > 10) {
      this.ctx.fillStyle = color;
      this.ctx.font = '10px "Space Grotesk", sans-serif';
      this.ctx.fillText(label, endProj.x + 8, endProj.y + 4);
    }
    this.ctx.restore();
  }

  renderFlatGrid2D() {
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    this.ctx.lineWidth = 1;
    const size = 300;
    const step = 40;
    for (let x = -size; x <= size; x += step) {
      const p1 = this.project(x, 0, -size);
      const p2 = this.project(x, 0, size);
      if (p1 && p2) {
        this.ctx.beginPath();
        this.ctx.moveTo(p1.x, p1.y);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.stroke();
      }
    }
    for (let z = -size; z <= size; z += step) {
      const p1 = this.project(-size, 0, z);
      const p2 = this.project(size, 0, z);
      if (p1 && p2) {
        this.ctx.beginPath();
        this.ctx.moveTo(p1.x, p1.y);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.stroke();
      }
    }
    this.ctx.restore();
  }

  // ----------------------------------------------------------------------------------------
  // 3. GRAVITOMAGNETISM (GEM) FRAME-DRAGGING RENDERER
  // ----------------------------------------------------------------------------------------
  renderGEMFrameDragging(dt) {
    const p = this.params.gem;

    // 1. Render Rotating Mass Core Cylinder (Source of J)
    const R_core = p.cylinderRadius;
    const height_core = 100;

    this.ctx.save();
    // Rotating top and bottom disks
    const numRing = 32;
    for (let h of [-height_core/2, height_core/2]) {
      this.ctx.strokeStyle = '#00f0ff';
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      for (let i = 0; i <= numRing; i++) {
        const theta = (i / numRing) * Math.PI * 2 + this.simTime * 2.0;
        const x = Math.cos(theta) * R_core;
        const z = Math.sin(theta) * R_core;
        const proj = this.project(x, h, z);
        if (proj) {
          if (i === 0) this.ctx.moveTo(proj.x, proj.y);
          else this.ctx.lineTo(proj.x, proj.y);
        }
      }
      this.ctx.stroke();
    }

    // Cylinder Verticals
    for (let i = 0; i < 8; i++) {
      const theta = (i / 8) * Math.PI * 2 + this.simTime * 2.0;
      const x = Math.cos(theta) * R_core;
      const z = Math.sin(theta) * R_core;
      const topProj = this.project(x, -height_core/2, z);
      const botProj = this.project(x, height_core/2, z);
      if (topProj && botProj) {
        this.ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
        this.ctx.beginPath();
        this.ctx.moveTo(topProj.x, topProj.y);
        this.ctx.lineTo(botProj.x, botProj.y);
        this.ctx.stroke();
      }
    }

    // Angular Momentum Vector J
    const jTop = this.project(0, -height_core/2 - 40, 0);
    const jBot = this.project(0, -height_core/2, 0);
    if (jTop && jBot) {
      this.renderVectorArrow(jBot, 0, -40, '#ffbb00', `ANGULAR MOMENTUM J = ${p.J.toFixed(1)} 10²⁵ J·s`);
    }

    // 2. Gravitomagnetic Swirling Field Particles (Frame-Dragging)
    for (let pt of this.gemParticles) {
      // Swirl speed decreases with 1/r^3 (Gravitomagnetic dipole)
      const swirlOmega = (p.J * 200) / Math.pow(pt.radius, 2.5);
      pt.angle += swirlOmega * dt;

      const x = Math.cos(pt.angle) * pt.radius;
      const z = Math.sin(pt.angle) * pt.radius;
      const proj = this.project(x, pt.z, z);
      if (proj) {
        this.ctx.fillStyle = pt.color;
        this.ctx.beginPath();
        this.ctx.arc(proj.x, proj.y, Math.max(1, 2.2 * proj.scale), 0, Math.PI * 2);
        this.ctx.fill();
      }
    }

    this.ctx.restore();
  }

  // ----------------------------------------------------------------------------------------
  // 4. DYNAMIC CASIMIR CAVITY RENDERER
  // ----------------------------------------------------------------------------------------
  renderCasimirCavity(dt) {
    const p = this.params.casimir;
    let d = p.gapDistance;
    if (p.vibrate) {
      d = p.gapDistance + Math.sin(this.simTime * p.frequency * 5) * 8;
    }

    const plateWidth = 140;
    const plateHeight = 120;

    this.ctx.save();

    // 1. Left Conducting Plate (-d/2)
    this.renderConductingPlate(-d / 2, plateWidth, plateHeight, 'rgba(0, 240, 255, 0.4)', 'CONDUCTOR A (V = 0)');

    // 2. Right Conducting Plate (+d/2)
    this.renderConductingPlate(d / 2, plateWidth, plateHeight, 'rgba(0, 240, 255, 0.4)', 'CONDUCTOR B (V = 0)');

    // 3. Render Standing Vacuum Wave Modes Inside the Cavity (Suppressed modes)
    this.renderRestrictedCavityModes(d, plateHeight);

    // 4. Render Vacuum Fluctuations Outside (Full continuum modes)
    this.renderExteriorVacuumModes(d, plateWidth, plateHeight);

    // 5. Radiation Pressure Force Arrows (Inward attractive Casimir force)
    const leftPlateProj = this.project(-d / 2, 0, 0);
    const rightPlateProj = this.project(d / 2, 0, 0);
    if (leftPlateProj && rightPlateProj) {
      const casimirCalc = this.engine.calculateCasimirPressure(d * 1e-9);
      this.renderVectorArrow({ x: leftPlateProj.x - 50, y: leftPlateProj.y }, 40, 0, '#ff0055', `F_casimir →`);
      this.renderVectorArrow({ x: rightPlateProj.x + 50, y: rightPlateProj.y }, -40, 0, '#ff0055', `← F_casimir`);

      // Label with formula
      this.ctx.fillStyle = '#ffbb00';
      this.ctx.font = '11px "Space Grotesk", sans-serif';
      this.ctx.fillText(`P_casimir = - (π² ħ c) / (240 d⁴) = ${Math.abs(casimirCalc.pressure_Pa).toExponential(2)} Pa`, this.width / 2 - 130, this.height - 40);
    }

    this.ctx.restore();
  }

  renderConductingPlate(posX, width, height, color, label) {
    const p1 = this.project(posX, -height / 2, -width / 2);
    const p2 = this.project(posX, -height / 2, width / 2);
    const p3 = this.project(posX, height / 2, width / 2);
    const p4 = this.project(posX, height / 2, -width / 2);

    if (p1 && p2 && p3 && p4) {
      this.ctx.fillStyle = color;
      this.ctx.strokeStyle = '#00f0ff';
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.lineTo(p3.x, p3.y);
      this.ctx.lineTo(p4.x, p4.y);
      this.ctx.closePath();
      this.ctx.fill();
      this.ctx.stroke();

      if (label) {
        this.ctx.fillStyle = '#00f0ff';
        this.ctx.font = '10px "Space Grotesk", monospace';
        this.ctx.fillText(label, p1.x - 20, p1.y - 10);
      }
    }
  }

  renderRestrictedCavityModes(d, height) {
    const numModes = 3;
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(0, 255, 157, 0.7)';
    this.ctx.lineWidth = 1.5;

    for (let n = 1; n <= numModes; n++) {
      this.ctx.beginPath();
      const samples = 30;
      for (let i = 0; i <= samples; i++) {
        const u = i / samples; // 0 to 1
        const x = -d / 2 + u * d;
        // Standing wave nodes at boundaries: sin(n * pi * u)
        const amp = 15 * Math.sin(n * Math.PI * u) * Math.cos(this.simTime * 8 + n);
        const y = -height / 4 + (n - 1) * 25 + amp;
        const proj = this.project(x, y, 0);
        if (proj) {
          if (i === 0) this.ctx.moveTo(proj.x, proj.y);
          else this.ctx.lineTo(proj.x, proj.y);
        }
      }
      this.ctx.stroke();
    }
    this.ctx.restore();
  }

  renderExteriorVacuumModes(d, width, height) {
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(255, 0, 110, 0.3)';
    this.ctx.lineWidth = 1.0;

    // Draw high-density continuum waves on left and right exterior
    for (let side of [-1, 1]) {
      const startX = side === -1 ? -d / 2 - 90 : d / 2;
      const endX = side === -1 ? -d / 2 : d / 2 + 90;
      this.ctx.beginPath();
      const samples = 40;
      for (let i = 0; i <= samples; i++) {
        const u = i / samples;
        const x = startX + u * (endX - startX);
        const wave = Math.sin(u * 12 * Math.PI + this.simTime * 12) * 10;
        const proj = this.project(x, wave, 0);
        if (proj) {
          if (i === 0) this.ctx.moveTo(proj.x, proj.y);
          else this.ctx.lineTo(proj.x, proj.y);
        }
      }
      this.ctx.stroke();
    }
    this.ctx.restore();
  }

  // ----------------------------------------------------------------------------------------
  // HUD OVERLAY (Camera coordinates & Telemetry)
  // ----------------------------------------------------------------------------------------
  renderHUDOverlay() {
    this.ctx.save();
    this.ctx.fillStyle = 'rgba(0, 240, 255, 0.7)';
    this.ctx.font = '10px "Space Grotesk", monospace';
    this.ctx.fillText(`CAM YAW: ${(this.camera.rotY * 180 / Math.PI).toFixed(0)}° | PITCH: ${(this.camera.rotX * 180 / Math.PI).toFixed(0)}° | ZOOM: ${this.camera.zoom.toFixed(2)}x`, 16, 22);
    this.ctx.fillText(`CONTROLS: LEFT-CLICK DRAG TO ROTATE // RIGHT-CLICK OR SHIFT-DRAG TO PAN // WHEEL TO ZOOM`, 16, 36);
    this.ctx.restore();
  }
}

window.SpacetimeVisualizer = SpacetimeVisualizer;
