/**
 * ==========================================================================================
 * ANTIGRAV RESEARCH AI // RELATIVISTIC & QUANTUM FIELD PROPULSION ENGINE
 * Standard Physical Constants & Formal Tensor Formulations
 * ==========================================================================================
 */

const CONSTANTS = {
  G: 6.67430e-11,       // Gravitational Constant (m^3 kg^-1 s^-2)
  c: 299792458,         // Speed of Light (m/s)
  hbar: 1.054571817e-34,// Reduced Planck Constant (J s)
  h: 6.62607015e-34,    // Planck Constant (J s)
  M_earth: 5.9722e24,   // Earth Mass (kg)
  M_jupiter: 1.898e27,  // Jupiter Mass (kg)
  M_sun: 1.989e30,      // Solar Mass (kg)
  l_planck: 1.616255e-35,// Planck Length (m)
  t_planck: 5.391247e-44,// Planck Time (s)
  m_planck: 2.176434e-8, // Planck Mass (kg)
  rho_planck: 5.155e96,  // Planck Density (kg/m^3)
  kappa: (8 * Math.PI * 6.67430e-11) / Math.pow(299792458, 4) // Einstein constant ~ 2.07e-43 s^2/(m kg)
};

class RelativisticPhysicsEngine {
  constructor() {
    this.constants = CONSTANTS;
  }

  // ========================================================================================
  // 1. ALCUBIERRE WARP METRIC SOLVER (ADM 3+1 Formalism)
  // ds^2 = -c^2 dt^2 + [dx - v_s(t) f(r_s) dt]^2 + dy^2 + dz^2
  // ========================================================================================
  
  /**
   * Top-hat hyperbolic tangent shaping function f(r_s)
   * @param {number} r Distance from center of bubble (m)
   * @param {number} R Bubble radius (m)
   * @param {number} sigma Wall thickness parameter (1/m)
   */
  alcubierreShapingFunction(r, R, sigma) {
    const num = Math.tanh(sigma * (r + R)) - Math.tanh(sigma * (r - R));
    const den = 2 * Math.tanh(sigma * R);
    return num / den;
  }

  /**
   * Spatial derivative df/dr
   */
  alcubierreShapingDerivative(r, R, sigma) {
    const sechSqPlus = 1 - Math.pow(Math.tanh(sigma * (r + R)), 2);
    const sechSqMinus = 1 - Math.pow(Math.tanh(sigma * (r - R)), 2);
    const num = sigma * (sechSqPlus - sechSqMinus);
    const den = 2 * Math.tanh(sigma * R);
    return num / den;
  }

  /**
   * Eulerian Expansion Scalar theta = Tr(K_ij) = -v_s (x/r_s) (df/dr_s)
   * Positive theta => Spacetime expansion (behind the ship)
   * Negative theta => Spacetime contraction (ahead of the ship)
   */
  calculateExpansionScalar(x, y, z, vs_ratio, R, sigma) {
    const vs = vs_ratio * this.constants.c;
    const r = Math.sqrt(x * x + y * y + z * z);
    if (r < 1e-6) return 0;
    const df_dr = this.alcubierreShapingDerivative(r, R, sigma);
    return -vs * (x / r) * df_dr;
  }

  /**
   * Eulerian Energy Density rho_eff = - (c^2 / (32 pi G)) * v_s^2 * (y^2 + z^2)/r^2 * (df/dr)^2
   * Always <= 0, strictly violating WEC and NEC
   */
  calculateWarpEnergyDensity(x, y, z, vs_ratio, R, sigma) {
    const vs = vs_ratio * this.constants.c;
    const r = Math.sqrt(x * x + y * y + z * z);
    if (r < 1e-6) return 0;
    const rho_perp_sq = (y * y + z * z) / (r * r);
    const df_dr = this.alcubierreShapingDerivative(r, R, sigma);
    
    const factor = -(Math.pow(this.constants.c, 2)) / (32 * Math.PI * this.constants.G);
    const energyDensity = factor * Math.pow(vs, 2) * rho_perp_sq * Math.pow(df_dr, 2);
    return energyDensity; // Joules / m^3 (or kg/m^3 equivalent when divided by c^2)
  }

