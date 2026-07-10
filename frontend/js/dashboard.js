/**
 * STAYLYTICS — Dashboard JavaScript
 *
 * Arquitectura:
 * 1. MOCK DATA       → simula la API mientras diseño sin el backend corriendo
 * 2. AUTH            → login con FormData, JWT en localStorage
 * 3. API WRAPPER     → fetch() con Authorization header
 * 4. ROUTER          → hash-based SPA (#login, #dashboard, #estudiantes, #perfil/{id})
 * 5. VIEWS           → renderizan cada sección
 * 6. CHARTS          → Chart.js con click handlers (drill-down)
 * 7. INIT            → arranque
 *
 * Modo mock = true  → usa datos locales (diseño)
 * Modo mock = false → usa fetch() real con token
 * ============================================================ */


// 1. MOCK DATA — estructura IDÉNTICA a la que devuelve la API real

const MOCK = Object.freeze({
  enabled: false, 

  resumen: { Bajo: 10, Medio: 5, Alto: 3 },

  estudiantes: [
    { Cedula: "28544044", Nombres: "Luis", Apellidos: "Hidalgo", Edad: 25, Estrato_Socioeconomico: "Medio", Situacion_Laboral: false, ID_Estudiante: 1, Estatus_Actual: "Activo", Riesgo: "Alto" },
    
  ],

  
  estudiantesPorRiesgo(nivel) {
    return this.estudiantes.filter((e) => e.Riesgo === nivel);
  },

 
  estudiantePorId(id) {
    return this.estudiantes.find((e) => e.ID_Estudiante === id) || null;
  },
});


// 2. AUTH

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


// 3. API WRAPPER

const API_BASE = "http://localhost:8000";

//const API_BASE = "https://staylytics-api.onrender.com";

async function apiFetch(endpoint, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...options.headers,
  };

  
  if (token && !endpoint.includes("/auth/")) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  
  if (MOCK.enabled) {
    return mockHandler(endpoint, options);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  
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


// 3b. MOCK HANDLER — responde igual que la API real

function mockHandler(endpoint, options = {}) {
  
  const delay = (ms) => new Promise((r) => setTimeout(r, ms));

  
  if (endpoint === "/api/auth/login" && options.method === "POST") {
    return delay(600).then(() => ({
      access_token: "mock_token_sin_backend",
      token_type: "bearer",
    }));
  }

  
  if (endpoint === "/api/dashboard/resumen") {
    return delay(400).then(() => ({ ...MOCK.resumen }));
  }

  
  if (endpoint === "/api/estudiantes/") {
    return delay(400).then(() =>
      MOCK.estudiantes.map(({ Riesgo, ...rest }) => ({
        ...rest,
        Riesgo,
      }))
    );
  }

  
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

  
  const idMatch = endpoint.match(/^\/api\/estudiantes\/(\d+)$/);
  if (idMatch) {
    const id = parseInt(idMatch[1], 10);
    const est = MOCK.estudiantePorId(id);
    if (!est) return delay(400).then(() => { throw new Error("Estudiante no encontrado"); });
    const { Riesgo, ...rest } = est;
    return delay(400).then(() => ({ ...rest }));
  }

  
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

  
  return delay(300).then(() => ({}));
}


// 4. ROUTER

let currentView = null;

function navigate(hash) {
  
  const [view, ...rest] = hash.replace("#", "").split("?");
  const params = new URLSearchParams(rest.join("?"));

  
  if (!estaAutenticado() && view !== "login") {
    showView("login");
    return;
  }

  
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
  
  document.getElementById("view-login").classList.toggle("hidden", view !== "login");
  document.getElementById("app-main").classList.toggle("hidden", view === "login");

  
  document.querySelectorAll(".view-section").forEach((el) => {
    el.classList.toggle("hidden", el.id !== `view-${view}`);
  });

  
  document.querySelectorAll(".nav-link").forEach((el) => {
    const isActive = el.dataset.view === view;
    el.classList.toggle("bg-white/10", isActive);
    el.classList.toggle("text-white", isActive);
    el.classList.toggle("text-gray-300", !isActive);
  });

  currentView = view;
}


// 5. VIEWS


// ---- 5a. LOGIN ----
async function handleLogin(email, password) {
  const btn = document.getElementById("btn-login");
  const errorEl = document.getElementById("login-error");

  btn.disabled = true;
  btn.textContent = "Ingresando...";
  errorEl.classList.add("hidden");

  try {
    if (MOCK.enabled) {
      
      setToken("mock_token_sin_backend");
      window.location.hash = "#dashboard";
      return;
    }

    
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
  const carreraSeleccionada = document.getElementById('filtro-carrera-dashboard').value;
  let url = "/api/dashboard/resumen";
  if (carreraSeleccionada !== "Todas") {
      url += `?carrera=${encodeURIComponent(carreraSeleccionada)}`;
  }

  const data = await apiFetch(url);

  
  document.getElementById('titulo-periodo').textContent = `Resumen Analítico — Cohorte ${data.Periodo_Actual}`;
  document.getElementById('mensaje-inteligente').textContent = data.Mensaje_Inteligente;

  
  document.querySelectorAll(".kpi-val").forEach((el) => {
    const key = el.dataset.key;
    el.textContent = data[key] ?? 0;
  });

 
  const ctx = document.getElementById("dashboardChart").getContext("2d");
  if (dashboardChartInstance) dashboardChartInstance.destroy();

  const labels = ["Bajo", "Medio", "Alto"];
  const colors = ["#10B981", "#F59E0B", "#EF4444"];
  const valores = [data.Bajo, data.Medio, data.Alto];

  dashboardChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
          data: valores,
          backgroundColor: colors,
          borderWidth: 0,
          hoverOffset: 10,
        }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const nivel = labels[elements[0].index];
          window.location.hash = `#estudiantes?riesgo=${nivel}`;
        }
      },
    },
    plugins: [{
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
    }],
  });
}

