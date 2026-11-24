/*
 * data.js — Dữ liệu sản phẩm cố định (có chủ đích) phục vụ test Search / Filter / Sort.
 *
 * Điểm đáng chú ý cho tester:
 *  - Nhiều sản phẩm có tên gần giống nhau: "Quần Jeans Slim Đen/Xanh", "Áo Polo Basic Trắng/Đen",
 *    "Áo Sơ Mi Oxford Trắng/Xanh", "Quần Kaki Slim Be/Đen"...
 *  - Giá nằm đúng ranh giới khoảng giá: 299.000 / 300.000 / 499.000 (không có) / 500.000 / 700.000 / 750.000.
 *  - SP012 chỉ còn 3 sản phẩm (test giới hạn số lượng), SP025 hết hàng (stock = 0).
 *  - SP024, SP025 không có size (Free size) -> không xuất hiện khi lọc theo size.
 *  - `color` là màu chính; `colors` là tất cả màu có sẵn (bộ lọc & tìm kiếm dùng `colors`).
 */

const CATEGORIES = {
  polo: 'Áo Polo',
  thun: 'Áo thun',
  somi: 'Sơ mi',
  jeans: 'Quần Jeans',
  quanau: 'Quần âu',
  kaki: 'Quần Kaki',
  phukien: 'Phụ kiện'
};

// Nhóm danh mục dùng cho menu "Áo", "Quần", "Phụ kiện"
const CATEGORY_GROUPS = {
  ao: ['polo', 'thun', 'somi'],
  quan: ['jeans', 'quanau', 'kaki'],
  phukien: ['phukien']
};

const COLORS = [
  { code: 'black', name: 'Đen', hex: '#22262b' },
  { code: 'white', name: 'Trắng', hex: '#f4f4f2' },
  { code: 'blue', name: 'Xanh', hex: '#2f5b88' },
  { code: 'gray', name: 'Xám', hex: '#8a9099' },
  { code: 'beige', name: 'Be', hex: '#cdb892' }
];

const SIZES = ['S', 'M', 'L', 'XL', 'XXL'];

// Khoảng giá: [min, max) — riêng "500.000 - 700.000" tính cả 700.000
const PRICE_RANGES = {
  under300: { label: 'Dưới 300.000', test: (p) => p < 300000 },
  '300-500': { label: '300.000 - 500.000', test: (p) => p >= 300000 && p < 500000 },
  '500-700': { label: '500.000 - 700.000', test: (p) => p >= 500000 && p <= 700000 },
  over700: { label: 'Trên 700.000', test: (p) => p > 700000 }
};

function makeProduct(id, name, category, price, oldPrice, colors, sizes, flags, stock, createdAt, description) {
  return {
    id: id,
    name: name,
    category: category,
    price: price,
    oldPrice: oldPrice,          // null nếu không giảm giá
    color: colors[0],
    colors: colors,
    sizes: sizes,
    isSale: !!flags.sale,
    isNew: !!flags.isNew,
    isFeatured: !!flags.featured,
    stock: stock,
    createdAt: createdAt,        // ISO date, dùng cho sắp xếp "Mới nhất"
    description: description
  };
}

