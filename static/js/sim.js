/* sim.js — Planetary Free-Fall Web Simulator */
"use strict";

const PLANET_COLORS = {
    Mercury: "#a8a8a8", Venus: "#ffc649",  Earth:   "#6495ed",
    Mars:    "#cd5c5c", Jupiter: "#ff8c00", Saturn:  "#ffd700",
    Uranus:  "#40e0d0", Neptune: "#1e90ff", Pluto:   "#8b6355",
};

// ── State ─────────────────────────────────────────────────────────────────────
let simData       = null;
let animState     = [];
let rafId         = null;
let paused        = false;
let selectedIcon  = null;
let currentSort   = "fall_time";
let currentHeight = 100;
let currentShape  = "circle";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const massInput       = document.getElementById("mass-input");
const iconSearch      = document.getElementById("icon-search");
const iconGrid        = document.getElementById("icon-grid");
const selectedIconRow = document.getElementById("selected-icon-row");
const selectedIconPrv = document.getElementById("selected-icon-preview");
const selectedIconNm  = document.getElementById("selected-icon-name");
const clearIconBtn    = document.getElementById("clear-icon-btn");
const runBtn          = document.getElementById("run-btn");
const pauseBtn        = document.getElementById("pause-btn");
const restartBtn      = document.getElementById("restart-btn");
const simStage        = document.getElementById("sim-stage");
const simTitle        = document.getElementById("sim-title");
const resultsTable    = document.getElementById("results-table");
const sortSelect      = document.getElementById("sort-select");

// ── Preset mass buttons ───────────────────────────────────────────────────────
document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => { massInput.value = btn.dataset.mass; });
});

// ── Height buttons ────────────────────────────────────────────────────────────
document.querySelectorAll(".height-btn").forEach(btn => {
    if (btn.dataset.h === "100") btn.classList.add("active");
    else btn.classList.remove("active");

    btn.addEventListener("click", () => {
        document.querySelectorAll(".height-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentHeight = parseInt(btn.dataset.h);
    });
});

// ── Shape buttons ─────────────────────────────────────────────────────────────
document.querySelectorAll(".shape-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".shape-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentShape = btn.dataset.shape;
    });
});

// ── Icon search ───────────────────────────────────────────────────────────────
let searchDebounce = null;
iconSearch.addEventListener("input", () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(fetchIcons, 260);
});

async function fetchIcons() {
    try {
        const q   = iconSearch.value.trim();
        const res = await fetch(`/api/icons?q=${encodeURIComponent(q)}`);
        // FIX: check HTTP status before parsing
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const icons = await res.json();
        renderIconGrid(icons);
    } catch (e) {
        console.error("Icon fetch failed:", e);
        iconGrid.innerHTML = `<p style="color:var(--txt3);font-size:.75rem;grid-column:1/-1;padding:6px">Could not load icons</p>`;
    }
}

function renderIconGrid(icons) {
    iconGrid.innerHTML = "";
    if (!icons.length) {
        iconGrid.innerHTML = `<p style="color:var(--txt3);font-size:.75rem;grid-column:1/-1;padding:6px">No icons found</p>`;
        return;
    }
    icons.forEach(icon => {
        const el = document.createElement("div");
        el.className = "icon-item" + (selectedIcon?.name === icon.name ? " selected" : "");
        el.title = icon.name;
        // FIX: sanitize icon name before injecting into class — only allow alphanumeric and hyphen
        const safeName = icon.name.replace(/[^a-z0-9-]/g, "");
        el.innerHTML = `<i class="fa-solid fa-${safeName}"></i><span>${safeName.split("-")[0]}</span>`;
        el.addEventListener("click", () => selectIcon(icon, el));
        iconGrid.appendChild(el);
    });
}

function selectIcon(icon, el) {
    document.querySelectorAll(".icon-item").forEach(i => i.classList.remove("selected"));
    el.classList.add("selected");
    selectedIcon = icon;
    const safeName = icon.name.replace(/[^a-z0-9-]/g, "");
    selectedIconPrv.className = `fa-solid fa-${safeName}`;
    selectedIconNm.textContent = icon.name;
    selectedIconRow.style.display = "flex";
}

