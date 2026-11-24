/*
 * home.js — Trang chủ: đổ sản phẩm vào 3 khu vực (mỗi sản phẩm chỉ xuất hiện 1 lần để ID không bị trùng).
 *  - Sale: mọi sản phẩm đang giảm giá
 *  - Mới: sản phẩm mới nhưng không sale
 *  - Nổi bật: sản phẩm nổi bật, không sale, không mới
 * Mỗi khu vực hiện tối đa 4 sản phẩm; danh sách đầy đủ ở trang products.html.
 */
(function () {
  'use strict';
  var A = window.Atino;
  var LIMIT = 4;

  function newestFirst(a, b) { return b.createdAt.localeCompare(a.createdAt); }

  var sale = PRODUCTS.filter(function (p) { return p.isSale; }).sort(newestFirst).slice(0, LIMIT);
  var fresh = PRODUCTS.filter(function (p) { return p.isNew && !p.isSale; }).sort(newestFirst).slice(0, LIMIT);
  var featured = PRODUCTS.filter(function (p) { return p.isFeatured && !p.isSale && !p.isNew; }).sort(newestFirst).slice(0, LIMIT);

  A.byId('sale-products').innerHTML = A.renderProductCards(sale);
  A.byId('new-products').innerHTML = A.renderProductCards(fresh);
  A.byId('featured-products').innerHTML = A.renderProductCards(featured);

  // Ảnh hero (SVG nội bộ)
  var picks = ['SP001', 'SP013', 'SP020'];
  A.byId('hero-pics').innerHTML = picks.map(function (id) {
    var p = A.getProduct(id);
    return '<img src="' + A.productImage(p) + '" alt="" width="300" height="360">';
  }).join('');
})();
