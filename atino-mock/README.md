# Atino Mock — Website thời trang nam mô phỏng để kiểm thử Selenium

Website tĩnh (HTML + CSS + JavaScript thuần), không backend, không cần Internet. Dữ liệu tài khoản, trạng thái đăng nhập và giỏ hàng lưu trong `localStorage`. **Không có giao dịch hay đơn hàng thật.**

## 1. Cách chạy

Chọn một cách:

```bash
# Python
cd atino-mock && python -m http.server 5500      # mở http://localhost:SSS5500/index.html

# Node
npx serve atino-mock

# VS Code: cài Live Server -> chuột phải index.html -> Open with Live Server
```

Mở trực tiếp bằng `file://` cũng chạy được, nhưng nên dùng web server để `localStorage` ổn định giữa các trình duyệt.

## 2. Cấu trúc thư mục

```text
atino-mock/
├── index.html  login.html  register.html  products.html
├── product-detail.html  cart.html  checkout.html
├── css/   style.css  auth.css  products.css  cart.css  checkout.css
├── js/    data.js  common.js  auth.js  products.js
│          product-detail.js  cart.js  checkout.js  home.js
└── assets/images/   (trống: ảnh sản phẩm là SVG tạo bằng JS trong common.js)
```

## 3. Tài khoản test

```text
Email:    test@example.com
Password: Test123456
```

Tự tạo ở lần chạy đầu. Đăng nhập bằng email hoặc số điện thoại (`0900000000`). Có thể tạo thêm tài khoản ở trang Đăng ký.

## 4. Chức năng

| Nhóm | Hành vi |
|---|---|
| Đăng ký | Họ tên (chỉ chữ + khoảng trắng), SĐT (10 số, bắt đầu 0), email đúng định dạng và chưa tồn tại (không phân biệt hoa/thường), mật khẩu ≥ 8 ký tự có cả chữ và số. Thành công thì lưu `users`, **không** tự đăng nhập. |
| Đăng nhập | Báo lỗi riêng cho: bỏ trống, tài khoản không tồn tại, sai mật khẩu. Thành công thì lưu `currentUser`, chuyển về trang chủ sau ~0,6 giây. |
| Đăng xuất | `currentUser = null`, giữ nguyên giỏ hàng. |
| Tìm kiếm | Ô tìm kiếm ở header mọi trang. Từ trang khác sẽ chuyển sang `products.html?q=...`. Khớp theo tên, danh mục, màu, mã SP; không phân biệt hoa/thường **và dấu tiếng Việt**; nhiều từ khóa = AND. Rỗng = hiện tất cả. |
| Bộ lọc | Danh mục, màu, size, khoảng giá. Cùng nhóm = OR, khác nhóm = AND. Chỉ có hiệu lực khi bấm **ÁP DỤNG BỘ LỌC**. **XÓA BỘ LỌC** bỏ chọn mọi ô, giữ nguyên từ khóa tìm kiếm. |
| Sắp xếp | Mới nhất (theo `createdAt`), giá tăng, giá giảm, đang giảm giá (sale lên trước, trong nhóm xếp mới nhất). Có hiệu lực ngay khi đổi. |
| Chi tiết | `product-detail.html?id=SP001`. Chọn màu (đổi ảnh), size (bắt buộc nếu SP có size), số lượng 1..stock. Có **Thêm vào giỏ** và **Mua ngay** (thêm rồi sang checkout). |
| Giỏ hàng | Tăng, giảm (tối thiểu 1), xóa từng dòng, xóa toàn bộ, thành tiền, tổng tiền. Số lượng tối đa = tồn kho. Giữ nguyên khi tải lại / chuyển trang. |
| Checkout | Chỉ vào được khi giỏ có hàng. Kiểm tra họ tên, SĐT (chỉ số), email, địa chỉ, phương thức thanh toán. Hợp lệ thì chỉ hiện thông báo mô phỏng, **không** xóa giỏ. |

### Phạm vi dữ liệu mẫu

- 25 sản phẩm (`SP001`..`SP025`), 7 danh mục, tên gần giống nhau để test tìm kiếm (Slim Đen / Slim Xanh, Basic Trắng / Basic Đen...).
- Giá ở các ranh giới: 299.000 · 300.000 · 500.000 · 700.000 · 750.000.
  - Dưới 300.000: giá < 300.000
  - 300.000 - 500.000: từ 300.000 đến dưới 500.000
  - 500.000 - 700.000: từ 500.000 đến 700.000 (gồm cả hai đầu)
  - Trên 700.000: giá > 700.000
- `SP012` còn 3 sản phẩm (test giới hạn số lượng). `SP025` hết hàng. `SP024`, `SP025` không có size.
- Bộ lọc/tìm kiếm màu dựa trên **tất cả** màu có sẵn của sản phẩm (`colors`), không chỉ màu chính.

## 5. localStorage và reset

| Key | Nội dung |
|---|---|
| `users` | Mảng `{ name, phone, email, password }` (mật khẩu lưu thường, chỉ vì đây là bản mô phỏng) |
| `currentUser` | `{ name, email, phone }` hoặc `null` |
| `cart` | Mảng `{ id, qty, size, color }` |

Cách reset:

- Nút **RESET TEST DATA** ở chân trang (khu vực ghi rõ chỉ dành cho kiểm thử).
- Trong Selenium: `driver.execute_script("resetTestData()")` rồi tải lại trang, hoặc `driver.execute_script("localStorage.clear()")`.
- Dữ liệu hỏng (JSON sai) sẽ được tự khôi phục về mặc định khi tải trang.

