/*
 * common.js — Tiện ích dùng chung cho mọi trang:
 *  - localStorage an toàn (users, currentUser, cart) + dữ liệu test mặc định
 *  - Header: số lượng giỏ hàng, trạng thái đăng nhập, đăng xuất, menu mobile
 *  - Giỏ hàng: thêm / cập nhật / xóa
 *  - Product card dùng chung (trang chủ + danh sách sản phẩm)
 *  - resetTestData()
 */
(function () {
  'use strict';

  var KEYS = { users: 'users', currentUser: 'currentUser', cart: 'cart' };
  var TEST_USER = { name: 'Test User', phone: '0900000000', email: 'test@example.com', password: 'Test123456' };

  /* ---------- localStorage an toàn ---------- */

  function readJSON(key, fallback) {
    try {
      var raw = window.localStorage.getItem(key);
      if (raw === null) return fallback;
      var value = JSON.parse(raw);
      return value === null || value === undefined ? fallback : value;
    } catch (e) {
      return fallback; // dữ liệu hỏng -> dùng giá trị mặc định
    }
  }

  function writeJSON(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      return false;
    }
  }

  /** Khởi tạo dữ liệu mặc định nếu chưa có (lần chạy đầu hoặc sau reset). */
  function initStorage() {
    if (!Array.isArray(readJSON(KEYS.users, null))) writeJSON(KEYS.users, [TEST_USER]);
    if (!Array.isArray(readJSON(KEYS.cart, null))) writeJSON(KEYS.cart, []);
    try {
      if (window.localStorage.getItem(KEYS.currentUser) === null) writeJSON(KEYS.currentUser, null);
    } catch (e) { /* bỏ qua */ }
  }

  /** Dùng cho môi trường test: xóa users, currentUser, cart rồi khởi tạo lại mặc định. */
  function resetTestData() {
    try {
      window.localStorage.removeItem(KEYS.users);
      window.localStorage.removeItem(KEYS.currentUser);
      window.localStorage.removeItem(KEYS.cart);
    } catch (e) { /* bỏ qua */ }
    initStorage();
  }

  /* ---------- Tài khoản ---------- */

  function getUsers() { var u = readJSON(KEYS.users, []); return Array.isArray(u) ? u : []; }
  function saveUsers(users) { writeJSON(KEYS.users, users); }
  function getCurrentUser() {
    var u = readJSON(KEYS.currentUser, null);
    return u && typeof u === 'object' && u.email ? u : null;
  }
  function setCurrentUser(user) {
    // Không lưu mật khẩu vào currentUser
    writeJSON(KEYS.currentUser, user ? { name: user.name, email: user.email, phone: user.phone } : null);
  }

  /* ---------- Tiện ích hiển thị ---------- */

  function formatPrice(n) {
    return String(Math.round(Number(n) || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + 'đ';
  }

  /** Chuẩn hóa chuỗi để tìm kiếm: không phân biệt hoa/thường và dấu tiếng Việt. */
  function normalizeText(s) {
    return String(s || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/đ/g, 'd')
      .trim();
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /** Thuộc tính id + data-testid giống nhau (dùng khi tạo HTML động). */
  function idt(id) { return 'id="' + id + '" data-testid="' + id + '"'; }

  function colorCode(name) {
    for (var i = 0; i < COLORS.length; i++) if (COLORS[i].name === name) return COLORS[i].code;
    return 'black';
  }

  function getProduct(id) {
    for (var i = 0; i < PRODUCTS.length; i++) if (PRODUCTS[i].id === id) return PRODUCTS[i];
    return null;
  }

  /* ---------- Ảnh sản phẩm: SVG nội bộ, không cần Internet ---------- */

  var SHAPES = {
    tee: 'M95 62 L135 46 Q150 72 165 46 L205 62 L252 108 L224 138 L205 120 L205 300 L95 300 L95 120 L76 138 L48 108 Z',
    shirt: 'M95 58 L135 44 Q150 66 165 44 L205 58 L262 252 L232 260 L205 156 L205 306 L95 306 L95 156 L68 260 L38 252 Z',
    pants: 'M104 52 L196 52 L206 122 L224 312 L173 312 L150 156 L127 312 L76 312 L94 122 Z'
  };

  function productImage(product, colorName) {
    var hex = '#22262b';
    for (var i = 0; i < COLORS.length; i++) if (COLORS[i].name === (colorName || product.color)) hex = COLORS[i].hex;
    var stroke = 'rgba(0,0,0,0.28)';
    var body = '';
    var cat = product.category;
    if (cat === 'jeans' || cat === 'quanau' || cat === 'kaki') {
      body = '<path d="' + SHAPES.pants + '" fill="' + hex + '" stroke="' + stroke + '" stroke-width="3" stroke-linejoin="round"/>' +
        '<path d="M104 70 L196 70 M150 70 L150 156" stroke="' + stroke + '" stroke-width="2" fill="none"/>';
    } else if (cat === 'phukien') {
      body = '<ellipse cx="150" cy="180" rx="84" ry="84" fill="none" stroke="' + hex + '" stroke-width="22"/>' +
        '<rect x="132" y="86" width="36" height="28" rx="3" fill="#b9bfc6" stroke="' + stroke + '" stroke-width="2"/>';
    } else {
      var shape = cat === 'somi' ? SHAPES.shirt : SHAPES.tee;
      body = '<path d="' + shape + '" fill="' + hex + '" stroke="' + stroke + '" stroke-width="3" stroke-linejoin="round"/>';
      if (cat === 'polo' || cat === 'somi') {
        body += '<path d="M135 46 L150 92 L165 46 M150 92 L150 200" stroke="' + stroke + '" stroke-width="2.5" fill="none"/>';
      }
    }
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 360"><rect width="300" height="360" fill="#e8ecf0"/>' + body + '</svg>';
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }

  /* ---------- Giỏ hàng ---------- */
  // Mỗi sản phẩm chỉ có 1 dòng trong giỏ: { id, qty, size, color }

  function getCart() {
    var raw = readJSON(KEYS.cart, []);
    if (!Array.isArray(raw)) return [];
    return raw.filter(function (line) {
      var p = line && getProduct(line.id);
      return p && p.stock > 0 && Number(line.qty) >= 1;
    }).map(function (line) {
      var p = getProduct(line.id);
      return { id: line.id, qty: Math.min(Math.floor(Number(line.qty)), p.stock), size: line.size || '', color: line.color || p.color };
    });
  }

  function saveCart(cart) { writeJSON(KEYS.cart, cart); updateHeader(); }
  function cartCount() { return getCart().reduce(function (sum, l) { return sum + l.qty; }, 0); }
  function cartTotal() {
    return getCart().reduce(function (sum, l) { return sum + getProduct(l.id).price * l.qty; }, 0);
  }

  /**
   * Thêm sản phẩm vào giỏ.
   * Trả về { ok, message } — ok=false nếu không thêm được.
   */
  function addToCart(id, qty, size, color) {
    var p = getProduct(id);
    if (!p) return { ok: false, message: 'Không tìm thấy sản phẩm.' };
    if (p.stock <= 0) return { ok: false, message: 'Sản phẩm đã hết hàng.' };
    qty = Math.floor(Number(qty));
    if (!(qty >= 1)) return { ok: false, message: 'Số lượng không hợp lệ.' };
    if (p.sizes.length > 0 && !size) return { ok: false, message: 'Vui lòng chọn size.' };

    var cart = getCart();
    var line = null;
    for (var i = 0; i < cart.length; i++) if (cart[i].id === id) line = cart[i];

    var current = line ? line.qty : 0;
    if (current >= p.stock) {
      return { ok: false, message: 'Giỏ hàng đã có tối đa số lượng còn trong kho (' + p.stock + ').' };
    }
    var next = current + qty;
    var capped = false;
    if (next > p.stock) { next = p.stock; capped = true; }

    if (line) {
      line.qty = next; line.size = size || line.size; line.color = color || line.color;
    } else {
      cart.push({ id: id, qty: next, size: size || '', color: color || p.color });
    }
    saveCart(cart);
    return {
      ok: true,
      message: capped
        ? 'Đã thêm vào giỏ hàng. Số lượng được giới hạn ở mức còn trong kho (' + p.stock + ').'
        : 'Đã thêm vào giỏ hàng.'
    };
  }

  function setCartQty(id, qty) {
    var p = getProduct(id);
    var cart = getCart();
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].id === id) { cart[i].qty = Math.max(1, Math.min(qty, p.stock)); }
    }
    saveCart(cart);
  }

  function removeFromCart(id) {
    saveCart(getCart().filter(function (l) { return l.id !== id; }));
  }

  function clearCart() { saveCart([]); }

  /* ---------- Header ---------- */

  function byId(id) { return document.getElementById(id); }

  function updateHeader() {
    var countEl = byId('cart-count');
    if (countEl) countEl.textContent = String(cartCount());

    var user = getCurrentUser();
    var loginLink = byId('login-link');
    var registerLink = byId('register-link');
    var logoutBtn = byId('logout-button');
    var nameEl = byId('user-name');
    if (loginLink) loginLink.hidden = !!user;
    if (registerLink) registerLink.hidden = !!user;
    if (logoutBtn) logoutBtn.hidden = !user;
    if (nameEl) {
      nameEl.hidden = !user;
      nameEl.textContent = user ? 'Xin chào, ' + user.name : '';
    }
  }

  var toastTimer = null;
  function showToast(message) {
    var el = byId('toast');
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.hidden = true; }, 2500);
  }

  /* ---------- Product card dùng chung ---------- */

  function renderProductCard(p) {
    var soldOut = p.stock <= 0;
    var detailUrl = 'product-detail.html?id=' + p.id;
    var badges = '';
    if (p.isSale) badges += '<span ' + idt('product-badge-sale-' + p.id) + ' class="badge badge-sale">SALE</span>';
    if (p.isNew) badges += '<span ' + idt('product-badge-new-' + p.id) + ' class="badge badge-new">Mới</span>';
    if (soldOut) badges += '<span ' + idt('product-badge-soldout-' + p.id) + ' class="badge badge-soldout">Hết hàng</span>';

    return '<article ' + idt('product-card-' + p.id) + ' class="product-card" data-product-id="' + p.id + '"' +
      ' data-category="' + p.category + '" data-price="' + p.price + '">' +
      '<a ' + idt('product-image-' + p.id) + ' class="product-media" href="' + detailUrl + '" aria-label="Xem ' + esc(p.name) + '">' +
      '<img src="' + productImage(p) + '" alt="' + esc(p.name) + '" width="300" height="360" loading="eager">' +
      '<span class="badges">' + badges + '</span></a>' +
      '<div class="product-info">' +
      '<h3 class="product-title"><a ' + idt('product-name-' + p.id) + ' href="' + detailUrl + '">' + esc(p.name) + '</a></h3>' +
      '<p class="product-meta">' + esc(CATEGORIES[p.category]) + ' · ' + esc(p.colors.join(', ')) + '</p>' +
      '<p class="product-prices"><span ' + idt('product-price-' + p.id) + ' class="price-current" data-price="' + p.price + '">' + formatPrice(p.price) + '</span>' +
      (p.oldPrice ? ' <del ' + idt('product-old-price-' + p.id) + ' class="price-old">' + formatPrice(p.oldPrice) + '</del>' : '') + '</p>' +
      '<div class="product-actions">' +
      '<a ' + idt('product-detail-' + p.id) + ' class="btn btn-outline" href="' + detailUrl + '">Xem chi tiết</a>' +
      '<button ' + idt('product-add-' + p.id) + ' class="btn btn-primary" type="button" data-add-to-cart="' + p.id + '"' + (soldOut ? ' disabled' : '') + '>' +
      (soldOut ? 'Hết hàng' : 'Thêm vào giỏ') + '</button>' +
      '</div></div></article>';
  }

  function renderProductCards(list) {
    return list.map(renderProductCard).join('');
  }

  /* ---------- Gắn sự kiện toàn cục ---------- */

  function bindGlobalHandlers() {
    // "Thêm vào giỏ" từ product card: dùng size đầu tiên và màu chính làm mặc định
    document.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('[data-add-to-cart]') : null;
      if (!btn) return;
      var p = getProduct(btn.getAttribute('data-add-to-cart'));
      if (!p) return;
      var result = addToCart(p.id, 1, p.sizes[0] || '', p.color);
      showToast(result.ok ? 'Đã thêm "' + p.name + '" vào giỏ hàng.' : result.message);
    });

    var logoutBtn = byId('logout-button');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', function () {
        setCurrentUser(null); // currentUser = null, giữ nguyên giỏ hàng
        updateHeader();
        if (/(^|\/)checkout\.html$/.test(location.pathname) === false) showToast('Bạn đã đăng xuất.');
      });
    }

    var menuToggle = byId('menu-toggle');
    var nav = byId('main-nav');
    if (menuToggle && nav) {
      menuToggle.addEventListener('click', function () {
        var open = nav.classList.toggle('open');
        menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    var resetBtn = byId('reset-test-data');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        resetTestData();
        window.location.reload();
      });
    }
  }

  /* ---------- Khởi động ---------- */

  initStorage();
  bindGlobalHandlers();
  updateHeader();

  window.resetTestData = resetTestData;
  window.Atino = {
    KEYS: KEYS, TEST_USER: TEST_USER,
    getUsers: getUsers, saveUsers: saveUsers, getCurrentUser: getCurrentUser, setCurrentUser: setCurrentUser,
    getProduct: getProduct, productImage: productImage, colorCode: colorCode,
    formatPrice: formatPrice, normalizeText: normalizeText, esc: esc, idt: idt, byId: byId,
    getCart: getCart, cartCount: cartCount, cartTotal: cartTotal,
    addToCart: addToCart, setCartQty: setCartQty, removeFromCart: removeFromCart, clearCart: clearCart,
    updateHeader: updateHeader, showToast: showToast,
    renderProductCard: renderProductCard, renderProductCards: renderProductCards,
    resetTestData: resetTestData
  };
})();