const PRODUCTS = [
  makeProduct('SP001', 'Quần Jeans Slim Đen', 'jeans', 399000, 499000, ['Đen', 'Xanh'], ['M', 'L', 'XL'], { sale: true, isNew: true }, 20, '2026-10-20',
    'Quần jeans dáng slim, vải denim co giãn nhẹ, màu đen bền màu. Mặc đi làm hay đi chơi đều gọn.'),
  makeProduct('SP002', 'Quần Jeans Slim Xanh', 'jeans', 429000, null, ['Xanh'], ['S', 'M', 'L', 'XL'], { isNew: true }, 25, '2026-10-18',
    'Quần jeans slim màu xanh denim đậm, form ôm vừa phải, không bó đùi.'),
  makeProduct('SP003', 'Quần Jeans Regular Đen', 'jeans', 459000, null, ['Đen'], ['M', 'L', 'XL', 'XXL'], { featured: true }, 30, '2026-08-12',
    'Quần jeans form regular thoải mái, ống đứng, phù hợp người dáng đậm.'),
  makeProduct('SP004', 'Quần Jeans Rách Gối Xanh', 'jeans', 549000, 649000, ['Xanh'], ['S', 'M', 'L'], { sale: true }, 12, '2026-07-05',
    'Quần jeans wash nhẹ, rách gối nhỏ, phong cách trẻ trung.'),
  makeProduct('SP005', 'Áo Polo Basic Trắng', 'polo', 289000, null, ['Trắng', 'Đen', 'Xanh'], ['S', 'M', 'L', 'XL'], { featured: true }, 40, '2026-08-20',
    'Áo polo cotton cá sấu, cổ bo dệt, thoáng mát. Có 3 màu để chọn.'),
  makeProduct('SP006', 'Áo Polo Basic Đen', 'polo', 289000, null, ['Đen'], ['M', 'L', 'XL', 'XXL'], {}, 35, '2026-08-19',
    'Áo polo basic màu đen, dễ phối với quần jeans và quần kaki.'),
  makeProduct('SP007', 'Áo Polo Cafe Xám', 'polo', 349000, 429000, ['Xám', 'Be'], ['S', 'M', 'L'], { sale: true }, 18, '2026-06-30',
    'Áo polo sợi cafe khử mùi, nhanh khô, giảm giá theo mùa.'),
  makeProduct('SP008', 'Áo Polo Premium Xanh', 'polo', 599000, null, ['Xanh'], ['M', 'L', 'XL'], { isNew: true }, 10, '2026-10-15',
    'Áo polo cao cấp, cotton compact dày dặn, đường may tỉ mỉ.'),
  makeProduct('SP009', 'Áo Thun Basic Trắng', 'thun', 199000, null, ['Trắng', 'Đen', 'Xám'], ['S', 'M', 'L', 'XL', 'XXL'], { featured: true }, 60, '2026-08-01',
    'Áo thun cotton 100%, cổ tròn, đủ size từ S đến XXL.'),
  makeProduct('SP010', 'Áo Thun Basic Đen', 'thun', 199000, 249000, ['Đen'], ['S', 'M', 'L', 'XL'], { sale: true }, 50, '2026-07-22',
    'Áo thun đen cổ tròn, giá mềm, mặc hằng ngày.'),
  makeProduct('SP011', 'Áo Thun Oversize Xám', 'thun', 259000, null, ['Xám'], ['M', 'L', 'XL', 'XXL'], { isNew: true }, 22, '2026-10-12',
    'Áo thun form rộng, vai trễ nhẹ, vải dày không xuyên thấu.'),
  makeProduct('SP012', 'Áo Thun Graphic Be', 'thun', 300000, null, ['Be'], ['S', 'M', 'L'], { isNew: true }, 3, '2026-10-10',
    'Áo thun in hình giới hạn. Chỉ còn 3 sản phẩm trong kho.'),
  makeProduct('SP013', 'Áo Sơ Mi Oxford Trắng', 'somi', 399000, null, ['Trắng', 'Xanh'], ['S', 'M', 'L', 'XL'], { featured: true }, 28, '2026-08-25',
    'Sơ mi oxford dài tay, vải dệt chéo, ít nhăn.'),
  makeProduct('SP014', 'Áo Sơ Mi Oxford Xanh', 'somi', 399000, null, ['Xanh'], ['M', 'L', 'XL'], { isNew: true }, 16, '2026-10-08',
    'Sơ mi oxford màu xanh nhạt, hợp môi trường công sở.'),
  makeProduct('SP015', 'Áo Sơ Mi Linen Be', 'somi', 499000, 599000, ['Be', 'Trắng'], ['S', 'M', 'L', 'XL'], { sale: true }, 14, '2026-07-15',
    'Sơ mi linen mát nhẹ, màu be nhã nhặn, hợp mùa hè.'),
  makeProduct('SP016', 'Áo Sơ Mi Flannel Xám', 'somi', 549000, null, ['Xám'], ['L', 'XL', 'XXL'], { isNew: true }, 9, '2026-10-05',
    'Sơ mi flannel dày vừa, giữ ấm nhẹ cho mùa lạnh.'),
  makeProduct('SP017', 'Quần Âu Slimfit Đen', 'quanau', 500000, null, ['Đen'], ['M', 'L', 'XL'], { featured: true }, 24, '2026-08-30',
    'Quần âu slimfit đen, ống côn, vải ít nhăn.'),
  makeProduct('SP018', 'Quần Âu Slimfit Xám', 'quanau', 549000, 699000, ['Xám'], ['S', 'M', 'L', 'XL'], { sale: true, isNew: true }, 11, '2026-10-02',
    'Quần âu xám tro, giảm giá đợt ra mắt.'),
  makeProduct('SP019', 'Quần Âu Công Sở Đen', 'quanau', 750000, null, ['Đen', 'Xám'], ['L', 'XL', 'XXL'], {}, 8, '2026-06-10',
    'Quần âu công sở cao cấp, vải wool pha, form đứng.'),
  makeProduct('SP020', 'Quần Kaki Slim Be', 'kaki', 379000, null, ['Be', 'Xám'], ['S', 'M', 'L', 'XL'], {}, 26, '2026-09-28',
    'Quần kaki slim màu be, chất vải mềm, co giãn 2 chiều.'),
  makeProduct('SP021', 'Quần Kaki Slim Đen', 'kaki', 379000, 429000, ['Đen'], ['M', 'L', 'XL'], { sale: true }, 19, '2026-09-15',
    'Quần kaki slim màu đen, đang giảm giá.'),
  makeProduct('SP022', 'Quần Kaki Short Xám', 'kaki', 249000, null, ['Xám', 'Be'], ['S', 'M', 'L', 'XL'], { isNew: true }, 33, '2026-09-25',
    'Quần short kaki ngang gối, mát và gọn cho mùa nóng.'),
  makeProduct('SP023', 'Thắt Lưng Da Đen', 'phukien', 299000, null, ['Đen'], ['M', 'L'], {}, 15, '2026-05-20',
    'Thắt lưng da bò, khóa kim loại không gỉ.'),
  makeProduct('SP024', 'Ví Da Nam Đen', 'phukien', 700000, null, ['Đen'], [], {}, 7, '2026-05-02',
    'Ví da bò nguyên tấm, nhiều ngăn thẻ. Sản phẩm không có size (Free size).'),
  makeProduct('SP025', 'Tất Cotton Trắng', 'phukien', 99000, null, ['Trắng', 'Đen'], [], {}, 0, '2026-04-15',
    'Tất cotton cổ ngắn. Sản phẩm đang HẾT HÀNG (dùng để test trạng thái hết hàng).')
];