  /**
   * Integrated Total Negative Energy Mass Equivalent M_warp (kg)
   * Ford-Pfenning / Van Den Broeck scaling:
   * M ~ - (1/12) * (v_s^2 c^2 / G) * R^2 * sigma
   */
  calculateTotalWarpMassEnergy(vs_ratio, R, sigma) {
    const vs = vs_ratio * this.constants.c;
    const mass_kg = -(1 / 12) * (Math.pow(vs, 2) / this.constants.G) * Math.pow(R, 2) * sigma;
    return {
      mass_kg: mass_kg,
      mass_earth: mass_kg / this.constants.M_earth,
      mass_jupiter: mass_kg / this.constants.M_jupiter,
      mass_solar: mass_kg / this.constants.M_sun,
      energy_joules: mass_kg * Math.pow(this.constants.c, 2)
    };
  }

  // ========================================================================================
  // 2. BONDI NEGATIVE MASS DIPOLE SIMULATOR (Runge-Kutta 4th Order)
  // Mutual interaction between +m and -m: m_i = m_p = m_a
  // ========================================================================================
  
  /**
   * Step Bondi Dipole using RK4
   * @param {Object} state { x1, y1, vx1, vy1, m1 (pos), x2, y2, vx2, vy2, m2 (neg) }
   * @param {number} dt Time step
   * @param {number} G_eff Scaled gravitational coupling for numerical stability
   */
  stepBondiDipoleRK4(state, dt, G_eff = 1.0) {
    const derivatives = (s) => {
      const dx = s.x2 - s.x1;
      const dy = s.y2 - s.y1;
      const distSq = dx * dx + dy * dy + 0.1; // Softening parameter
      const dist = Math.sqrt(distSq);
      const distCubed = distSq * dist;

      // Force on pos mass m1 due to neg mass m2:
      // F_12 = - G * m1 * m2 / r^2 in direction (x2 - x1)
      // Since m2 < 0, F_12 is REPELLED (points away from m2: -(x2 - x1) = (x1 - x2))
      // a1 = F_12 / m1 = - G * m2 / r^2 * r_hat = + G * |m2| / r^2 * (x1 - x2)/r
      const a1_x = -G_eff * s.m2 * dx / distCubed;
      const a1_y = -G_eff * s.m2 * dy / distCubed;

      // Force on neg mass m2 due to pos mass m1:
      // F_21 = - G * m2 * m1 / r^2 in direction (x1 - x2)
      // a2 = F_21 / m2 = - G * m1 / r^2 * (x1 - x2)/r = + G * m1 / r^2 * (x1 - x2)/r
      // Notice a2 is in the SAME direction as (x1 - x2), meaning -m is attracted towards +m!
      const a2_x = -G_eff * s.m1 * (-dx) / distCubed;
      const a2_y = -G_eff * s.m1 * (-dy) / distCubed;

      return {
        dx1: s.vx1, dy1: s.vy1,
        dvx1: a1_x, dvy1: a1_y,
        dx2: s.vx2, dy2: s.vy2,
        dvx2: a2_x, dvy2: a2_y
      };
    };

    // RK4 Integration
    const k1 = derivatives(state);

    const s_k2 = {
      ...state,
      x1: state.x1 + 0.5 * dt * k1.dx1, y1: state.y1 + 0.5 * dt * k1.dy1,
      vx1: state.vx1 + 0.5 * dt * k1.dvx1, vy1: state.vy1 + 0.5 * dt * k1.dvy1,
      x2: state.x2 + 0.5 * dt * k1.dx2, y2: state.y2 + 0.5 * dt * k1.dy2,
      vx2: state.vx2 + 0.5 * dt * k1.dvx2, vy2: state.vy2 + 0.5 * dt * k1.dvy2
    };
    const k2 = derivatives(s_k2);

    const s_k3 = {
      ...state,
      x1: state.x1 + 0.5 * dt * k2.dx1, y1: state.y1 + 0.5 * dt * k2.dy1,
      vx1: state.vx1 + 0.5 * dt * k2.dvx1, vy1: state.vy1 + 0.5 * dt * k2.dvy1,
      x2: state.x2 + 0.5 * dt * k2.dx2, y2: state.y2 + 0.5 * dt * k2.dy2,
      vx2: state.vx2 + 0.5 * dt * k2.dvx2, vy2: state.vy2 + 0.5 * dt * k2.dvy2
    };
    const k3 = derivatives(s_k3);

    const s_k4 = {
      ...state,
      x1: state.x1 + dt * k3.dx1, y1: state.y1 + dt * k3.dy1,
      vx1: state.vx1 + dt * k3.dvx1, vy1: state.vy1 + dt * k3.dvy1,
      x2: state.x2 + dt * k3.dx2, y2: state.y2 + dt * k3.dy2,
      vx2: state.vx2 + dt * k3.dvx2, vy2: state.vy2 + dt * k3.dvy2
    };
    const k4 = derivatives(s_k4);

    const nextState = {
      ...state,
      x1: state.x1 + (dt / 6) * (k1.dx1 + 2 * k2.dx1 + 2 * k3.dx1 + k4.dx1),
      y1: state.y1 + (dt / 6) * (k1.dy1 + 2 * k2.dy1 + 2 * k3.dy1 + k4.dy1),
      vx1: state.vx1 + (dt / 6) * (k1.dvx1 + 2 * k2.dvx1 + 2 * k3.dvx1 + k4.dvx1),
      vy1: state.vy1 + (dt / 6) * (k1.dvy1 + 2 * k2.dvy1 + 2 * k3.dvy1 + k4.dvy1),
      x2: state.x2 + (dt / 6) * (k1.dx2 + 2 * k2.dx2 + 2 * k3.dx2 + k4.dx2),
      y2: state.y2 + (dt / 6) * (k1.dy2 + 2 * k2.dy2 + 2 * k3.dy2 + k4.dy2),
      vx2: state.vx2 + (dt / 6) * (k1.dvx2 + 2 * k2.dvx2 + 2 * k3.dvx2 + k4.dvx2),
      vy2: state.vy2 + (dt / 6) * (k1.dvy2 + 2 * k2.dvy2 + 2 * k3.dvy2 + k4.dvy2)
    };

    // Calculate diagnostic invariants
    const Px = state.m1 * nextState.vx1 + state.m2 * nextState.vx2;
    const Py = state.m1 * nextState.vy1 + state.m2 * nextState.vy2;
    const Ek = 0.5 * state.m1 * (nextState.vx1 ** 2 + nextState.vy1 ** 2) +
               0.5 * state.m2 * (nextState.vx2 ** 2 + nextState.vy2 ** 2);

    return { nextState, Px, Py, Ek };
  }

