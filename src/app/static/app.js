const state = {
  token: localStorage.getItem("token") || null,
  user: JSON.parse(localStorage.getItem("user") || "null"),
  cart: [],
  products: [],
  activeTab: "catalog",
};

// Toast notification helper
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.setAttribute("data-testid", "toast");
  const bg = type === "success" ? "bg-emerald-600" : "bg-rose-600";
  toast.className = `${bg} text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg toast-animate pointer-events-auto flex items-center justify-between gap-3 min-w-[240px]`;
  toast.innerHTML = `<span>${message}</span><button class="text-white/80 hover:text-white font-bold text-sm ml-2">&times;</button>`;
  
  toast.querySelector("button").onclick = () => toast.remove();
  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 4000);
}

// API client helper
async function api(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }

  const res = await fetch(endpoint, { ...options, headers });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "API request failed");
  }
  return data;
}

// UI State Updates
function updateAuthUI() {
  const userSection = document.getElementById("user-section");
  const btnOpenAuth = document.getElementById("btn-open-auth-modal");
  const btnNewProduct = document.getElementById("btn-open-new-product");
  const userDisplayName = document.getElementById("user-display-name");
  const userDisplayRole = document.getElementById("user-display-role");
  const mainNav = document.getElementById("main-nav");

  if (state.token && state.user) {
    userSection.classList.remove("hidden");
    userSection.classList.add("flex");
    btnOpenAuth.classList.add("hidden");
    mainNav.classList.remove("hidden");

    userDisplayName.textContent = state.user.full_name;
    userDisplayRole.textContent = state.user.role;

    if (state.user.role === "admin") {
      btnNewProduct.classList.remove("hidden");
    } else {
      btnNewProduct.classList.add("hidden");
    }
  } else {
    userSection.classList.add("hidden");
    userSection.classList.remove("flex");
    btnOpenAuth.classList.remove("hidden");
    mainNav.classList.add("hidden");
    btnNewProduct.classList.add("hidden");
    switchTab("catalog");
  }
}

function updateCartBadge() {
  const count = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  document.getElementById("cart-badge-count").textContent = count;
}

// Tab Switching
function switchTab(tab) {
  state.activeTab = tab;
  ["catalog", "orders", "analytics"].forEach((t) => {
    const view = document.getElementById(`view-${t}`);
    const navBtn = document.getElementById(`nav-btn-${t}`);
    if (t === tab) {
      view.classList.remove("hidden");
      if (navBtn) {
        navBtn.classList.add("bg-indigo-600", "text-white");
        navBtn.classList.remove("text-slate-400");
      }
    } else {
      view.classList.add("hidden");
      if (navBtn) {
        navBtn.classList.remove("bg-indigo-600", "text-white");
        navBtn.classList.add("text-slate-400");
      }
    }
  });

  if (tab === "orders") loadOrders();
  if (tab === "analytics") loadAnalytics();
}

