/*
 * auth.js — Đăng ký + Đăng nhập (đăng xuất nằm trong common.js).
 * Dữ liệu lưu ở localStorage: users (danh sách tài khoản), currentUser (người đang đăng nhập).
 * Lưu ý: mật khẩu lưu dạng văn bản thường vì đây chỉ là website mô phỏng phục vụ kiểm thử.
 */
(function () {
  'use strict';
  var A = window.Atino;
  var byId = A.byId;

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var NAME_RE = /^[A-Za-zÀ-ỹ\s]+$/;      // chỉ chữ cái (có dấu) và khoảng trắng
  var PHONE_RE = /^0\d{9}$/;               // 10 số, bắt đầu bằng 0

  function setError(fieldId, text) {
    var el = byId(fieldId + '-error');
    if (el) el.textContent = text || '';
    var input = byId(fieldId);
    if (input) {
      if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
    }
  }

  function showMessage(el, text, type) {
    el.textContent = text;
    el.className = 'form-message ' + (type === 'success' ? 'is-success' : 'is-error');
  }

  /* ---------- Đăng ký ---------- */

  function initRegister() {
    var form = byId('register-form');
    if (!form) return;
    var message = byId('register-message');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = byId('register-name').value.trim();
      var phone = byId('register-phone').value.trim();
      var email = byId('register-email').value.trim();
      var password = byId('register-password').value;
      var errors = 0;

      // Họ tên
      var nameErr = '';
      if (!name) nameErr = 'Vui lòng nhập họ tên.';
      else if (!NAME_RE.test(name)) nameErr = 'Họ tên không được chứa số hoặc ký tự đặc biệt.';
      setError('register-name', nameErr);

      // Số điện thoại
      var phoneErr = '';
      if (!phone) phoneErr = 'Vui lòng nhập số điện thoại.';
      else if (!/^\d+$/.test(phone)) phoneErr = 'Số điện thoại chỉ được chứa chữ số.';
      else if (!PHONE_RE.test(phone)) phoneErr = 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0.';
      setError('register-phone', phoneErr);

      // Email
      var emailErr = '';
      var users = A.getUsers();
      if (!email) emailErr = 'Vui lòng nhập email.';
      else if (!EMAIL_RE.test(email)) emailErr = 'Email không đúng định dạng.';
      else if (users.some(function (u) { return String(u.email).toLowerCase() === email.toLowerCase(); })) {
        emailErr = 'Email này đã được đăng ký.';
      }
      setError('register-email', emailErr);

      // Mật khẩu
      var passErr = '';
      if (!password) passErr = 'Vui lòng nhập mật khẩu.';
      else if (password.length < 8 || !/[A-Za-z]/.test(password) || !/\d/.test(password)) {
        passErr = 'Mật khẩu phải có ít nhất 8 ký tự, gồm cả chữ và số.';
      }
      setError('register-password', passErr);

      errors = [nameErr, phoneErr, emailErr, passErr].filter(Boolean).length;
      if (errors > 0) {
        showMessage(message, 'Đăng ký không thành công. Vui lòng kiểm tra lại các trường báo lỗi.', 'error');
        return;
      }

      users.push({ name: name, phone: phone, email: email, password: password });
      A.saveUsers(users);
      form.reset();
      showMessage(message, 'Đăng ký thành công. Bạn có thể đăng nhập bằng tài khoản vừa tạo.', 'success');
    });
  }

  /* ---------- Đăng nhập ---------- */

  function initLogin() {
    var form = byId('login-form');
    if (!form) return;
    var message = byId('login-message');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var account = byId('login-email').value.trim();
      var password = byId('login-password').value;

      var accErr = account ? '' : 'Vui lòng nhập email hoặc tên đăng nhập.';
      var passErr = password ? '' : 'Vui lòng nhập mật khẩu.';
      setError('login-email', accErr);
      setError('login-password', passErr);
      if (accErr || passErr) {
        showMessage(message, 'Đăng nhập không thành công. ' + [accErr, passErr].filter(Boolean).join(' '), 'error');
        return;
      }

      // Tên đăng nhập = email (không phân biệt hoa/thường) hoặc số điện thoại
      var user = A.getUsers().filter(function (u) {
        return String(u.email).toLowerCase() === account.toLowerCase() || u.phone === account;
      })[0];

      if (!user) {
        showMessage(message, 'Tài khoản không tồn tại.', 'error');
        return;
      }
      if (user.password !== password) {
        showMessage(message, 'Mật khẩu không chính xác.', 'error');
        return;
      }

      A.setCurrentUser(user);
      A.updateHeader();
      showMessage(message, 'Đăng nhập thành công. Đang chuyển về trang chủ...', 'success');
      setTimeout(function () { window.location.href = 'index.html'; }, 600);
    });

    var forgot = byId('forgot-password-link');
    if (forgot) {
      forgot.addEventListener('click', function (e) {
        e.preventDefault();
        showMessage(message, 'Chức năng quên mật khẩu chưa được hỗ trợ trong bản mô phỏng.', 'error');
      });
    }
  }

  initRegister();
  initLogin();
})();