  // ========================================================================================
  // 3. GRAVITOELECTROMAGNETISM (GEM) FRAME-DRAGGING SOLVER
  // Weak-field linearized Einstein equations
  // ========================================================================================
  
  /**
   * Gravitomagnetic field B_g at distance r from rotating cylinder/toroid
   * B_g = (G / c^2) * (2 J / r^3)
   * @param {number} J Angular momentum (kg m^2 / s)
   * @param {number} r Distance (m)
   */
  calculateGravitomagneticField(J, r) {
    if (r < 1e-3) r = 1e-3;
    const Bg = (this.constants.G / Math.pow(this.constants.c, 2)) * (2 * J / Math.pow(r, 3));
    return Bg; // s^-1
  }

  /**
   * Gravitomagnetic Lorentz Acceleration: a_g = E_g + v x B_g
   */
  calculateGEMAcceleration(Eg, v, Bg) {
    return Eg + v * Bg; // m/s^2
  }

  /**
   * Required angular momentum density to cancel 1g (9.81 m/s^2) at laboratory velocity v
   */
  calculateRequiredGEMDensity(v_test, target_g = 9.80665) {
    const required_Bg = target_g / v_test; // B_g = g / v
    // B_g ~ (G / c^2) * rho_J
    const required_J_density = (Math.pow(this.constants.c, 2) * required_Bg) / this.constants.G;
    return {
      required_Bg,
      required_J_density,
      ratio_to_neutron_star: required_J_density / 1e24
    };
  }