// Products Catalog
async function loadProducts() {
  const category = document.getElementById("category-filter").value;
  const search = document.getElementById("search-input").value;

  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (search) params.append("search", search);

  try {
    const products = await api(`/api/products?${params.toString()}`);
    state.products = products;
    renderProducts(products);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderProducts(products) {
  const grid = document.getElementById("products-grid");
  if (!products.length) {
    grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500">No products match your criteria.</div>`;
    return;
  }

  grid.innerHTML = products.map((prod) => `
    <div data-testid="product-card" data-product-id="${prod.id}" class="bg-slate-950/50 rounded-2xl border border-slate-800 p-5 flex flex-col justify-between hover:border-slate-700 transition-all shadow-md">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300">${prod.category}</span>
          <span class="text-xs ${prod.stock > 0 ? "text-emerald-400" : "text-rose-400"} font-medium" data-testid="product-stock">
            ${prod.stock > 0 ? `${prod.stock} in stock` : "Out of stock"}
          </span>
        </div>
        <h3 data-testid="product-title" class="font-bold text-white text-base leading-snug">${prod.title}</h3>
        <p class="text-xs text-slate-400 mt-1 line-clamp-2">${prod.description || "High reliability component for professional operations."}</p>
        <div class="text-[11px] font-mono text-slate-500 mt-2">SKU: ${prod.sku}</div>
      </div>
      <div class="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-between">
        <span data-testid="product-price" class="text-lg font-bold text-indigo-400">$${prod.price.toFixed(2)}</span>
        <button
          data-testid="btn-add-to-cart-${prod.id}"
          onclick="addToCart(${prod.id})"
          ${prod.stock <= 0 ? "disabled" : ""}
          class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed text-white rounded-xl text-xs font-semibold shadow transition-all">
          ${prod.stock > 0 ? "Add to Cart" : "Sold Out"}
        </button>
      </div>
    </div>
  `).join("");
}

// Cart Logic
function addToCart(productId) {
  const prod = state.products.find((p) => p.id === productId);
  if (!prod) return;

  const existing = state.cart.find((item) => item.product_id === productId);
  if (existing) {
    if (existing.quantity >= prod.stock) {
      showToast("Cannot add more than available stock", "error");
      return;
    }
    existing.quantity += 1;
  } else {
    state.cart.push({
      product_id: prod.id,
      title: prod.title,
      price: prod.price,
      quantity: 1,
    });
  }

  updateCartBadge();
  renderCart();
  showToast(`Added ${prod.title} to cart`);
}

function removeFromCart(productId) {
  state.cart = state.cart.filter((item) => item.product_id !== productId);
  updateCartBadge();
  renderCart();
}

function renderCart() {
  const container = document.getElementById("cart-items-list");
  if (!state.cart.length) {
    container.innerHTML = `<div class="text-center py-10 text-xs text-slate-500">Your cart is empty.</div>`;
    updateCartTotals(0);
    return;
  }

  container.innerHTML = state.cart.map((item) => `
    <div data-testid="cart-item" class="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between gap-3">
      <div class="flex-1 min-w-0">
        <div class="text-xs font-semibold text-white truncate">${item.title}</div>
        <div class="text-[11px] text-slate-400 mt-0.5">$${item.price.toFixed(2)} &times; ${item.quantity}</div>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-indigo-400">$${(item.price * item.quantity).toFixed(2)}</span>
        <button onclick="removeFromCart(${item.product_id})" class="text-rose-400 hover:text-rose-300 text-xs px-1.5 py-0.5 rounded bg-rose-950/40">✕</button>
      </div>
    </div>
  `).join("");

  const subtotal = state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  updateCartTotals(subtotal);
}

function updateCartTotals(subtotal) {
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  document.getElementById("cart-subtotal").textContent = `$${subtotal.toFixed(2)}`;
  document.getElementById("cart-tax").textContent = `$${tax.toFixed(2)}`;
  document.getElementById("cart-total").textContent = `$${total.toFixed(2)}`;
  document.getElementById("btn-place-order").disabled = state.cart.length === 0;
}

// Orders Logic
async function loadOrders() {
  if (!state.token) return;
  try {
    const orders = await api("/api/orders");
    renderOrders(orders);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderOrders(orders) {
  const tbody = document.getElementById("orders-table-body");
  if (!orders.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-5 py-8 text-center text-slate-500 text-xs">No orders recorded yet.</td></tr>`;
    return;
  }

  const badgeColors = {
    PENDING: "bg-amber-950/60 text-amber-300 border-amber-800",
    PROCESSING: "bg-blue-950/60 text-blue-300 border-blue-800",
    SHIPPED: "bg-purple-950/60 text-purple-300 border-purple-800",
    DELIVERED: "bg-emerald-950/60 text-emerald-300 border-emerald-800",
    CANCELLED: "bg-rose-950/60 text-rose-300 border-rose-800",
  };

  tbody.innerHTML = orders.map((o) => `
    <tr data-testid="order-row-${o.id}" class="hover:bg-slate-900/40 transition-colors">
      <td class="px-5 py-4 font-mono font-medium text-white text-xs">#${o.id}</td>
      <td class="px-5 py-4">
        <div class="font-medium text-xs text-white">${o.user_email}</div>
        <div class="text-[11px] text-slate-400 truncate max-w-[200px]">${o.shipping_address}</div>
      </td>
      <td class="px-5 py-4 text-xs text-slate-300">
        ${o.items.map((i) => `${i.product_title} (${i.quantity})`).join(", ")}
      </td>
      <td class="px-5 py-4 font-bold text-xs text-indigo-300">$${o.total.toFixed(2)}</td>
      <td class="px-5 py-4">
        <span data-testid="order-status-badge" class="px-2.5 py-1 text-[11px] font-semibold uppercase rounded-full border ${badgeColors[o.status] || "bg-slate-800 text-slate-300"}">
          ${o.status}
        </span>
      </td>
      <td class="px-5 py-4 text-right">
        <div class="flex items-center justify-end gap-2">
          ${state.user?.role === "admin" && o.status !== "CANCELLED" ? `
            <select data-testid="select-status-update-${o.id}" id="select-status-${o.id}" class="bg-slate-900 border border-slate-700 text-[11px] rounded px-2 py-1 text-slate-200">
              <option value="PENDING" ${o.status === "PENDING" ? "selected" : ""}>PENDING</option>
              <option value="PROCESSING" ${o.status === "PROCESSING" ? "selected" : ""}>PROCESSING</option>
              <option value="SHIPPED" ${o.status === "SHIPPED" ? "selected" : ""}>SHIPPED</option>
              <option value="DELIVERED" ${o.status === "DELIVERED" ? "selected" : ""}>DELIVERED</option>
            </select>
            <button data-testid="btn-update-status-${o.id}" onclick="updateStatus(${o.id})" class="px-2 py-1 text-[11px] bg-indigo-600 hover:bg-indigo-500 text-white rounded">
              Update
            </button>
          ` : ""}
          ${o.status !== "CANCELLED" && o.status !== "DELIVERED" && o.status !== "SHIPPED" ? `
            <button data-testid="btn-cancel-order-${o.id}" onclick="cancelOrder(${o.id})" class="px-2 py-1 text-[11px] bg-rose-950/60 hover:bg-rose-900 border border-rose-800 text-rose-300 rounded">
              Cancel
            </button>
          ` : ""}
        </div>
      </td>
    </tr>
  `).join("");
}

async function updateStatus(orderId) {
  const sel = document.getElementById(`select-status-${orderId}`);
  const status = sel.value;
  try {
    await api(`/api/orders/${orderId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    showToast(`Order #${orderId} marked as ${status}`);
    loadOrders();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function cancelOrder(orderId) {
  try {
    await api(`/api/orders/${orderId}/cancel`, { method: "POST" });
    showToast(`Order #${orderId} has been cancelled`);
    loadOrders();
    loadProducts();
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Analytics
async function loadAnalytics() {
  if (!state.token) return;
  try {
    const data = await api("/api/analytics/summary");
    document.getElementById("metric-total-orders").textContent = data.total_orders;
    document.getElementById("metric-total-revenue").textContent = `$${data.total_revenue.toFixed(2)}`;
    document.getElementById("metric-pending-orders").textContent = data.pending_orders;
    document.getElementById("metric-low-stock").textContent = data.low_stock_products;
  } catch (err) {
    showToast(err.message, "error");
  }
}

// Event Listeners Setup
document.addEventListener("DOMContentLoaded", () => {
  updateAuthUI();
  loadProducts();

  // Navigation
  document.getElementById("nav-btn-catalog")?.addEventListener("click", () => switchTab("catalog"));
  document.getElementById("nav-btn-orders")?.addEventListener("click", () => switchTab("orders"));
  document.getElementById("nav-btn-analytics")?.addEventListener("click", () => switchTab("analytics"));
  document.getElementById("btn-refresh-orders")?.addEventListener("click", loadOrders);

  // Search & Filter
  document.getElementById("search-input").addEventListener("input", debounce(loadProducts, 250));
  document.getElementById("category-filter").addEventListener("change", loadProducts);

  // Auth modal controls
  const authModal = document.getElementById("auth-modal");
  const tabLogin = document.getElementById("tab-btn-login");
  const tabRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");
  const authError = document.getElementById("auth-error-msg");

  document.getElementById("btn-open-auth-modal").onclick = () => {
    authModal.classList.remove("hidden");
    authError.classList.add("hidden");
  };
  document.getElementById("btn-close-auth-modal").onclick = () => authModal.classList.add("hidden");

  tabLogin.onclick = () => {
    tabLogin.className = "flex-1 pb-3 text-sm font-semibold border-b-2 border-indigo-500 text-indigo-400";
    tabRegister.className = "flex-1 pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-white";
    formLogin.classList.remove("hidden");
    formRegister.classList.add("hidden");
    authError.classList.add("hidden");
  };

  tabRegister.onclick = () => {
    tabRegister.className = "flex-1 pb-3 text-sm font-semibold border-b-2 border-indigo-500 text-indigo-400";
    tabLogin.className = "flex-1 pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-white";
    formRegister.classList.remove("hidden");
    formLogin.classList.add("hidden");
    authError.classList.add("hidden");
  };

  formLogin.onsubmit = async (e) => {
    e.preventDefault();
    authError.classList.add("hidden");
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
      const res = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      state.token = res.access_token;
      state.user = res.user;
      localStorage.setItem("token", state.token);
      localStorage.setItem("user", JSON.stringify(state.user));
      authModal.classList.add("hidden");
      updateAuthUI();
      showToast(`Welcome back, ${state.user.full_name}!`);
    } catch (err) {
      authError.textContent = err.message;
      authError.classList.remove("hidden");
    }
  };

  formRegister.onsubmit = async (e) => {
    e.preventDefault();
    authError.classList.add("hidden");
    const full_name = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
      await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name, email, password }),
      });
      showToast("Account created! Please sign in.");
      tabLogin.click();
      document.getElementById("login-email").value = email;
      document.getElementById("login-password").value = password;
    } catch (err) {
      authError.textContent = err.message;
      authError.classList.remove("hidden");
    }
  };

  document.getElementById("btn-logout").onclick = () => {
    state.token = null;
    state.user = null;
    state.cart = [];
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    updateAuthUI();
    updateCartBadge();
    renderCart();
    showToast("Signed out successfully");
  };

  // Cart Drawer
  const cartDrawer = document.getElementById("cart-drawer");
  document.getElementById("cart-toggle-btn").onclick = () => {
    cartDrawer.classList.toggle("translate-x-full");
    renderCart();
  };
  document.getElementById("btn-close-cart").onclick = () => {
    cartDrawer.classList.add("translate-x-full");
  };

  document.getElementById("btn-place-order").onclick = async () => {
    if (!state.token) {
      showToast("Please log in to place an order", "error");
      document.getElementById("btn-open-auth-modal").click();
      return;
    }
    const address = document.getElementById("input-shipping-address").value.trim();
    if (!address) {
      showToast("Please enter a shipping address", "error");
      return;
    }

    try {
      const order = await api("/api/orders", {
        method: "POST",
        body: JSON.stringify({
          shipping_address: address,
          items: state.cart.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
        }),
      });
      state.cart = [];
      updateCartBadge();
      renderCart();
      cartDrawer.classList.add("translate-x-full");
      showToast(`Order #${order.id} placed successfully!`);
      loadProducts();
      switchTab("orders");
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  // Add Product Modal (Admin)
  const productModal = document.getElementById("new-product-modal");
  document.getElementById("btn-open-new-product").onclick = () => productModal.classList.remove("hidden");
  document.getElementById("btn-close-new-product-modal").onclick = () => productModal.classList.add("hidden");

  document.getElementById("form-create-product").onsubmit = async (e) => {
    e.preventDefault();
    const title = document.getElementById("prod-title").value;
    const sku = document.getElementById("prod-sku").value;
    const category = document.getElementById("prod-category").value;
    const price = parseFloat(document.getElementById("prod-price").value);
    const stock = parseInt(document.getElementById("prod-stock").value);
    const description = document.getElementById("prod-desc").value;

    try {
      await api("/api/products", {
        method: "POST",
        body: JSON.stringify({ title, sku, category, price, stock, description }),
      });
      productModal.classList.add("hidden");
      e.target.reset();
      showToast(`Product "${title}" added to catalog!`);
      loadProducts();
    } catch (err) {
      showToast(err.message, "error");
    }
  };
});

function debounce(fn, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), wait);
  };
}
