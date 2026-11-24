/*
 * checkout.js — Trang thanh toán (mô phỏng).
 * Chỉ kiểm tra dữ liệu hợp lệ; KHÔNG tạo đơn hàng, KHÔNG gửi request nào ra ngoài, KHÔNG xóa giỏ hàng.
 */
(function () {
  'use strict';
  var A = window.Atino;
  var byId = A.byId;

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_RE = /^0\d{9}$/;

  var DISTRICTS = {
    'Hà Nội': ['Ba Đình', 'Cầu Giấy', 'Hoàn Kiếm', 'Đống Đa'],
    'TP. Hồ Chí Minh': ['Quận 1', 'Quận 3', 'Bình Thạnh', 'Thủ Đức'],
    'Đà Nẵng': ['Hải Châu', 'Thanh Khê', 'Sơn Trà']
  };

  var form = byId('checkout-form');
  var emptyBox = byId('checkout-empty');
  var message = byId('checkout-message');
  var cart = A.getCart();

  // Chỉ cho vào checkout khi giỏ hàng có sản phẩm
  if (cart.length === 0) {
    form.hidden = true;
    byId('checkout-summary').hidden = true;
    emptyBox.hidden = false;
    return;
  }
  emptyBox.hidden = true;

  /* ---------- Tóm tắt đơn hàng ---------- */

  byId('checkout-items').innerHTML = cart.map(function (line) {
    var p = A.getProduct(line.id);
    return '<li ' + A.idt('checkout-item-' + line.id) + '><span>' + A.esc(p.name) + ' × ' + line.qty + '</span>' +
      '<span>' + A.formatPrice(p.price * line.qty) + '</span></li>';
  }).join('');
  byId('checkout-total').textContent = A.formatPrice(A.cartTotal());

  /* ---------- Tỉnh / Quận ---------- */

  var province = byId('checkout-province');
  var district = byId('checkout-district');

  province.innerHTML = '<option value="">-- Chọn Tỉnh/Thành phố --</option>' +
    Object.keys(DISTRICTS).map(function (n) { return '<option value="' + n + '">' + n + '</option>'; }).join('');

  function fillDistricts() {
    var names = DISTRICTS[province.value] || [];
    district.innerHTML = '<option value="">-- Chọn Quận/Huyện --</option>' +
      names.map(function (n) { return '<option value="' + n + '">' + n + '</option>'; }).join('');
  }
  province.addEventListener('change', fillDistricts);
  fillDistricts();

  /* ---------- Validation ---------- */

  function setError(id, text) {
    byId(id + '-error').textContent = text || '';
    var input = byId(id);
    if (input) { if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid'); }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var name = byId('checkout-name').value.trim();
    var phone = byId('checkout-phone').value.trim();
    var email = byId('checkout-email').value.trim();
    var address = byId('checkout-address').value.trim();
    var payment = form.querySelector('input[name="payment"]:checked');

    var errs = {
      name: name ? '' : 'Vui lòng nhập họ tên.',
      phone: !phone ? 'Vui lòng nhập số điện thoại.'
        : !/^\d+$/.test(phone) ? 'Số điện thoại chỉ được chứa chữ số.'
        : !PHONE_RE.test(phone) ? 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.' : '',
      email: !email ? 'Vui lòng nhập email.' : !EMAIL_RE.test(email) ? 'Email không đúng định dạng.' : '',
      address: address ? '' : 'Vui lòng nhập địa chỉ.',
      payment: payment ? '' : 'Vui lòng chọn phương thức thanh toán.'
    };

    setError('checkout-name', errs.name);
    setError('checkout-phone', errs.phone);
    setError('checkout-email', errs.email);
    setError('checkout-address', errs.address);
    byId('checkout-payment-error').textContent = errs.payment;

    var hasError = Object.keys(errs).some(function (k) { return errs[k]; });
    if (hasError) {
      message.textContent = 'Thông tin đặt hàng chưa hợp lệ. Vui lòng kiểm tra lại các trường báo lỗi.';
      message.className = 'form-message is-error';
      return;
    }

    message.textContent = 'Thông tin đặt hàng hợp lệ. Đây là website mô phỏng kiểm thử, không có giao dịch thực tế.';
    message.className = 'form-message is-success';
  });
})();