// ---- 5c. TABLA GENERAL DE ESTUDIANTES ----
let estudiantesData = [];

let ordenRiesgoActivo = 0; 
let limiteVisualEstudiantes = 100; 

async function renderTablaEstudiantes(filtroRiesgoDirecto, cargarMas = false) {
  const tbody = document.getElementById("table-estudiantes-body");
  const empty = document.getElementById("table-estudiantes-empty");
  const pagContainer = document.getElementById("pagination-container");

  
  if (!cargarMas) {
      limiteVisualEstudiantes = 100;
  }

  const carrera = document.getElementById("filtro-carrera-estudiantes")?.value || "Todas";
  const periodo = document.getElementById("filtro-periodo-estudiantes")?.value || "Todos";
  const filtroLocalRiesgo = filtroRiesgoDirecto || document.getElementById("filtro-riesgo-estudiantes")?.value || "Todos";

  if (filtroRiesgoDirecto && document.getElementById("filtro-riesgo-estudiantes")) {
      document.getElementById("filtro-riesgo-estudiantes").value = filtroRiesgoDirecto;
  }

  let endpoint = "/api/estudiantes/";
  const params = new URLSearchParams();
  if (carrera !== "Todas") params.append("carrera", carrera);
  if (periodo !== "Todos") params.append("periodo", periodo);
  const queryStr = params.toString();
  if (queryStr) endpoint += `?${queryStr}`;

  
  if (!cargarMas) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-gray-400 py-12">Filtrando expedientes...</td></tr>`;
  }

  try {
    
    if (!cargarMas) {
        estudiantesData = await apiFetch(endpoint);
    }

    let dataFiltrada = estudiantesData;
    if (filtroLocalRiesgo !== "Todos") {
        dataFiltrada = dataFiltrada.filter(e => e.Riesgo === filtroLocalRiesgo);
    }

    if (dataFiltrada.length === 0) {
      tbody.innerHTML = "";
      empty.classList.remove("hidden");
      pagContainer?.classList.add("hidden");
      return;
    }

    empty.classList.add("hidden");

    
    const jerarquiaRiesgo = { "Alto": 4, "Medio": 3, "Bajo": 2, "Inactivo": 1, "—": 0 };
    dataFiltrada.sort((a, b) => {
        if (ordenRiesgoActivo === 0) {
            const nombreA = `${a.Nombres} ${a.Apellidos}`.toLowerCase();
            const nombreB = `${b.Nombres} ${b.Apellidos}`.toLowerCase();
            return nombreA.localeCompare(nombreB);
        } else {
            const pesoA = jerarquiaRiesgo[a.Riesgo || "—"];
            const pesoB = jerarquiaRiesgo[b.Riesgo || "—"];
            return (pesoA - pesoB) * ordenRiesgoActivo;
        }
    });

    
    const totalFiltrados = dataFiltrada.length;
    const chunkMostrado = dataFiltrada.slice(0, limiteVisualEstudiantes);

    tbody.innerHTML = chunkMostrado
      .map((e) => `
        <tr class="border-b border-gray-50 hover:bg-gray-50 transition cursor-pointer" onclick="window.location.hash='#perfil?id=${e.ID_Estudiante}'">
          <td class="px-6 py-3.5 font-medium text-gray-900">${e.Cedula}</td>
          <td class="px-6 py-3.5">${e.Nombres} ${e.Apellidos}</td>
          <td class="px-6 py-3.5">${e.Edad}</td>
          <td class="px-6 py-3.5 capitalize">${e.Estrato_Socioeconomico}</td>
          <td class="px-6 py-3.5">
            <span class="inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${e.Es_Regular ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"}">
              ${e.Es_Regular ? "Regular" : "Solo Activo"}
            </span>
          </td>
          <td class="px-6 py-3.5">${riesgoBadgeHTML(e.Riesgo || "—")}</td>
          <td class="px-6 py-3.5">
            <button class="text-electric-cyan hover:text-cyan-700 text-xs font-medium" onclick="event.stopPropagation(); window.location.hash='#perfil?id=${e.ID_Estudiante}'">
              Ver perfil
            </button>
          </td>
        </tr>
      `).join("");

    
    if (pagContainer) {
        if (limiteVisualEstudiantes < totalFiltrados) {
            pagContainer.classList.remove("hidden");
        } else {
            pagContainer.classList.add("hidden");
        }
    }

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 py-12">Error: ${err.message}</td></tr>`;
  }
}

