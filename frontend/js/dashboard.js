/**
 * STAYLYTICS — Dashboard JavaScript
 *
 * Arquitectura:
 *   1. MOCK DATA       → simula la API mientras diseño sin el backend corriendo
 *   2. AUTH            → login con FormData, JWT en localStorage
 *   3. API WRAPPER     → fetch() con Authorization header
 *   4. ROUTER          → hash-based SPA (#login, #dashboard, #estudiantes, #perfil/{id})
 *   5. VIEWS           → renderizan cada sección
 *   6. CHARTS          → Chart.js con click handlers (drill-down)
 *   7. INIT            → arranque
 *
 * Modo mock = true  → usa datos locales (diseño)
 * Modo mock = false → usa fetch() real con token
 * ============================================================ */

// ================================================================
// 1. MOCK DATA — estructura IDÉNTICA a la que devuelve la API real
// ================================================================
const MOCK = Object.freeze({
  enabled: true,

  resumen: { Bajo: 10, Medio: 5, Alto: 3 },

  estudiantes: [
    { Cedula: "28544044", Nombres: "Luis", Apellidos: "Hidalgo", Edad: 25, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 1, Estatus_Actual: "Activo", Riesgo: "Alto" },
    { Cedula: "30123456", Nombres: "María", Apellidos: "González", Edad: 22, Estrato_Socioeconomico: "Bajo", Situacion_Laboral: true, ID_Estudiante: 2, Estatus_Actual: "Activo", Riesgo: "Alto" },
    { Cedula: "25111222", Nombres: "Carlos", Apellidos: "Mendoza", Edad: 24, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 3, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "27444555", Nombres: "Ana", Apellidos: "Paredes", Edad: 23, Estrato_Socioeconomico: "Alto", Situacion_Laboral: false, ID_Estudiante: 4, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "29777888", Nombres: "Pedro", Apellidos: "Ramírez", Edad: 26, Estrato_Socioeconomico: "Medio", Situacion_Laboral: true, ID_Estudiante: 5, Estatus_Actual: "Inactivo", Riesgo: "Bajo" },
    { Cedula: "26555999", Nombres: "Sofía", Apellidos: "López", Edad: 21, Estrato_Socioeconomico: "Bajo", Situacion_Laboral: false, ID_Estudiante: 6, Estatus_Actual: "Activo", Riesgo: "Bajo" },
    { Cedula: "28333444", Nombres: "Diego", Apellidos: "Martínez", Edad: 27, Estrato_Socioeconomico: "Medio", Situacion_Laboral: true, ID_Estudiante: 7, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "24666111", Nombres: "Laura", Apellidos: "Castillo", Edad: 20, Estrato_Socioeconomico: "Bajo", Situacion_Laboral: false, ID_Estudiante: 8, Estatus_Actual: "Activo", Riesgo: "Alto" },
    { Cedula: "31000222", Nombres: "Jorge", Apellidos: "Rivas", Edad: 28, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 9, Estatus_Actual: "Activo", Riesgo: "Bajo" },
    { Cedula: "27777888", Nombres: "Valentina", Apellidos: "Morales", Edad: 22, Estrato_Socioeconomico: "Alto", Situacion_Laboral: false, ID_Estudiante: 10, Estatus_Actual: "Activo", Riesgo: "Bajo" },
    { Cedula: "29333444", Nombres: "Andrés", Apellidos: "Cruz", Edad: 24, Estrato_Socioeconomico: "Medio", Situacion_Laboral: true, ID_Estudiante: 11, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "26111222", Nombres: "Camila", Apellidos: "Torres", Edad: 23, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 12, Estatus_Actual: "Activo", Riesgo: "Bajo" },
    { Cedula: "28555111", Nombres: "Fernando", Apellidos: "García", Edad: 26, Estrato_Socioeconomico: "Bajo", Situacion_Laboral: true, ID_Estudiante: 13, Estatus_Actual: "Activo", Riesgo: "Alto" },
    { Cedula: "30555666", Nombres: "Gabriela", Apellidos: "Silva", Edad: 21, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 14, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "27000123", Nombres: "Ricardo", Apellidos: "Peña", Edad: 25, Estrato_Socioeconomico: "Alto", Situacion_Laboral: false, ID_Estudiante: 15, Estatus_Actual: "Inactivo", Riesgo: "Bajo" },
    { Cedula: "25444999", Nombres: "Daniela", Apellidos: "Flores", Edad: 22, Estrato_Socioeconomico: "Bajo", Situacion_Laboral: true, ID_Estudiante: 16, Estatus_Actual: "Activo", Riesgo: "Medio" },
    { Cedula: "28111222", Nombres: "Mateo", Apellidos: "Suárez", Edad: 24, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 17, Estatus_Actual: "Activo", Riesgo: "Bajo" },
    { Cedula: "29555333", Nombres: "Isabella", Apellidos: "Rojas", Edad: 23, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 18, Estatus_Actual: "Activo", Riesgo: "Alto" },
  ],

  /** Devuelve los estudiantes filtrados por nivel de riesgo */
  estudiantesPorRiesgo(nivel) {
    return this.estudiantes.filter((e) => e.Riesgo === nivel);
  },

  /** Devuelve un estudiante por ID */
  estudiantePorId(id) {
    return this.estudiantes.find((e) => e.ID_Estudiante === id) || null;
  },
});

