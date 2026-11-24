/*
 * cart.js — Trang giỏ hàng: tăng / giảm / xóa / xóa toàn bộ, tính thành tiền và tổng tiền.
 * Giỏ hàng lưu ở localStorage key "cart" (xem common.js).
 */
(function () {
  'use strict';
  var A = window.Atino;
  var byId = A.byId;

  var list = byId('cart-items');
  var content = byId('cart-content');
  var emptyEl = byId('cart-empty');
  var totalEl = byId('cart-total');
  var message = byId('cart-message');

  function showMessage(text) {
    message.textContent = text;
    message.className = text ? 'form-message is-error' : 'form-message';
  }

  function lineHtml(line) {
    var p = A.getProduct(line.id);
    var id = line.id;
    var variant = (line.size ? 'Size ' + line.size + ' · ' : '') + 'Màu ' + line.color;
    return '<li ' + A.idt('cart-item-' + id) + ' class="cart-item" data-product-id="' + id + '" data-quantity="' + line.qty + '">' +
      '<a class="cart-thumb" href="product-detail.html?id=' + id + '" tabindex="-1" aria-hidden="true"><img src="' + A.productImage(p, line.color) + '" alt="" width="90" height="108"></a>' +
      '<div class="cart-info">' +
      '<a ' + A.idt('cart-name-' + id) + ' class="cart-name" href="product-detail.html?id=' + id + '">' + A.esc(p.name) + '</a>' +
      '<p ' + A.idt('cart-variant-' + id) + ' class="cart-variant">' + A.esc(variant) + '</p>' +
      '<p ' + A.idt('cart-price-' + id) + ' class="cart-unit" data-price="' + p.price + '">' + A.formatPrice(p.price) + '</p>' +
      '</div>' +
      '<div class="qty-control" role="group" aria-label="Số lượng ' + A.esc(p.name) + '">' +
      '<button ' + A.idt('cart-decrease-' + id) + ' type="button" class="qty-btn" data-action="decrease" data-id="' + id + '" aria-label="Giảm số lượng"' + (line.qty <= 1 ? ' disabled' : '') + '>-</button>' +
      '<span ' + A.idt('cart-quantity-' + id) + ' class="qty-value">' + line.qty + '</span>' +
      '<button ' + A.idt('cart-increase-' + id) + ' type="button" class="qty-btn" data-action="increase" data-id="' + id + '" aria-label="Tăng số lượng"' + (line.qty >= p.stock ? ' disabled' : '') + '>+</button>' +
      '</div>' +
      '<p class="cart-line-total">Thành tiền: <strong ' + A.idt('cart-subtotal-' + id) + ' data-amount="' + (p.price * line.qty) + '">' + A.formatPrice(p.price * line.qty) + '</strong></p>' +
      '<button ' + A.idt('cart-remove-' + id) + ' type="button" class="link-btn danger" data-action="remove" data-id="' + id + '">Xóa</button>' +
      '</li>';
  }

  function render() {
    var cart = A.getCart();
    var isEmpty = cart.length === 0;
    emptyEl.hidden = !isEmpty;
    content.hidden = isEmpty;
    list.innerHTML = cart.map(lineHtml).join('');
    totalEl.textContent = A.formatPrice(A.cartTotal());
    totalEl.setAttribute('data-amount', String(A.cartTotal()));
    A.updateHeader();
  }

  list.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-action]');
    if (!btn || btn.disabled) return;
    var id = btn.getAttribute('data-id');
    var action = btn.getAttribute('data-action');
    var line = A.getCart().filter(function (l) { return l.id === id; })[0];
    if (!line) return;
    showMessage('');

    if (action === 'increase') {
      A.setCartQty(id, line.qty + 1);
    } else if (action === 'decrease') {
      A.setCartQty(id, line.qty - 1);
    } else if (action === 'remove') {
      A.removeFromCart(id);
    }
    render();
  });

  byId('cart-clear').addEventListener('click', function () {
    A.clearCart();
    showMessage('');
    render();
  });

  render();
})();
