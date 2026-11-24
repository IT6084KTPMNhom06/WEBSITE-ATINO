/*
 * products.js — Trang danh sách: tìm kiếm, bộ lọc, sắp xếp.
 *
 * Quy tắc:
 *  - Tìm kiếm: tách từ khóa theo khoảng trắng, MỌI từ khóa phải khớp với tên / danh mục / màu / mã sản phẩm.
 *    Không phân biệt hoa-thường và dấu tiếng Việt. Ô tìm kiếm rỗng = hiện tất cả.
 *  - Bộ lọc: các giá trị trong CÙNG một nhóm là OR, giữa các nhóm khác nhau là AND.
 *    Bộ lọc chỉ có hiệu lực khi bấm "Áp dụng bộ lọc"; "Xóa bộ lọc" bỏ chọn mọi ô (giữ nguyên từ khóa tìm kiếm).
 *  - Sắp xếp: có hiệu lực ngay khi đổi lựa chọn.
 */
(function () {
  'use strict';
  var A = window.Atino;
  var byId = A.byId;

  var state = {
    q: '',
    filters: { category: [], color: [], size: [], price: [] },
    sort: 'newest'
  };

  var grid = byId('product-grid');
  var countEl = byId('search-result-count');
  var noResult = byId('no-search-result');
  var queryLabel = byId('search-query-label');
  var searchInput = byId('search-input');
  var sortSelect = byId('sort-select');

  /* ---------- Điều kiện khớp ---------- */

  function matchesSearch(p) {
    var tokens = A.normalizeText(state.q).split(/\s+/).filter(Boolean);
    if (tokens.length === 0) return true;
    var haystack = A.normalizeText([p.name, CATEGORIES[p.category], p.colors.join(' '), p.id].join(' '));
    return tokens.every(function (t) { return haystack.indexOf(t) !== -1; });
  }

  function matchesFilters(p) {
    var f = state.filters;
    if (f.category.length && f.category.indexOf(p.category) === -1) return false;
    if (f.color.length) {
      var ok = p.colors.some(function (name) { return f.color.indexOf(A.colorCode(name)) !== -1; });
      if (!ok) return false;
    }
    if (f.size.length) {
      var hasSize = p.sizes.some(function (s) { return f.size.indexOf(s) !== -1; });
      if (!hasSize) return false;
    }
    if (f.price.length) {
      var inRange = f.price.some(function (key) { return PRICE_RANGES[key] && PRICE_RANGES[key].test(p.price); });
      if (!inRange) return false;
    }
    return true;
  }

  function sortList(list) {
    var arr = list.slice();
    var byNewest = function (a, b) { return b.createdAt.localeCompare(a.createdAt) || a.id.localeCompare(b.id); };
    switch (state.sort) {
      case 'price-asc':
        arr.sort(function (a, b) { return a.price - b.price || a.id.localeCompare(b.id); });
        break;
      case 'price-desc':
        arr.sort(function (a, b) { return b.price - a.price || a.id.localeCompare(b.id); });
        break;
      case 'sale':
        // Sản phẩm đang giảm giá đứng trước, trong mỗi nhóm xếp theo mới nhất
        arr.sort(function (a, b) { return (Number(b.isSale) - Number(a.isSale)) || byNewest(a, b); });
        break;
      default:
        arr.sort(byNewest);
    }
    return arr;
  }

  /* ---------- Hiển thị ---------- */

  function render() {
    var list = sortList(PRODUCTS.filter(function (p) { return matchesSearch(p) && matchesFilters(p); }));
    grid.innerHTML = A.renderProductCards(list);
    countEl.textContent = 'Tìm thấy ' + list.length + ' sản phẩm';
    noResult.hidden = list.length !== 0;
    var q = state.q.trim();
    queryLabel.hidden = !q;
    queryLabel.textContent = q ? 'Kết quả cho "' + q + '"' : '';
  }

  function readFilterForm() {
    ['category', 'color', 'size', 'price'].forEach(function (group) {
      var checked = document.querySelectorAll('#filter-form input[name="' + group + '"]:checked');
      state.filters[group] = Array.prototype.map.call(checked, function (i) { return i.value; });
    });
  }

  function syncUrl() {
    if (!window.history || !history.replaceState) return;
    var params = new URLSearchParams();
    if (state.q.trim()) params.set('q', state.q.trim());
    if (state.sort !== 'newest') params.set('sort', state.sort);
    var qs = params.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }

  /* ---------- Sự kiện ---------- */

  byId('search-form').addEventListener('submit', function (e) {
    e.preventDefault(); // tìm ngay trên trang, không tải lại
    state.q = searchInput.value;
    syncUrl();
    render();
  });

  byId('filter-form').addEventListener('submit', function (e) {
    e.preventDefault();
    readFilterForm();
    render();
  });

  byId('clear-filter').addEventListener('click', function () {
    var boxes = document.querySelectorAll('#filter-form input[type="checkbox"]');
    Array.prototype.forEach.call(boxes, function (b) { b.checked = false; });
    readFilterForm();
    render();
  });

  sortSelect.addEventListener('change', function () {
    state.sort = sortSelect.value;
    syncUrl();
    render();
  });

  var filterToggle = byId('filter-toggle');
  var filterPanel = byId('filter-panel');
  filterToggle.addEventListener('click', function () {
    var open = filterPanel.classList.toggle('open');
    filterToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  /* ---------- Khởi tạo từ URL: ?q=...&group=ao|quan|phukien&category=jeans&sort=... ---------- */

  var params = new URLSearchParams(location.search);
  state.q = params.get('q') || '';
  searchInput.value = state.q;

  var sortParam = params.get('sort');
  if (['newest', 'price-asc', 'price-desc', 'sale'].indexOf(sortParam) !== -1) state.sort = sortParam;
  sortSelect.value = state.sort;

  var preset = [];
  if (CATEGORY_GROUPS[params.get('group')]) preset = CATEGORY_GROUPS[params.get('group')];
  if (CATEGORIES[params.get('category')]) preset = [params.get('category')];
  preset.forEach(function (c) {
    var box = byId('filter-category-' + c);
    if (box) box.checked = true;
  });

  readFilterForm();
  render();
})();