// ================================================================
// 2. AUTH
// ================================================================
const TOKEN_KEY = "staylytics_token";
const USER_KEY = "staylytics_user";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function estaAutenticado() {
  return !!getToken();
}

// ================================================================
// 3. API WRAPPER
// ================================================================
const API_BASE = "http://localhost:8000";

async function apiFetch(endpoint, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...options.headers,
  };

  // Si hay token y no es el login, lo inyectamos
  if (token && !endpoint.includes("/auth/")) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Modo mock: interceptamos endpoints conocidos
  if (MOCK.enabled) {
    return mockHandler(endpoint, options);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Token expirado → logout automático
  if (res.status === 401) {
    clearToken();
    window.location.hash = "#login";
    throw new Error("Sesión expirada. Iniciá sesión de nuevo.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error del servidor" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ================================================================
// 3b. MOCK HANDLER — responde igual que la API real
// ================================================================
function mockHandler(endpoint, options = {}) {
  // Simular latencia de red
  const delay = (ms) => new Promise((r) => setTimeout(r, ms));

  // Login mock
  if (endpoint === "/api/auth/login" && options.method === "POST") {
    return delay(600).then(() => ({
      access_token: "mock_token_sin_backend",
      token_type: "bearer",
    }));
  }

  // Dashboard resumen
  if (endpoint === "/api/dashboard/resumen") {
    return delay(400).then(() => ({ ...MOCK.resumen }));
  }

  // Lista de estudiantes
  if (endpoint === "/api/estudiantes/") {
    return delay(400).then(() =>
      MOCK.estudiantes.map(({ Riesgo, ...rest }) => ({
        ...rest,
        Riesgo,
      }))
    );
  }

  // Estudiantes por riesgo (drill-down)
  const riesgoMatch = endpoint.match(/^\/api\/estudiantes\/riesgo\/(\w+)$/);
  if (riesgoMatch) {
    const nivel = riesgoMatch[1].charAt(0).toUpperCase() + riesgoMatch[1].slice(1).toLowerCase();
    return delay(400).then(() =>
      MOCK.estudiantesPorRiesgo(nivel).map(({ Riesgo, ...rest }) => ({
        ...rest,
        Riesgo,
      }))
    );
  }

  // Estudiante por ID
  const idMatch = endpoint.match(/^\/api\/estudiantes\/(\d+)$/);
  if (idMatch) {
    const id = parseInt(idMatch[1], 10);
    const est = MOCK.estudiantePorId(id);
    if (!est) return delay(400).then(() => { throw new Error("Estudiante no encontrado"); });
    const { Riesgo, ...rest } = est;
    return delay(400).then(() => ({ ...rest }));
  }

  // POST falta (mock)
  if (endpoint === "/api/faltas/" && options.method === "POST") {
    const body = JSON.parse(options.body || "{}");
    return delay(500).then(() => ({
      ID_Falta: Math.floor(Math.random() * 100),
      ID_Estudiante: body.ID_Estudiante,
      Materia: body.Materia,
      Faltas_Acumuladas: body.Faltas_Acumuladas,
      Limite_Faltas: body.Limite_Faltas,
    }));
  }

  // POST historial (mock)
  if (endpoint === "/api/historial/" && options.method === "POST") {
    const body = JSON.parse(options.body || "{}");
    return delay(500).then(() => ({
      ID_Historial: Math.floor(Math.random() * 100),
      ID_Estudiante: body.ID_Estudiante,
      Materia: body.Materia,
      Semestre: body.Semestre,
      Nota_Definitiva: body.Nota_Definitiva,
      Condicion: body.Condicion || "Regular",
    }));
  }

  // Fallback
  return delay(300).then(() => ({}));
}

// ================================================================
// 4. ROUTER
// ================================================================
let currentView = null;

function navigate(hash) {
  // Extraer view y params
  const [view, ...rest] = hash.replace("#", "").split("?");
  const params = new URLSearchParams(rest.join("?"));

  // Si no está autenticado y no está en login, redirigir
  if (!estaAutenticado() && view !== "login") {
    showView("login");
    return;
  }

  // Si está autenticado y está en login, redirigir a dashboard
  if (estaAutenticado() && view === "login") {
    showView("dashboard");
    return;
  }

  switch (view) {
    case "login":
      showView("login");
      break;
    case "dashboard":
      showView("dashboard");
      renderDashboard();
      break;
    case "estudiantes":
      showView("estudiantes");
      if (params.get("riesgo")) {
        renderTablaEstudiantes(params.get("riesgo"));
      } else {
        renderTablaEstudiantes();
      }
      break;
    case "perfil":
      const id = parseInt(params.get("id"), 10);
      showView("perfil");
      renderPerfil(id);
      break;
    default:
      showView(estaAutenticado() ? "dashboard" : "login");
  }
}

function showView(view) {
  // Login vs app
  document.getElementById("view-login").classList.toggle("hidden", view !== "login");
  document.getElementById("app-main").classList.toggle("hidden", view === "login");

  // Views dentro de app
  document.querySelectorAll(".view-section").forEach((el) => {
    el.classList.toggle("hidden", el.id !== `view-${view}`);
  });

  // Active nav
  document.querySelectorAll(".nav-link").forEach((el) => {
    const isActive = el.dataset.view === view;
    el.classList.toggle("bg-white/10", isActive);
    el.classList.toggle("text-white", isActive);
    el.classList.toggle("text-gray-300", !isActive);
  });

  currentView = view;
}

// ================================================================
// 5. VIEWS
// ================================================================

// ---- 5a. LOGIN ----
async function handleLogin(email, password) {
  const btn = document.getElementById("btn-login");
  const errorEl = document.getElementById("login-error");

  btn.disabled = true;
  btn.textContent = "Ingresando...";
  errorEl.classList.add("hidden");

  try {
    if (MOCK.enabled) {
      // Mock: login instantáneo
      setToken("mock_token_sin_backend");
      window.location.hash = "#dashboard";
      return;
    }

    // Login real: FormData estricto (OAuth2)
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const data = await apiFetch("/api/auth/login", {
      method: "POST",
      body: formData,
    });

    setToken(data.access_token);
    window.location.hash = "#dashboard";
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Ingresar";
  }
}

// ---- 5b. DASHBOARD ----
let dashboardChartInstance = null;

async function renderDashboard() {
  const data = await apiFetch("/api/dashboard/resumen");

  // KPIs
  document.querySelectorAll(".kpi-val").forEach((el) => {
    const key = el.dataset.key;
    el.textContent = data[key] ?? 0;
  });

  // Chart
  const ctx = document.getElementById("dashboardChart").getContext("2d");
  if (dashboardChartInstance) dashboardChartInstance.destroy();

  const labels = ["Bajo", "Medio", "Alto"];
  const colors = ["#10B981", "#F59E0B", "#EF4444"];
  const valores = [data.Bajo, data.Medio, data.Alto];

  dashboardChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: valores,
          backgroundColor: colors,
          borderWidth: 0,
          hoverOffset: 10,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { usePointStyle: true, padding: 16, font: { size: 12 } },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
              return `${ctx.label}: ${ctx.parsed} (${pct}%)`;
            },
          },
        },
      },
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const idx = elements[0].index;
          const nivel = labels[idx];
          window.location.hash = `#estudiantes?riesgo=${nivel}`;
        }
      },
    },
    plugins: [
      {
        id: "centerTotal",
        afterDraw(chart) {
          const { ctx, chartArea, data } = chart;
          const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
          const cx = (chartArea.left + chartArea.right) / 2;
          const cy = (chartArea.top + chartArea.bottom) / 2;

          ctx.save();
          ctx.font = "bold 32px Inter, system-ui, sans-serif";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#0A2540";
          ctx.fillText(total, cx, cy - 8);
          ctx.font = "11px Inter, system-ui, sans-serif";
          ctx.fillStyle = "#6B7280";
          ctx.fillText("estudiantes", cx, cy + 20);
          ctx.restore();
        },
      },
    ],
  });

}