clearIconBtn.addEventListener("click", () => {
    selectedIcon = null;
    selectedIconRow.style.display = "none";
    document.querySelectorAll(".icon-item").forEach(i => i.classList.remove("selected"));
});

// ── Run simulation ────────────────────────────────────────────────────────────
runBtn.addEventListener("click", launchSim);

// FIX: also allow Enter key in mass input to trigger simulation
massInput.addEventListener("keydown", e => {
    if (e.key === "Enter") launchSim();
});

async function launchSim() {
    const mass = parseFloat(massInput.value);
    if (!mass || mass <= 0) {
        massInput.focus();
        massInput.style.borderColor = "var(--danger)";
        setTimeout(() => { massInput.style.borderColor = ""; }, 1000);
        return;
    }

    runBtn.disabled = true;
    runBtn.classList.add("loading");
    runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running…`;
    cancelAnimation();

    const body = {
        mass,
        shape:  currentShape,
        height: currentHeight,
        icon:   selectedIcon?.name || currentShape,
    };

    try {
        const res = await fetch("/api/simulate", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(body),
        });

        // FIX: handle non-2xx responses with a user-visible message
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: "Unknown error" }));
            showError(err.error || `Server error ${res.status}`);
            return;
        }

        simData = await res.json();
        buildStage(simData);
        buildResults(simData.results);
        startAnimation();
        pauseBtn.disabled   = false;
        restartBtn.disabled = false;
        simTitle.textContent = `${simData.mass} kg · ${simData.icon} · ${simData.height} m drop`;

    } catch (e) {
        // FIX: network errors (offline, CORS, etc.) shown to user
        showError("Network error — is the server running?");
        console.error(e);
    } finally {
        runBtn.disabled = false;
        runBtn.classList.remove("loading");
        runBtn.innerHTML = `<i class="fa-solid fa-play"></i> Launch Simulation`;
    }
}

function showError(msg) {
    simStage.innerHTML = `
    <div class="sim-placeholder">
      <i class="fa-solid fa-triangle-exclamation" style="color:var(--danger)"></i>
      <p style="color:var(--danger)">${msg}</p>
    </div>`;
}

// ── Pause / Restart ───────────────────────────────────────────────────────────
pauseBtn.addEventListener("click", () => {
    paused = !paused;
    pauseBtn.innerHTML = paused
        ? `<i class="fa-solid fa-play"></i>`
        : `<i class="fa-solid fa-pause"></i>`;
});

restartBtn.addEventListener("click", () => {
    if (!simData) return;
    cancelAnimation();
    buildStage(simData);
    buildResults(simData.results);
    startAnimation();
    paused = false;
    pauseBtn.innerHTML = `<i class="fa-solid fa-pause"></i>`;
});

sortSelect.addEventListener("change", () => {
    currentSort = sortSelect.value;
    if (simData) buildResults(simData.results);
});

// ── Stage builder ─────────────────────────────────────────────────────────────
function buildStage(data) {
    simStage.innerHTML = "";

    // FIX: use getBoundingClientRect for accurate dimensions after layout
    const rect = simStage.getBoundingClientRect();
    const W = rect.width  || simStage.clientWidth;
    const H = rect.height || simStage.clientHeight;

    const planets  = data.results;
    const colW     = W / planets.length;
    const groundPct = 88;

    // Ground line
    const groundEl = document.createElement("div");
    groundEl.className = "ground-line";
    groundEl.style.cssText = `top:${groundPct}%;`;
    simStage.appendChild(groundEl);

    const groundLbl = document.createElement("div");
    groundLbl.className = "ground-label";
    groundLbl.style.cssText = `top:${groundPct}%; padding-top:4px;`;
    groundLbl.textContent = "0 m";
    simStage.appendChild(groundLbl);

    const safIcon = (data.icon || "circle").replace(/[^a-z0-9-]/g, "");

    animState = planets.map((p, i) => {
        const cx    = colW * i + colW / 2;
        const color = PLANET_COLORS[p.planet] || "#ffffff";

        // Planet label
        const lbl = document.createElement("div");
        lbl.className = "planet-label";
        lbl.style.cssText = `position:absolute;left:${cx}px;top:8px;transform:translateX(-50%);color:${color};`;
        lbl.textContent = p.planet;
        simStage.appendChild(lbl);

        // Gravity sub-label
        const glbl = document.createElement("div");
        glbl.style.cssText = `position:absolute;left:${cx}px;top:26px;transform:translateX(-50%);
      font-size:.58rem;color:var(--txt3);font-family:'Space Mono',monospace;`;
        glbl.textContent = `${p.gravity}g`;
        simStage.appendChild(glbl);

        // Dashed track
        const track = document.createElement("div");
        track.style.cssText = `position:absolute;left:${cx}px;top:44px;width:1px;
      height:${groundPct - 8}%;background:repeating-linear-gradient(
        to bottom,${color}33 0,${color}33 4px,transparent 4px,transparent 10px);`;
        simStage.appendChild(track);

        // Object
        const obj = document.createElement("div");
        obj.className = "falling-object";
        obj.style.cssText = `left:${cx}px;top:10%;color:${color};`;
        obj.innerHTML = `<i class="fa-solid fa-${safIcon}"></i>`;
        simStage.appendChild(obj);

        // Live readout
        const readout = document.createElement("div");
        readout.style.cssText = `position:absolute;left:${cx + 14}px;font-size:.6rem;
      color:${color};font-family:'Space Mono',monospace;white-space:nowrap;pointer-events:none;`;
        simStage.appendChild(readout);

        return {
            planet: p.planet, color, cx,
            objEl: obj, readEl: readout,
            tSeries: p.t_series, ySeries: p.y_series, vSeries: p.v_series,
            maxT: p.fall_time, maxV: p.final_velocity,
            height: data.height, groundPct, H,
            landed: false, trails: [],
        };
    });
}

// ── Animation loop ────────────────────────────────────────────────────────────
let lastTs     = null;
let simElapsed = 0;

function startAnimation() {
    lastTs     = null;
    simElapsed = 0;
    paused     = false;
    rafId      = requestAnimationFrame(tick);
}

function cancelAnimation() {
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    // FIX: clear orphaned trail dots when cancelling mid-animation
    simStage.querySelectorAll(".trail-dot").forEach(d => d.remove());
}

function tick(ts) {
    if (!lastTs) lastTs = ts;
    const delta = (ts - lastTs) / 1000;
    lastTs = ts;

    // FIX: clamp delta to max 0.1s to prevent huge jumps after tab switching
    if (!paused) simElapsed += Math.min(delta, 0.1);

    let allLanded = true;

    animState.forEach(state => {
        if (state.landed) return;

        const idx = state.tSeries.findIndex(t => t >= simElapsed);
        const i   = idx === -1 ? state.tSeries.length - 1 : idx;

        const y = state.ySeries[i];
        const v = state.vSeries[i];

        const topPct    = 8;
        const dropRange = state.groundPct - topPct;
        // FIX: guard against divide-by-zero if height is somehow 0
        const heightSafe = state.height || 1;
        const pct    = topPct + (1 - y / heightSafe) * dropRange;
        const screenY = (pct / 100) * state.H;

        state.objEl.style.top   = `${screenY}px`;
        state.objEl.style.color = speedColor(v / (state.maxV || 1));

        if (!paused && simElapsed % 0.06 < 0.02) addTrail(state, state.cx, screenY);

        state.readEl.style.top  = `${Math.max(screenY - 12, 30)}px`;
        state.readEl.textContent = `${v.toFixed(1)} m/s`;

        if (idx === -1 || y <= 0) {
            state.landed = true;
            state.objEl.style.top   = `${(state.groundPct / 100) * state.H}px`;
            state.objEl.style.color = state.color;
            state.readEl.textContent = `✓ ${state.maxV.toFixed(1)} m/s`;
            impactFlash(state.cx, (state.groundPct / 100) * state.H, state.color);
            updateCardLanded(state.planet);
        } else {
            allLanded = false;
        }
    });

    if (!allLanded || paused) {
        rafId = requestAnimationFrame(tick);
    } else {
        rafId = null;
    }
}

function speedColor(ratio) {
    if (ratio < 0.4)  return "#6495ed";
    if (ratio < 0.75) return "#ffd700";
    return "#ff4444";
}

function addTrail(state, x, y) {
    const dot = document.createElement("div");
    dot.className = "trail-dot";
    dot.style.cssText = `left:${x}px;top:${y}px;background:${state.color};`;
    simStage.appendChild(dot);
    state.trails.push(dot);
    setTimeout(() => { dot.remove(); state.trails.shift(); }, 600);
}

function impactFlash(x, y, color) {
    const flash = document.createElement("div");
    flash.className = "impact-flash";
    flash.style.cssText = `left:${x}px;top:${y}px;background:${color};`;
    simStage.appendChild(flash);
    setTimeout(() => flash.remove(), 550);
}

// ── Results table ─────────────────────────────────────────────────────────────
function buildResults(results) {
    const sorted  = [...results].sort((a, b) => a[currentSort] - b[currentSort]);
    // FIX: guard against empty results or all-zero fall_time
    const maxTime = Math.max(...results.map(r => r.fall_time), 1);

    resultsTable.innerHTML = "";
    sorted.forEach((r, delay) => {
        const card = document.createElement("div");
        card.className = "result-card";
        card.id        = `card-${r.planet}`;
        card.style.animationDelay = `${delay * 0.04}s`;

        const vt      = r.v_terminal !== null ? `${r.v_terminal} m/s` : "∞ (no atm.)";
        const pctFill = ((r.fall_time / maxTime) * 100).toFixed(1);
        const color   = PLANET_COLORS[r.planet] || "#ffffff";

        // FIX: use textContent for user-controlled values to prevent XSS
        card.innerHTML = `
      <div class="card-header">
        <div class="planet-dot" style="background:${color}"></div>
        <span class="card-planet"></span>
        <span class="card-gravity"></span>
        <span class="card-impact-badge"></span>
      </div>
      <div class="card-metrics">
        <div class="metric">
          <span class="metric-label">Fall Time</span>
          <span class="metric-value highlight"></span>
        </div>
        <div class="metric">
          <span class="metric-label">Impact Velocity</span>
          <span class="metric-value"></span>
        </div>
        <div class="metric">
          <span class="metric-label">KE at Impact</span>
          <span class="metric-value"></span>
        </div>
        <div class="metric">
          <span class="metric-label">Terminal v</span>
          <span class="metric-value"></span>
        </div>
        <div class="metric">
          <span class="metric-label">Momentum</span>
          <span class="metric-value"></span>
        </div>
        <div class="metric">
          <span class="metric-label">Air Density</span>
          <span class="metric-value"></span>
        </div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${pctFill}%"></div>
      </div>`;

        // Safely set text values
        const [planet, gravity, badge] = card.querySelectorAll(".card-planet, .card-gravity, .card-impact-badge");
        planet.textContent = r.planet;
        gravity.textContent = `${r.gravity} m/s²`;
        badge.textContent = r.impact_desc;

        const vals = card.querySelectorAll(".metric-value");
        vals[0].textContent = `${r.fall_time.toFixed(2)} s`;
        vals[1].textContent = `${r.final_velocity.toFixed(1)} m/s`;
        vals[2].textContent = `${r.ke_impact.toFixed(0)} J`;
        vals[3].textContent = vt;
        vals[4].textContent = `${r.momentum.toFixed(1)} kg·m/s`;
        vals[5].textContent = `${r.air_density} kg/m³`;

        resultsTable.appendChild(card);
    });
}

function updateCardLanded(planet) {
    const card = document.getElementById(`card-${planet}`);
    if (card) card.classList.add("landed");
}

// ── Boot ──────────────────────────────────────────────────────────────────────
fetchIcons();