  // ========================================================================================
  // 4. CASIMIR EFFECT & QUANTUM VACUUM MODES
  // F/A = - (pi^2 * hbar * c) / (240 * d^4)
  // ========================================================================================
  
  calculateCasimirPressure(d_meters) {
    if (d_meters < 1e-12) d_meters = 1e-12; // Prevent singularity
    const pressure = -(Math.PI ** 2 * this.constants.hbar * this.constants.c) / (240 * Math.pow(d_meters, 4));
    const energyDensity = -(Math.PI ** 2 * this.constants.hbar * this.constants.c) / (720 * Math.pow(d_meters, 4));
    return {
      pressure_Pa: pressure,
      energyDensity_J_m3: energyDensity,
      force_on_1m2_N: Math.abs(pressure)
    };
  }

  /**
   * Ford-Roman Bound Evaluator
   * Maximum negative energy duration tau_0 for a given negative energy density rho_neg
   * |rho_neg| <= (3 hbar) / (32 pi^2 c^3 tau_0^4) => tau_0 <= [ 3 hbar / (32 pi^2 c^3 |rho_neg|) ]^(1/4)
   */
  calculateFordRomanLimit(rho_neg_J_m3) {
    const rho_abs = Math.abs(rho_neg_J_m3);
    if (rho_abs === 0) return Infinity;
    const numerator = 3 * this.constants.hbar;
    const denominator = 32 * Math.pow(Math.PI, 2) * Math.pow(this.constants.c, 3) * rho_abs;
    const tau_max = Math.pow(numerator / denominator, 0.25);
    return tau_max; // seconds
  }

  // ========================================================================================
  // 5. ENERGY CONDITION VALIDATOR
  // Evaluates arbitrary Stress-Energy Tensor T_mu_nu diagonal (rho, p_x, p_y, p_z)
  // ========================================================================================
  
  validateEnergyConditions(rho, px, py, pz) {
    const p_sum = px + py + pz;
    
    // Null Energy Condition (NEC): rho + p_i >= 0 for all i
    const nec_pass = (rho + px >= 0) && (rho + py >= 0) && (rho + pz >= 0);
    
    // Weak Energy Condition (WEC): rho >= 0 and rho + p_i >= 0
    const wec_pass = (rho >= 0) && nec_pass;
    
    // Strong Energy Condition (SEC): rho + sum(p_i) >= 0 and rho + p_i >= 0
    const sec_pass = (rho + p_sum >= 0) && nec_pass;
    
    // Dominant Energy Condition (DEC): rho >= 0 and rho >= |p_i| for all i
    const dec_pass = (rho >= 0) && (rho >= Math.abs(px)) && (rho >= Math.abs(py)) && (rho >= Math.abs(pz));

    return {
      NEC: {
        satisfied: nec_pass,
        details: `rho + p_x = ${(rho+px).toExponential(3)}, rho + p_y = ${(rho+py).toExponential(3)}, rho + p_z = ${(rho+pz).toExponential(3)}`,
        formalText: "T_μν k^μ k^ν ≥ 0 (Light-cone non-divergence)"
      },
      WEC: {
        satisfied: wec_pass,
        details: `rho = ${rho.toExponential(3)} (>= 0 required)`,
        formalText: "T_μν u^μ u^ν ≥ 0 (Positive local observer energy)"
      },
      SEC: {
        satisfied: sec_pass,
        details: `rho + sum(p_i) = ${(rho + p_sum).toExponential(3)}`,
        formalText: "(T_μν - 1/2 T g_μν) u^μ u^ν ≥ 0 (Gravitational attraction)"
      },
      DEC: {
        satisfied: dec_pass,
        details: `Max pressure = ${Math.max(Math.abs(px), Math.abs(py), Math.abs(pz)).toExponential(3)}`,
        formalText: "Causal energy flux (Energy cannot travel faster than light)"
      }
    };
  }
}

// Export for browser
window.RelativisticPhysicsEngine = RelativisticPhysicsEngine;
window.PHYSICS_CONSTANTS = CONSTANTS;