// ---- 5c. TABLA GENERAL DE ESTUDIANTES ----
let estudiantesData = [];

async function renderTablaEstudiantes(filtroRiesgo) {
  const tbody = document.getElementById("table-estudiantes-body");
  const empty = document.getElementById("table-estudiantes-empty");

  estudiantesData = await apiFetch("/api/estudiantes/");

  let filtered = estudiantesData;
  if (filtroRiesgo) {
    filtered = filtered.filter((e) => e.Riesgo === filtroRiesgo);
  }

  if (filtered.length === 0) {
    tbody.innerHTML = "";
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");
  tbody.innerHTML = filtered
    .map(
      (e) => `
    <tr class="border-b border-gray-50 hover:bg-gray-50 transition cursor-pointer" onclick="window.location.hash='#perfil?id=${e.ID_Estudiante}'">
      <td class="px-6 py-3.5 font-medium text-gray-900">${e.Cedula}</td>
      <td class="px-6 py-3.5">${e.Nombres} ${e.Apellidos}</td>
      <td class="px-6 py-3.5">${e.Edad}</td>
      <td class="px-6 py-3.5 capitalize">${e.Estrato_Socioeconomico}</td>
      <td class="px-6 py-3.5">
        <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${e.Estatus_Actual === "Activo" ? "bg-emerald-100 text-emerald-800" : "bg-gray-100 text-gray-600"}">
          ${e.Estatus_Actual}
        </span>
      </td>
      <td class="px-6 py-3.5">${riesgoBadgeHTML(e.Riesgo || "—")}</td>
      <td class="px-6 py-3.5">
        <button class="text-electric-cyan hover:text-cyan-700 text-xs font-medium" onclick="event.stopPropagation(); window.location.hash='#perfil?id=${e.ID_Estudiante}'">
          Ver perfil
        </button>
      </td>
    </tr>
  `
    )
    .join("");
}

// ---- 5e. PERFIL DEL ESTUDIANTE ----
async function renderPerfil(id) {
  const est = await apiFetch(`/api/estudiantes/${id}`);

  // Necesitamos el riesgo del estudiante. En modo mock está incluido,
  // en modo real necesitaríamos un endpoint adicional.
  // Por ahora lo buscamos en los datos mock.
  const riesgoEst = MOCK.enabled
    ? MOCK.estudiantePorId(id)?.Riesgo || "—"
    : "—";

  // Avatar
  const inicial = (est.Nombres || "—").charAt(0).toUpperCase();
  document.getElementById("perfil-avatar").textContent = inicial;

  // Info
  document.getElementById("perfil-nombre").textContent = `${est.Nombres || "—"} ${est.Apellidos || "—"}`;
  document.getElementById("perfil-id").textContent = `ID #${est.ID_Estudiante}`;
  document.getElementById("perfil-cedula").textContent = est.Cedula || "—";
  document.getElementById("perfil-edad").textContent = est.Edad ?? "—";
  document.getElementById("perfil-estrato").textContent = est.Estrato_Socioeconomico || "—";
  document.getElementById("perfil-laboral").textContent = est.Situacion_Laboral ? "Trabaja" : "No trabaja";
  document.getElementById("perfil-estado").textContent = est.Estatus_Actual || "—";

  // Semáforo
  const semaforoMap = {
    Bajo: { color: "#10B981", label: "Bajo", text: "white" },
    Medio: { color: "#F59E0B", label: "Medio", text: "white" },
    Alto: { color: "#EF4444", label: "Alto", text: "white" },
  };
  const s = semaforoMap[riesgoEst] || { color: "#9CA3AF", label: "Sin datos", text: "white" };
  const semaforo = document.getElementById("semaforo");
  semaforo.style.backgroundColor = s.color;
  semaforo.textContent = s.label;
  document.getElementById("semaforo-label").textContent =
    riesgoEst !== "—" ? `Riesgo ${s.label}` : "Sin datos de riesgo";

  // Cargar ID en formularios
  document.getElementById("nota-id-estudiante").value = id;
  document.getElementById("falta-id-estudiante").value = id;
}

// ---- 5f. FORM: NOTA ----
document.getElementById("form-nota").addEventListener("submit", async (e) => {
  e.preventDefault();
  const feedback = document.getElementById("nota-feedback");
  const btn = e.target.querySelector('button[type="submit"]');

  const body = {
    ID_Estudiante: parseInt(document.getElementById("nota-id-estudiante").value, 10),
    Materia: document.getElementById("nota-materia").value,
    Semestre: parseInt(document.getElementById("nota-semestre").value, 10),
    Nota_Definitiva: parseFloat(document.getElementById("nota-valor").value),
    Condicion: document.getElementById("nota-condicion").value,
  };

  btn.disabled = true;
  btn.textContent = "Guardando...";
  feedback.classList.add("hidden");

  try {
    await apiFetch("/api/historial/", {
      method: "POST",
      body: JSON.stringify(body),
    });
    feedback.className = "text-sm p-3 rounded-xl bg-emerald-50 text-emerald-700";
    feedback.textContent = "✅ Nota registrada. El riesgo se ha recalculado automáticamente.";
    feedback.classList.remove("hidden");
    e.target.reset();
    document.getElementById("nota-id-estudiante").value = body.ID_Estudiante;
  } catch (err) {
    feedback.className = "text-sm p-3 rounded-xl bg-red-50 text-red-600";
    feedback.textContent = `Error: ${err.message}`;
    feedback.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Guardar Nota";
  }
});

// ---- 5g. FORM: FALTA ----
document.getElementById("form-falta").addEventListener("submit", async (e) => {
  e.preventDefault();
  const feedback = document.getElementById("falta-feedback");
  const btn = e.target.querySelector('button[type="submit"]');

  const body = {
    ID_Estudiante: parseInt(document.getElementById("falta-id-estudiante").value, 10),
    Materia: document.getElementById("falta-materia").value,
    Faltas_Acumuladas: parseInt(document.getElementById("falta-acumuladas").value, 10),
    Limite_Faltas: parseInt(document.getElementById("falta-limite").value, 10),
  };

  btn.disabled = true;
  btn.textContent = "Guardando...";
  feedback.classList.add("hidden");

  try {
    await apiFetch("/api/faltas/", {
      method: "POST",
      body: JSON.stringify(body),
    });
    feedback.className = "text-sm p-3 rounded-xl bg-emerald-50 text-emerald-700";
    feedback.textContent = "✅ Falta registrada. El riesgo se ha recalculado automáticamente.";
    feedback.classList.remove("hidden");
    e.target.reset();
    document.getElementById("falta-id-estudiante").value = body.ID_Estudiante;
  } catch (err) {
    feedback.className = "text-sm p-3 rounded-xl bg-red-50 text-red-600";
    feedback.textContent = `Error: ${err.message}`;
    feedback.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.textContent = "Guardar Falta";
  }
});

// ---- 5h. BÚSQUEDA EN TABLA ----
document.getElementById("search-estudiantes")?.addEventListener("input", (e) => {
  const q = e.target.value.toLowerCase().trim();
  const rows = document.querySelectorAll("#table-estudiantes-body tr");
  rows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? "" : "none";
  });
});

