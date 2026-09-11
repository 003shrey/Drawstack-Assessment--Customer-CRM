const $ = (selector) => document.querySelector(selector);

function formatDate(value) {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function statusClass(status) {
  if (status === "Open") return "status-open";
  if (status === "Closed") return "status-closed";
  return "status-progress";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

async function loadTickets() {
  const params = new URLSearchParams();
  const search = $("#search")?.value.trim();
  const status = $("#status")?.value;

  if (search) params.set("search", search);
  if (status) params.set("status", status);

  const response = await fetch(`/api/tickets?${params}`);
  const tickets = await response.json();

  const list = $("#ticket-list");
  if (!list) return;

  if (!tickets.length) {
    list.innerHTML = `<div class="rounded-xl bg-slate-50 p-8 text-center text-slate-500">No tickets found.</div>`;
    return;
  }

  list.innerHTML = tickets.map((ticket) => `
    <a href="/tickets/${encodeURIComponent(ticket.ticket_id)}"
       class="block rounded-xl border border-slate-200 p-4 transition hover:-translate-y-0.5 hover:border-cyan-300 hover:shadow-md">
      <div class="flex flex-col justify-between gap-3 md:flex-row md:items-center">
        <div class="min-w-0">
          <div class="mb-1 flex flex-wrap items-center gap-2">
            <span class="font-bold text-cyan-700">${escapeHtml(ticket.ticket_id)}</span>
            <span class="status ${statusClass(ticket.status)}">${escapeHtml(ticket.status)}</span>
          </div>
          <h3 class="truncate text-lg font-bold">${escapeHtml(ticket.subject)}</h3>
          <p class="text-sm text-slate-500">${escapeHtml(ticket.customer_name)}</p>
        </div>
        <time class="text-sm text-slate-400">${formatDate(ticket.created_at)}</time>
      </div>
    </a>
  `).join("");

  loadStats(tickets);
}

async function loadStats(currentTickets) {
  const stats = $("#stats");
  if (!stats) return;

  const counts = {
    Open: currentTickets.filter((ticket) => ticket.status === "Open").length,
    "In Progress": currentTickets.filter((ticket) => ticket.status === "In Progress").length,
    Closed: currentTickets.filter((ticket) => ticket.status === "Closed").length,
  };

  stats.innerHTML = Object.entries(counts).map(([label, count]) => `
    <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p class="text-xs font-bold uppercase tracking-wider text-slate-400">${label}</p>
      <p class="mt-2 text-3xl font-black">${count}</p>
    </div>
  `).join("");
}

async function createTicket(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const error = $("#form-error");
  const payload = Object.fromEntries(new FormData(form));

  const response = await fetch("/api/tickets", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    error.textContent = data.detail || "Unable to create ticket.";
    error.classList.remove("hidden");
    return;
  }

  const ticket = await response.json();
  window.location.href = `/tickets/${ticket.ticket_id}`;
}

async function loadDetail() {
  const container = $("#ticket-content");
  if (!container) return;

  const response = await fetch(`/api/tickets/${encodeURIComponent(window.TICKET_ID)}`);
  if (!response.ok) {
    container.innerHTML = `<div class="rounded-xl bg-red-50 p-5 text-red-700">Ticket not found.</div>`;
    return;
  }

  const ticket = await response.json();

  container.innerHTML = `
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-col justify-between gap-4 md:flex-row md:items-start">
        <div>
          <p class="font-bold text-cyan-700">${escapeHtml(ticket.ticket_id)}</p>
          <h1 class="mt-2 text-3xl font-black">${escapeHtml(ticket.subject)}</h1>
          <p class="mt-2 text-slate-500">${escapeHtml(ticket.customer_name)} · ${escapeHtml(ticket.customer_email)}</p>
        </div>
        <span class="status ${statusClass(ticket.status)}">${escapeHtml(ticket.status)}</span>
      </div>
      <div class="mt-7 rounded-xl bg-slate-50 p-5 whitespace-pre-wrap text-slate-700">${escapeHtml(ticket.description)}</div>
    </div>

    <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="text-xl font-black">Update ticket</h2>
      <form id="update-form" class="mt-4 space-y-4">
        <label class="label">Status
          <select name="status" class="field">
            ${["Open", "In Progress", "Closed"].map((value) =>
              `<option ${value === ticket.status ? "selected" : ""}>${value}</option>`
            ).join("")}
          </select>
        </label>
        <label class="label">Add note
          <textarea name="notes" class="field min-h-28" placeholder="Write an internal note..."></textarea>
        </label>
        <p id="update-error" class="hidden rounded-xl bg-red-50 p-3 text-sm text-red-700"></p>
        <button class="rounded-xl bg-slate-900 px-5 py-3 font-bold text-white hover:bg-cyan-700">Save update</button>
      </form>
    </div>

    <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 class="text-xl font-black">Notes</h2>
      <div class="mt-4 space-y-3">
        ${ticket.notes.length
          ? ticket.notes.map((note) => `
            <div class="rounded-xl bg-slate-50 p-4">
              <p class="whitespace-pre-wrap text-slate-700">${escapeHtml(note.note_text)}</p>
              <time class="mt-2 block text-xs text-slate-400">${formatDate(note.created_at)}</time>
            </div>
          `).join("")
          : `<p class="text-slate-500">No notes yet.</p>`}
      </div>
    </div>
  `;

  $("#update-form").addEventListener("submit", updateTicket);
}

async function updateTicket(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const error = $("#update-error");
  const payload = Object.fromEntries(new FormData(form));

  const response = await fetch(`/api/tickets/${encodeURIComponent(window.TICKET_ID)}`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const data = await response.json();
    error.textContent = data.detail || "Unable to update ticket.";
    error.classList.remove("hidden");
    return;
  }

  await loadDetail();
}

document.addEventListener("DOMContentLoaded", () => {
  if ($("#ticket-list")) {
    loadTickets();
    $("#search").addEventListener("input", loadTickets);
    $("#status").addEventListener("change", loadTickets);
  }

  if ($("#create-form")) {
    $("#create-form").addEventListener("submit", createTicket);
  }

  if ($("#ticket-content")) {
    loadDetail();
  }
});