// ---- 5e. PERFIL DEL ESTUDIANTE ----
async function renderPerfil(id) {
  const est = await apiFetch(`/api/estudiantes/${id}`);

  
  const riesgoEst = est.Riesgo || "—"; 

  
  const inicial = (est.Nombres || "—").charAt(0).toUpperCase();
  document.getElementById("perfil-avatar").textContent = inicial;

  
  document.getElementById("perfil-nombre").textContent = `${est.Nombres || "—"} ${est.Apellidos || "—"}`;
  document.getElementById("perfil-id").textContent = `ID #${est.ID_Estudiante}`;
  document.getElementById("perfil-cedula").textContent = est.Cedula || "—";
  document.getElementById("perfil-edad").textContent = est.Edad ?? "—";
  document.getElementById("perfil-estrato").textContent = est.Estrato_Socioeconomico || "—";
  document.getElementById("perfil-laboral").textContent = est.Situacion_Laboral ? "Trabaja" : "No trabaja";
  document.getElementById("perfil-estado").textContent = est.Estatus_Actual || "—";
  document.getElementById('perfil-genero').textContent = est.Genero || "—";
  document.getElementById('perfil-carrera').textContent = est.Carrera || "—";
  document.getElementById('perfil-carrera').title = est.Carrera || "—";

  const inscripcionEl = document.getElementById('perfil-inscripcion');
  if (est.Es_Regular) {
      inscripcionEl.textContent = "Regular (Inscrito)";
      inscripcionEl.className = "font-semibold text-emerald-600";
  } else {
      inscripcionEl.textContent = "Solo Activo";
      inscripcionEl.className = "font-semibold text-red-600";
  }

  
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

  
  document.getElementById("nota-id-estudiante").value = id;
  document.getElementById("falta-id-estudiante").value = id;

  
  try {
    const expediente = await apiFetch(`/api/estudiantes/${id}/expediente`);
    
    
    const tbodyNotas = document.getElementById("perfil-tabla-notas");
    if (expediente.notas.length === 0) {
      tbodyNotas.innerHTML = `<tr><td colspan="4" class="py-3 text-gray-400 text-xs text-center">Sin notas registradas</td></tr>`;
    } else {
      tbodyNotas.innerHTML = expediente.notas.map(n => `
        <tr class="border-b border-gray-50">
          <td class="py-2 font-medium text-gray-800">${n.Materia}</td>
          <td class="py-2 text-gray-600">${n.Semestre}</td>
          <td class="py-2 font-bold ${n.Nota_Definitiva < 10 ? 'text-red-600' : 'text-emerald-600'}">${n.Nota_Definitiva}</td>
          <td class="py-2 text-xs">${n.Condicion}</td>
        </tr>
      `).join('');
    }

    
    const tbodyFaltas = document.getElementById("perfil-tabla-faltas");
    if (expediente.faltas.length === 0) {
      tbodyFaltas.innerHTML = `<tr><td colspan="4" class="py-3 text-gray-400 text-xs text-center">Sin faltas registradas</td></tr>`;
    } else {
      tbodyFaltas.innerHTML = expediente.faltas.map(f => {
        const critica = f.Faltas_Acumuladas >= f.Limite_Faltas;
        return `
        <tr class="border-b border-gray-50">
          <td class="py-2 font-medium text-gray-800">${f.Materia}</td>
          <td class="py-2 font-bold ${critica ? 'text-red-600' : 'text-gray-600'}">${f.Faltas_Acumuladas}</td>
          <td class="py-2 text-gray-600">${f.Limite_Faltas}</td>
          <td class="py-2 text-xs">
            ${critica ? '<span class="text-red-600 font-semibold">Crítico</span>' : '<span class="text-emerald-600">Regular</span>'}
          </td>
        </tr>
        `;
      }).join('');
    }
  } catch (error) {
    console.error("Error cargando expediente:", error);
  }

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

// ---- 5i. FORM: NUEVO ESTUDIANTE ----
document.getElementById("btn-toggle-form-estudiante")?.addEventListener("click", () => {
  document.getElementById("panel-nuevo-estudiante").classList.toggle("hidden");
});

document.getElementById("form-nuevo-estudiante")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button[type="submit"]');
  
  const body = {
    Cedula: document.getElementById("nuevo-cedula").value.trim(),
    Nombres: document.getElementById("nuevo-nombres").value.trim(),
    Apellidos: document.getElementById("nuevo-apellidos").value.trim(),
    Edad: parseInt(document.getElementById("nuevo-edad").value, 10),
    Genero: document.getElementById("nuevo-genero").value,
    Carrera: document.getElementById("nuevo-carrera").value,
    Es_Regular: document.getElementById("nuevo-es-regular").value === 'true',
    Estrato_Socioeconomico: document.getElementById("nuevo-estrato").value,
    Situacion_Laboral: document.getElementById("nuevo-laboral").value === "true"
  };

  btn.disabled = true;
  btn.textContent = "Guardando...";

  try {
    await apiFetch("/api/estudiantes/", { method: "POST", body: JSON.stringify(body) });
    e.target.reset();
    document.getElementById("panel-nuevo-estudiante").classList.add("hidden");
    
    renderTablaEstudiantes();
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Guardar Estudiante";
  }
});


