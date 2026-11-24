/*
 * product-detail.js — Trang chi tiết: chọn màu, size, số lượng; thêm vào giỏ / mua ngay.
 * URL: product-detail.html?id=SP001
 */
(function () {
  'use strict';
  var A = window.Atino;
  var byId = A.byId;

  var id = new URLSearchParams(location.search).get('id');
  var product = id ? A.getProduct(id) : null;

  var content = byId('detail-content');
  var notFound = byId('detail-not-found');

  if (!product) {
    content.hidden = true;
    notFound.hidden = false;
    return;
  }
  notFound.hidden = true;
  content.hidden = false;

  var message = byId('detail-message');
  var qtyInput = byId('quantity-input');
  var state = { color: product.colors[0], size: '' };

  function showMessage(text, type) {
    message.textContent = text;
    message.className = 'form-message ' + (type === 'success' ? 'is-success' : 'is-error');
  }

  /* ---------- Thông tin cơ bản ---------- */

  document.title = product.name + ' — Atino Mock';
  byId('detail-product-name').textContent = product.name;
  byId('detail-product-code').textContent = product.id;
  byId('detail-product-category').textContent = CATEGORIES[product.category];
  byId('detail-product-price').textContent = A.formatPrice(product.price);
  byId('detail-product-price').setAttribute('data-price', product.price);

  var oldPrice = byId('detail-product-old-price');
  if (product.oldPrice) { oldPrice.textContent = A.formatPrice(product.oldPrice); oldPrice.hidden = false; }
  byId('detail-sale-badge').hidden = !product.isSale;
  byId('detail-description').textContent = product.description;

  var stock = byId('detail-stock-status');
  if (product.stock > 0) {
    stock.textContent = 'Còn hàng (' + product.stock + ' sản phẩm)';
    stock.className = 'stock-status in-stock';
  } else {
    stock.textContent = 'Hết hàng';
    stock.className = 'stock-status out-of-stock';
  }

  var image = byId('detail-image');
  function updateImage() {
    image.src = A.productImage(product, state.color);
    image.alt = product.name + ' - màu ' + state.color;
  }

  /* ---------- Chọn màu ---------- */

  var colorGroup = byId('detail-product-color');
  var colorLabel = byId('detail-selected-color');

  function renderColors() {
    colorGroup.innerHTML = product.colors.map(function (name) {
      var code = A.colorCode(name);
      var selected = name === state.color;
      return '<button ' + A.idt('color-option-' + code) + ' type="button" class="option-btn" role="radio"' +
        ' aria-checked="' + selected + '" data-value="' + name + '">' + name + '</button>';
    }).join('');
    colorLabel.textContent = state.color;
    colorGroup.setAttribute('data-selected', state.color);
    updateImage();
  }

  colorGroup.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-value]');
    if (!btn) return;
    state.color = btn.getAttribute('data-value');
    renderColors();
  });

  /* ---------- Chọn size ---------- */

  var sizeGroup = byId('detail-product-size');
  var sizeLabel = byId('detail-selected-size');

  function renderSizes() {
    if (product.sizes.length === 0) {
      sizeGroup.innerHTML = '<span id="detail-size-free" data-testid="detail-size-free">Free size (không cần chọn size)</span>';
      sizeLabel.textContent = 'Free size';
      return;
    }
    sizeGroup.innerHTML = product.sizes.map(function (s) {
      return '<button ' + A.idt('size-option-' + s.toLowerCase()) + ' type="button" class="option-btn" role="radio"' +
        ' aria-checked="' + (s === state.size) + '" data-value="' + s + '">' + s + '</button>';
    }).join('');
    sizeLabel.textContent = state.size || 'Chưa chọn';
    sizeGroup.setAttribute('data-selected', state.size);
  }

  sizeGroup.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-value]');
    if (!btn) return;
    state.size = btn.getAttribute('data-value');
    renderSizes();
  });

  /* ---------- Số lượng: 1 <= số lượng <= stock ---------- */

  function clampQuantity() {
    var n = Math.floor(Number(qtyInput.value));
    if (!(n >= 1)) {
      qtyInput.value = '1';
      showMessage('Số lượng tối thiểu là 1.', 'error');
    } else if (product.stock > 0 && n > product.stock) {
      qtyInput.value = String(product.stock);
      showMessage('Chỉ còn ' + product.stock + ' sản phẩm trong kho.', 'error');
    } else {
      qtyInput.value = String(n);
    }
  }

  qtyInput.setAttribute('max', String(Math.max(product.stock, 1)));
  qtyInput.addEventListener('change', clampQuantity);

  byId('quantity-decrease').addEventListener('click', function () {
    var n = Math.floor(Number(qtyInput.value)) || 1;
    if (n <= 1) { qtyInput.value = '1'; showMessage('Số lượng tối thiểu là 1.', 'error'); return; }
    qtyInput.value = String(n - 1);
    message.textContent = ''; message.className = 'form-message';
  });

  byId('quantity-increase').addEventListener('click', function () {
    var n = Math.floor(Number(qtyInput.value)) || 1;
    if (n >= product.stock) {
      qtyInput.value = String(Math.max(product.stock, 1));
      showMessage('Chỉ còn ' + product.stock + ' sản phẩm trong kho.', 'error');
      return;
    }
    qtyInput.value = String(n + 1);
    message.textContent = ''; message.className = 'form-message';
  });

  /* ---------- Thêm vào giỏ / Mua ngay ---------- */

  /** Kiểm tra dữ liệu rồi thêm vào giỏ. Trả về true nếu thành công. */
  function submitToCart() {
    var n = Number(qtyInput.value);
    if (!Number.isInteger(n) || n < 1) { showMessage('Số lượng không hợp lệ. Tối thiểu là 1.', 'error'); return false; }
    if (n > product.stock) { showMessage('Chỉ còn ' + product.stock + ' sản phẩm trong kho.', 'error'); return false; }
    var result = A.addToCart(product.id, n, state.size, state.color);
    showMessage(result.message, result.ok ? 'success' : 'error');
    return result.ok;
  }

  if (product.stock <= 0) {
    byId('add-to-cart').disabled = true;
    byId('buy-now').disabled = true;
    qtyInput.disabled = true;
    byId('quantity-decrease').disabled = true;
    byId('quantity-increase').disabled = true;
    showMessage('Sản phẩm này hiện đã hết hàng.', 'error');
  }

  byId('add-to-cart').addEventListener('click', submitToCart);
  byId('buy-now').addEventListener('click', function () {
    if (submitToCart()) window.location.href = 'checkout.html';
  });

  renderColors();
  renderSizes();
})();
