"""
Selenium WebDriver (Python + pytest) — kiểm thử XEM SẢN PHẨM THEO DANH MỤC (bảng TC_CAT_01 .. TC_CAT_11).

Chạy (website phải đang bật):
    pip install -r requirements.txt
    pytest test_category.py -v

Biến môi trường (tùy chọn):  BASE_URL=http://localhost:5500   HEADLESS=1

Ghi chú:
  * Mã trong bảng "TC_CAT_9" và "TC_CAT_111" là gõ nhầm; test dùng TC_CAT_09 và TC_CAT_11.
  * TC_CAT_10: trong dữ liệu mẫu mọi danh mục đều có sản phẩm, nên để có "danh mục không có sản phẩm phù hợp"
    test kết hợp danh mục Phụ kiện với mức giá "Trên 700.000" (Phụ kiện đắt nhất là 700.000 nên không có kết quả).
  * Cuối file có thêm vài test bổ sung (menu Áo / Quần / Phụ kiện dẫn đến đúng danh mục).
"""
import os
import re

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

# key (phần cuối id ô lọc) -> nhãn hiển thị
CATEGORY_LABELS = {
    "polo": "Áo Polo",
    "thun": "Áo thun",
    "somi": "Sơ mi",
    "jeans": "Quần Jeans",
    "quanau": "Quần âu",
    "kaki": "Quần Kaki",
    "phukien": "Phụ kiện",
}
# Số sản phẩm mỗi danh mục trong dữ liệu mẫu (js/data.js)
EXPECTED_COUNT = {"polo": 4, "thun": 4, "somi": 4, "jeans": 4, "quanau": 3, "kaki": 3, "phukien": 3}
TOTAL_PRODUCTS = sum(EXPECTED_COUNT.values())  # 25

RESULT_COUNT = (By.ID, "search-result-count")
NO_RESULT = (By.ID, "no-search-result")
CARDS = (By.CSS_SELECTOR, "#product-grid article.product-card")
PRICE_TEXT_RE = re.compile(r"^\d{1,3}(\.\d{3})*đ$")  # ví dụ 399.000đ


# --------------------------------------------------------------------------
# Fixture & hàm hỗ trợ
# --------------------------------------------------------------------------
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    if os.environ.get("HEADLESS") == "1":
        options.add_argument("--headless=new")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