// 6. UTILITIES

function riesgoBadgeHTML(nivel) {
  const map = {
    Bajo: "bg-emerald-100 text-emerald-800",
    Medio: "bg-amber-100 text-amber-800",
    Alto: "bg-red-100 text-red-800",
  };
  const cls = map[nivel] || "bg-gray-100 text-gray-600";
  return `<span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${cls}">${nivel}</span>`;
}


// 7. INIT (ARRANQUE DEL SISTEMA Y ESCUCHA DE EVENTOS)

document.addEventListener("DOMContentLoaded", () => {
  
  document.getElementById("form-login")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    handleLogin(email, password);
  });

  document.getElementById("btn-mock-login")?.addEventListener("click", () => {
    setToken("mock_token_sin_backend");
    window.location.hash = "#dashboard";
  });

  document.getElementById("btn-logout")?.addEventListener("click", () => {
    clearToken();
    window.location.hash = "#login";
  });

  
  document.getElementById("btn-back-estudiantes")?.addEventListener("click", () => {
    window.location.hash = "#estudiantes";
  });

  
  window.addEventListener("hashchange", () => navigate(window.location.hash));
  if (!window.location.hash || window.location.hash === "#") {
    window.location.hash = estaAutenticado() ? "#dashboard" : "#login";
  } else {
    navigate(window.location.hash);
  }

 
  const modalFaq = document.getElementById("modal-faq");
  
  document.getElementById("btn-open-faq")?.addEventListener("click", (e) => {
    e.preventDefault();
    modalFaq.classList.remove("hidden");
  });

  document.getElementById("btn-close-faq")?.addEventListener("click", () => {
    modalFaq.classList.add("hidden");
  });

  modalFaq?.addEventListener("click", (e) => {
    if (e.target === modalFaq) {
      modalFaq.classList.add("hidden");
    }
  });

  
  document.getElementById('filtro-carrera-dashboard')?.addEventListener('change', () => {
    renderDashboard();
  });

  
  document.getElementById('filtro-carrera-estudiantes')?.addEventListener('change', () => {
    if (window.location.hash.includes("riesgo=")) window.location.hash = "#estudiantes";
    renderTablaEstudiantes();
  });

  document.getElementById('filtro-periodo-estudiantes')?.addEventListener('change', () => {
    if (window.location.hash.includes("riesgo=")) window.location.hash = "#estudiantes";
    renderTablaEstudiantes();
  });

  
  
  document.getElementById('btn-sync-dace')?.addEventListener('click', async (e) => {
    const btn = e.target;
    btn.textContent = "Ingestando 1,000 expedientes (DACE)...";
    btn.disabled = true;

    try {
      
      const responseArchivo = await fetch('lote_1000.json');
      if (!responseArchivo.ok) throw new Error("No se encontró el archivo lote_1000.json");
      const loteDACE = await responseArchivo.json();

      
      const response = await apiFetch("/api/estudiantes/dace-webhook", { 
        method: "POST", 
        body: JSON.stringify(loteDACE) 
      });
      
      alert(response.mensaje);
      renderDashboard(); 
    } catch (err) {
      alert("Error en la prueba de estrés: " + err.message);
    } finally {
      btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg> Simular Ingesta DACE (UNERG)`;
      btn.disabled = false;
    }
  });

  
  document.getElementById('filtro-riesgo-estudiantes')?.addEventListener('change', () => {
    if (window.location.hash.includes("riesgo=")) window.location.hash = "#estudiantes";
    renderTablaEstudiantes();
  });

 
  document.getElementById('sort-riesgo-btn')?.addEventListener('click', () => {
    
    if (ordenRiesgoActivo === 0) {
        ordenRiesgoActivo = -1;
    } else if (ordenRiesgoActivo === -1) {
        ordenRiesgoActivo = 1;
    } else {
        ordenRiesgoActivo = 0;
    }

    const iconos = {0: "↕", "-1": "↓", "1": "↑"};
    document.getElementById('sort-riesgo-btn').innerText = `Nivel de Alerta ${iconos[ordenRiesgoActivo]}`;

    renderTablaEstudiantes();
  });

  
  document.getElementById("btn-load-more")?.addEventListener("click", () => {
    limiteVisualEstudiantes += 100; 
    renderTablaEstudiantes(null, true); 
  });
});