// ================================================================
// 6. UTILITIES
// ================================================================
function riesgoBadgeHTML(nivel) {
  const map = {
    Bajo: "bg-emerald-100 text-emerald-800",
    Medio: "bg-amber-100 text-amber-800",
    Alto: "bg-red-100 text-red-800",
  };
  const cls = map[nivel] || "bg-gray-100 text-gray-600";
  return `<span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}">${nivel}</span>`;
}

// ================================================================
// 7. INIT
// ================================================================
document.addEventListener("DOMContentLoaded", () => {
  // --- Login form ---
  document.getElementById("form-login").addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    handleLogin(email, password);
  });

  // --- Mock login shortcut ---
  document.getElementById("btn-mock-login").addEventListener("click", () => {
    setToken("mock_token_sin_backend");
    window.location.hash = "#dashboard";
  });

  // --- Logout ---
  document.getElementById("btn-logout").addEventListener("click", () => {
    clearToken();
    window.location.hash = "#login";
  });

  // --- Back to students ---
  document.getElementById("btn-back-estudiantes").addEventListener("click", () => {
    window.location.hash = "#estudiantes";
  });

  // --- Router ---
  window.addEventListener("hashchange", () => navigate(window.location.hash));

  // --- Initial route ---
  if (!window.location.hash || window.location.hash === "#") {
    window.location.hash = estaAutenticado() ? "#dashboard" : "#login";
  } else {
    navigate(window.location.hash);
  }
});