def wait_for(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def open_products(driver, query=""):
    driver.get(f"{BASE_URL}/products.html{query}")
    wait_for(driver, RESULT_COUNT)


def cards(driver):
    return driver.find_elements(*CARDS)


def ids(driver):
    return [c.get_attribute("data-product-id") for c in cards(driver)]


def categories_shown(driver):
    """Tập danh mục (key) của các sản phẩm đang hiển thị."""
    return {c.get_attribute("data-category") for c in cards(driver)}


def select_categories(driver, *keys):
    """Bỏ chọn mọi danh mục đang chọn, chọn các danh mục trong `keys` rồi bấm ÁP DỤNG BỘ LỌC."""
    for key in CATEGORY_LABELS:
        box = driver.find_element(By.ID, f"filter-category-{key}")
        if box.is_selected():
            box.click()
    for key in keys:
        driver.find_element(By.ID, f"filter-category-{key}").click()
    driver.find_element(By.ID, "apply-filter").click()


def checked_categories(driver):
    return [k for k in CATEGORY_LABELS if driver.find_element(By.ID, f"filter-category-{k}").is_selected()]


def assert_count_matches_list(driver):
    text = driver.find_element(*RESULT_COUNT).text
    assert text == f"Tìm thấy {len(cards(driver))} sản phẩm", text


# --------------------------------------------------------------------------
# Giao diện
# --------------------------------------------------------------------------
def test_TC_CAT_01_hien_thi_danh_muc_tren_menu(driver):
    driver.get(f"{BASE_URL}/index.html")
    wait_for(driver, (By.ID, "nav-home"))

    menu = {"nav-home": "Trang chủ", "nav-shirts": "Áo", "nav-pants": "Quần",
            "nav-accessories": "Phụ kiện", "products-link": "Tất cả sản phẩm"}
    for element_id, text in menu.items():
        el = driver.find_element(By.ID, element_id)
        assert el.is_displayed(), element_id
        assert el.text.strip() == text, (element_id, el.text)

    # Dải danh mục ở trang chủ
    strip = {"polo": "Áo Polo", "thun": "Áo thun", "somi": "Sơ mi",
             "jeans": "Quần Jeans", "quanau": "Quần âu", "kaki": "Quần Kaki"}
    for key, text in strip.items():
        el = driver.find_element(By.ID, f"category-link-{key}")
        assert el.is_displayed() and el.text.strip() == text

    # Không bị lỗi giao diện: không tràn ngang
    assert not driver.execute_script("return document.documentElement.scrollWidth > window.innerWidth + 1;")


def test_TC_CAT_02_hien_thi_danh_muc_trong_bo_loc(driver):
    open_products(driver)
    labels = []
    for key in CATEGORY_LABELS:
        box = driver.find_element(By.ID, f"filter-category-{key}")
        assert box.is_displayed() and box.is_enabled(), key
        assert not box.is_selected(), f"{key} không được chọn sẵn"
        labels.append(driver.find_element(By.CSS_SELECTOR, f'label[for="filter-category-{key}"]').text.strip())
    assert labels == list(CATEGORY_LABELS.values())


# --------------------------------------------------------------------------
# Xem sản phẩm theo từng danh mục
# --------------------------------------------------------------------------
@pytest.mark.parametrize("case_id,key", [
    ("TC_CAT_03", "polo"),
    ("TC_CAT_04", "somi"),
    ("TC_CAT_05", "jeans"),
    ("TC_CAT_06", "phukien"),
])
def test_TC_CAT_03_04_05_06_xem_theo_danh_muc(driver, case_id, key):
    open_products(driver)
    select_categories(driver, key)

    shown = cards(driver)
    assert len(shown) == EXPECTED_COUNT[key], f"{case_id}: {len(shown)} sản phẩm"
    assert categories_shown(driver) == {key}
    assert_count_matches_list(driver)
    # Mỗi thẻ ghi đúng tên danh mục
    metas = driver.find_elements(By.CSS_SELECTOR, "#product-grid .product-meta")
    assert all(m.text.startswith(CATEGORY_LABELS[key]) for m in metas), [m.text for m in metas]
    assert not driver.find_element(*NO_RESULT).is_displayed()


def test_TC_CAT_07_chon_nhieu_danh_muc(driver):
    open_products(driver)
    select_categories(driver, "polo", "thun")

    assert len(cards(driver)) == EXPECTED_COUNT["polo"] + EXPECTED_COUNT["thun"]
    assert categories_shown(driver) == {"polo", "thun"}  # có đủ cả hai, không có danh mục khác
    assert_count_matches_list(driver)


def test_TC_CAT_08_thong_tin_tren_the_san_pham(driver):
    open_products(driver)
    select_categories(driver, "polo")

    shown = cards(driver)
    assert shown
    for card in shown:
        pid = card.get_attribute("data-product-id")
        # Hình ảnh
        img = card.find_element(By.CSS_SELECTOR, "img")
        assert img.is_displayed()
        assert driver.execute_script("return arguments[0].complete;", img)
        # Tên
        name = card.find_element(By.ID, f"product-name-{pid}").text.strip()
        assert name != ""
        assert img.get_attribute("alt") == name
        # Danh mục + màu sắc
        meta = card.find_element(By.CSS_SELECTOR, ".product-meta").text
        assert "Áo Polo" in meta and "·" in meta, meta
        # Giá bán: đúng định dạng và khớp data-price
        price_el = card.find_element(By.ID, f"product-price-{pid}")
        assert PRICE_TEXT_RE.match(price_el.text.strip()), price_el.text
        digits = int(re.sub(r"\D", "", price_el.text))
        assert digits == int(price_el.get_attribute("data-price"))
        # Nút thao tác
        assert card.find_element(By.ID, f"product-detail-{pid}").is_displayed()
        assert card.find_element(By.ID, f"product-add-{pid}").is_displayed()


def test_TC_CAT_09_xoa_bo_loc_danh_muc(driver):
    open_products(driver)
    default_ids = ids(driver)
    assert len(default_ids) == TOTAL_PRODUCTS

    select_categories(driver, "polo", "thun")
    assert len(ids(driver)) == 8
    assert sorted(checked_categories(driver)) == ["polo", "thun"]

    driver.find_element(By.ID, "clear-filter").click()
    assert checked_categories(driver) == []   # các ô được bỏ chọn
    assert ids(driver) == default_ids         # danh sách về mặc định
    assert_count_matches_list(driver)


def test_TC_CAT_10_danh_muc_khong_co_san_pham_phu_hop(driver):
    open_products(driver)
    select_categories(driver, "phukien")
    assert len(cards(driver)) == EXPECTED_COUNT["phukien"]

    # Kết hợp thêm mức giá "Trên 700.000": Phụ kiện không có sản phẩm nào thỏa
    driver.find_element(By.ID, "filter-price-over700").click()
    driver.find_element(By.ID, "apply-filter").click()

    assert cards(driver) == []
    message = driver.find_element(*NO_RESULT)
    assert message.is_displayed()
    assert message.text.strip() == "Không tìm thấy sản phẩm phù hợp."
    assert driver.find_element(*RESULT_COUNT).text == "Tìm thấy 0 sản phẩm"
    # Giao diện vẫn bình thường, bộ lọc vẫn dùng được
    assert driver.find_element(By.ID, "clear-filter").is_displayed()
    driver.find_element(By.ID, "clear-filter").click()
    assert len(cards(driver)) == TOTAL_PRODUCTS


def test_TC_CAT_11_mo_chi_tiet_tu_danh_muc(driver):
    target_name = "Áo Polo Basic Đen"
    open_products(driver)
    select_categories(driver, "polo")

    # Tìm sản phẩm theo tên rồi bấm "Xem chi tiết" của đúng thẻ đó
    target_id = None
    for card in cards(driver):
        pid = card.get_attribute("data-product-id")
        if card.find_element(By.ID, f"product-name-{pid}").text.strip() == target_name:
            target_id = pid
            break
    assert target_id, f"Không thấy '{target_name}' trong danh mục Áo Polo"
    driver.find_element(By.ID, f"product-detail-{target_id}").click()

    WebDriverWait(driver, 10).until(EC.url_contains("product-detail.html"))
    assert f"id={target_id}" in driver.current_url
    name_el = wait_for(driver, (By.ID, "detail-product-name"))
    WebDriverWait(driver, 10).until(lambda d: name_el.text.strip() != "")
    assert name_el.text == target_name
    assert driver.find_element(By.ID, "detail-product-code").text == target_id


# --------------------------------------------------------------------------
# Bổ sung: menu "Áo / Quần / Phụ kiện" dẫn đến đúng nhóm danh mục
# --------------------------------------------------------------------------
@pytest.mark.parametrize("nav_id,expected_keys,expected_total", [
    ("nav-shirts", {"polo", "thun", "somi"}, 12),
    ("nav-pants", {"jeans", "quanau", "kaki"}, 10),
    ("nav-accessories", {"phukien"}, 3),
])
def test_bo_sung_menu_dan_den_dung_danh_muc(driver, nav_id, expected_keys, expected_total):
    driver.get(f"{BASE_URL}/index.html")
    driver.find_element(By.ID, nav_id).click()
    wait_for(driver, RESULT_COUNT)

    assert len(cards(driver)) == expected_total
    assert categories_shown(driver) == expected_keys
    # Các ô danh mục trong bộ lọc được chọn sẵn tương ứng
    assert set(checked_categories(driver)) == expected_keys


def test_bo_sung_o_danh_muc_trang_chu_dan_den_danh_muc(driver):
    driver.get(f"{BASE_URL}/index.html")
    driver.find_element(By.ID, "category-link-jeans").click()
    wait_for(driver, RESULT_COUNT)
    assert categories_shown(driver) == {"jeans"}
    assert len(cards(driver)) == EXPECTED_COUNT["jeans"]