## 6. ID quan trọng cho Selenium

Mọi phần tử có `id` đều có thêm `data-testid` cùng giá trị.

**Header (mọi trang):** `home-link` `products-link` `nav-shirts` `nav-pants` `nav-accessories` `login-link` `register-link` `logout-button` `user-name` `cart-link` `cart-count` `menu-toggle` · tìm kiếm: `search-form` `search-input` `search-button`

**Đăng ký:** `register-name` `register-phone` `register-email` `register-password` `register-button` `register-message` · lỗi từng ô: `register-name-error` `register-phone-error` `register-email-error` `register-password-error`

**Đăng nhập:** `login-email` `login-password` `login-button` `login-message` `login-email-error` `login-password-error` `go-register-link` `forgot-password-link`

**Danh sách SP:** `search-result-count` (văn bản "Tìm thấy X sản phẩm") `no-search-result` `search-query-label` `product-grid` `sort-select` (value: `newest` `price-asc` `price-desc` `sale`) `apply-filter` `clear-filter` `filter-toggle`
- Danh mục: `filter-category-polo|thun|somi|jeans|quanau|kaki|phukien`
- Màu: `filter-color-black|white|blue|gray|beige`
- Size: `filter-size-s|m|l|xl|xxl`
- Giá: `filter-price-under300|300-500|500-700|over700`

**Product card (thay `SP001`):** `product-card-SP001` (kèm `data-product-id`, `data-price`, `data-category`) `product-image-SP001` `product-name-SP001` `product-price-SP001` (kèm `data-price` là số thuần) `product-old-price-SP001` `product-detail-SP001` `product-add-SP001` `product-badge-sale-SP001` `product-badge-new-SP001`

**Chi tiết:** `detail-product-name` `detail-product-code` `detail-product-price` `detail-product-old-price` `detail-stock-status` `detail-product-color` `detail-selected-color` `color-option-black|white|blue|gray|beige` `detail-product-size` `detail-selected-size` `size-option-s|m|l|xl|xxl` `quantity-input` `quantity-decrease` `quantity-increase` `add-to-cart` `buy-now` `detail-message` `detail-not-found`

Nút chọn màu/size là `button` có `aria-checked="true"` khi đang chọn.

**Giỏ hàng:** `cart-item-SP001` `cart-name-SP001` `cart-variant-SP001` `cart-price-SP001` `cart-quantity-SP001` `cart-increase-SP001` `cart-decrease-SP001` `cart-subtotal-SP001` `cart-remove-SP001` `cart-total` `cart-clear` `checkout-button` `cart-empty` `cart-message`

**Checkout:** `checkout-name` `checkout-phone` `checkout-email` `checkout-province` `checkout-district` `checkout-address` `checkout-note` `payment-cod` `payment-bank` `checkout-submit` `checkout-message` `checkout-empty` `checkout-total` · lỗi: `checkout-name-error` `checkout-phone-error` `checkout-email-error` `checkout-address-error` `checkout-payment-error`

## 7. Luồng test có thể tự động hóa

| Flow | Các bước |
|---|---|
| A | Home → Đăng ký → nhập thông tin → submit → Đăng nhập → thành công, `user-name` hiện tên |
| B | Home → gõ `Jeans` vào `search-input` → kiểm tra `search-result-count` |
| C | Products → `filter-category-jeans` + `filter-color-black` → `apply-filter` → kiểm tra các card |
| D | Products → `sort-select` = `price-asc` → đọc `data-price` các `product-price-*` → kiểm tra tăng dần |
| E | Chi tiết → chọn màu, size → `quantity-input` = 2 → `add-to-cart` → Giỏ → `cart-quantity-SP001` = 2 |
| F | Giỏ → tăng → kiểm tra `cart-total` → giảm → kiểm tra → xóa → `cart-empty` hiện |
| G | Giỏ → `checkout-button` → nhập hợp lệ + chọn thanh toán → submit → kiểm tra `checkout-message` |
| H | Checkout → để trống → submit → kiểm tra các `*-error` |

Gợi ý chờ: mọi phần tử đều có sẵn trong DOM khi trang tải xong. Các phần tử ẩn dùng thuộc tính `hidden`, nên dùng `is_displayed()` thay vì kiểm tra tồn tại. Sau khi đăng nhập thành công, trang chuyển về `index.html` sau ~0,6 giây, nên đợi URL đổi.

## 8. Chưa triển khai / giới hạn

- Mỗi sản phẩm chỉ có **một dòng** trong giỏ. Thêm lại cùng sản phẩm với size/màu khác sẽ cộng dồn số lượng và lấy size/màu mới nhất. (Cố ý để ID `cart-item-SP001` luôn duy nhất.)
- Tồn kho tính theo sản phẩm, không theo từng size/màu.
- Tỉnh/Thành, Quận/Huyện không bắt buộc (đúng theo danh sách validation của đề).
- Quên mật khẩu chỉ hiện thông báo "chưa hỗ trợ". Không có OAuth Facebook/Google.
- Các liên kết chân trang (Về chúng tôi, Chính sách...) chỉ là liên kết giữ chỗ.
- Font Be Vietnam Pro tải từ Google Fonts một cách không chặn trang. Mất mạng sẽ tự dùng font hệ thống.
