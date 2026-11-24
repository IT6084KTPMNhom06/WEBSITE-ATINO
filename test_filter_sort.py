"""
Selenium WebDriver (Python + pytest) — kiểm thử LỌC THEO GIÁ và SẮP XẾP (bảng TC_FS_01 .. TC_FS_14).

Chạy (website phải đang bật):
    pip install -r requirements.txt
    pytest test_filter_sort.py -v

Biến môi trường (tùy chọn):
    BASE_URL=http://localhost:5500    HEADLESS=1

Ghi chú về dữ liệu và quy tắc của website mô phỏng:
  * TC_FS_02: bảng ghi "dưới 200,000" nhưng tên mức là "Dưới 300,000" -> test dùng 300.000.
  * TC_FS_01 mở Quần -> Jeans. Các test lọc giá còn lại chạy trên TOÀN BỘ sản phẩm, vì trong
    danh mục Jeans không có sản phẩm nào dưới 300.000 hoặc trên 700.000.
  * Quy tắc biên: dưới 300.000 | 300.000 đến dưới 500.000 | 500.000 đến 700.000 (gồm 700.000) | trên 700.000.
  * Các mức giá là ô tích (checkbox): chọn nhiều mức cùng lúc sẽ là HOẶC (cộng dồn).
  * Bộ lọc chỉ áp dụng khi bấm "ÁP DỤNG BỘ LỌC"; sắp xếp có hiệu lực ngay khi đổi.
  * Website không có phân trang nên TC_FS_13 được đánh dấu bỏ qua (skip).
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

# key trùng với phần cuối id ô lọc: filter-price-<key>
PRICE_KEYS = ["under300", "300-500", "500-700", "over700"]
PRICE_RANGES = {            # (nhỏ nhất, lớn nhất) — tính cả hai đầu
    "under300": (0, 299999),
    "300-500": (300000, 499999),
    "500-700": (500000, 700000),
    "over700": (700001, 10 ** 9),
}
SORT_LABELS = ["Mới nhất", "Giá thấp đến cao", "Giá cao đến thấp", "Đang giảm giá"]

RESULT_COUNT = (By.ID, "search-result-count")
SORT_SELECT = (By.ID, "sort-select")
CARDS = (By.CSS_SELECTOR, "#product-grid article.product-card")


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


def total_count(driver):
    return len(driver.find_elements(*CARDS))


def prices(driver):
    """Dãy giá (số nguyên) của các sản phẩm đang hiển thị, theo đúng thứ tự trên trang."""
    els = driver.find_elements(By.CSS_SELECTOR, '[id^="product-price-"]')
    return [int(e.get_attribute("data-price")) for e in els]


def ids(driver):
    return [c.get_attribute("data-product-id") for c in driver.find_elements(*CARDS)]


def apply_filter(driver):
    driver.find_element(By.ID, "apply-filter").click()


def select_prices(driver, *keys):
    """Bỏ chọn mọi mức giá đang chọn, chọn các mức trong `keys` rồi bấm ÁP DỤNG BỘ LỌC."""
    for key in PRICE_KEYS:
        box = driver.find_element(By.ID, f"filter-price-{key}")
        if box.is_selected():
            box.click()
    for key in keys:
        driver.find_element(By.ID, f"filter-price-{key}").click()
    apply_filter(driver)


def sort_by(driver, value):
    """value: newest | price-asc | price-desc | sale"""
    Select(driver.find_element(*SORT_SELECT)).select_by_value(value)


def in_range(price, key):
    low, high = PRICE_RANGES[key]
    return low <= price <= high


def assert_count_matches_list(driver):
    """Dòng 'Tìm thấy X sản phẩm' phải khớp số card trên trang."""
    text = driver.find_element(*RESULT_COUNT).text
    assert text == f"Tìm thấy {total_count(driver)} sản phẩm", text


# --------------------------------------------------------------------------
# Giao diện
# --------------------------------------------------------------------------
def test_TC_FS_01_hien_thi_bo_loc_gia_va_sap_xep(driver):
    # Trang chủ -> menu "Quần" -> chỉ chọn danh mục Jeans
    driver.get(f"{BASE_URL}/index.html")
    driver.find_element(By.ID, "nav-pants").click()
    wait_for(driver, RESULT_COUNT)
    driver.find_element(By.ID, "clear-filter").click()
    driver.find_element(By.ID, "filter-category-jeans").click()
    apply_filter(driver)

    assert all(c.get_attribute("data-category") == "jeans" for c in driver.find_elements(*CARDS))
    # Khu vực lọc giá: đủ 4 mức, đều hiển thị
    labels = []
    for key in PRICE_KEYS:
        box = driver.find_element(By.ID, f"filter-price-{key}")
        assert box.is_displayed() and box.is_enabled()
        labels.append(driver.find_element(By.CSS_SELECTOR, f'label[for="filter-price-{key}"]').text.strip())
    assert labels == ["Dưới 300.000", "300.000 - 500.000", "500.000 - 700.000", "Trên 700.000"]
    # Danh sách sắp xếp
    sort_el = driver.find_element(*SORT_SELECT)
    assert sort_el.is_displayed()
    assert [o.text for o in Select(sort_el).options] == SORT_LABELS
    assert driver.find_element(By.ID, "apply-filter").is_displayed()
    assert driver.find_element(By.ID, "clear-filter").is_displayed()


# --------------------------------------------------------------------------
# Lọc theo khoảng giá
# --------------------------------------------------------------------------
@pytest.mark.parametrize("case_id,key", [
    ("TC_FS_02", "under300"),
    ("TC_FS_03", "300-500"),
    ("TC_FS_04", "500-700"),
])
def test_TC_FS_02_03_04_loc_theo_khoang_gia(driver, case_id, key):
    open_products(driver)
    all_items = total_count(driver)

    select_prices(driver, key)

    got = prices(driver)
    assert got, f"{case_id}: khoảng '{key}' phải có sản phẩm"
    assert len(got) < all_items, "Danh sách phải được cập nhật (ít hơn ban đầu)"
    assert all(in_range(p, key) for p in got), got
    assert_count_matches_list(driver)


def test_TC_FS_05_loc_tren_700000(driver):
    open_products(driver)
    select_prices(driver, "over700")

    got = prices(driver)
    if got:
        assert all(p > 700000 for p in got), got
    else:
        assert driver.find_element(By.ID, "no-search-result").is_displayed()
    assert_count_matches_list(driver)
    assert driver.find_element(By.ID, "apply-filter").is_displayed()  # trang không lỗi


# Sản phẩm có giá đúng bằng ranh giới: (giá, mã SP, khoảng mà sản phẩm phải thuộc về)
@pytest.mark.parametrize("price,product_id,expected_key", [
    (300000, "SP012", "300-500"),   # 300.000 thuộc "300.000 - 500.000", không thuộc "Dưới 300.000"
    (500000, "SP017", "500-700"),   # 500.000 thuộc "500.000 - 700.000", không thuộc "300.000 - 500.000"
    (700000, "SP024", "500-700"),   # 700.000 thuộc "500.000 - 700.000", không thuộc "Trên 700.000"
])
def test_TC_FS_06_gia_dung_bang_bien(driver, price, product_id, expected_key):
    open_products(driver)
    for key in PRICE_KEYS:
        select_prices(driver, key)
        shown = product_id in ids(driver)
        assert shown == (key == expected_key), (
            f"{product_id} (giá {price}) {'xuất hiện' if shown else 'không xuất hiện'} ở khoảng '{key}'"
        )


def test_TC_FS_07_bo_chon_bo_loc(driver):
    open_products(driver)
    full = ids(driver)

    # Cách 1: bỏ tích ô rồi áp dụng lại
    select_prices(driver, "300-500")
    assert 0 < len(ids(driver)) < len(full)
    driver.find_element(By.ID, "filter-price-300-500").click()
    apply_filter(driver)
    assert ids(driver) == full

    # Cách 2: nút XÓA BỘ LỌC
    select_prices(driver, "300-500")
    assert len(ids(driver)) < len(full)
    driver.find_element(By.ID, "clear-filter").click()
    assert ids(driver) == full
    assert not driver.find_element(By.ID, "filter-price-300-500").is_selected()


def test_TC_FS_08_doi_khoang_gia_lien_tiep(driver):
    open_products(driver)
    select_prices(driver, "under300")
    assert all(p < 300000 for p in prices(driver))

    # Đổi sang khoảng mới: bỏ khoảng cũ, chọn khoảng mới
    select_prices(driver, "300-500")
    got = prices(driver)
    assert got and all(in_range(p, "300-500") for p in got), got


def test_TC_FS_08b_chon_them_khoang_khac_la_cong_don(driver):
    """Ghi nhận: các mức giá là checkbox. Chọn thêm mà không bỏ mức cũ => kết quả là HỢP của 2 khoảng."""
    open_products(driver)
    driver.find_element(By.ID, "filter-price-under300").click()
    driver.find_element(By.ID, "filter-price-300-500").click()
    apply_filter(driver)
    got = prices(driver)
    assert any(p < 300000 for p in got) and any(300000 <= p < 500000 for p in got)
    assert all(in_range(p, "under300") or in_range(p, "300-500") for p in got)


# --------------------------------------------------------------------------
# Sắp xếp
# --------------------------------------------------------------------------
def test_TC_FS_09_sap_xep_gia_tang_dan(driver):
    open_products(driver)
    sort_by(driver, "price-asc")
    got = prices(driver)
    assert len(got) > 1
    assert got == sorted(got), got
    assert Select(driver.find_element(*SORT_SELECT)).first_selected_option.text == "Giá thấp đến cao"


def test_TC_FS_10_sap_xep_gia_giam_dan(driver):
    open_products(driver)
    sort_by(driver, "price-desc")
    got = prices(driver)
    assert len(got) > 1
    assert got == sorted(got, reverse=True), got


def test_TC_FS_11_doi_tieu_chi_sap_xep_lien_tiep(driver):
    open_products(driver)
    sort_by(driver, "price-asc")
    asc = prices(driver)
    assert asc == sorted(asc)

    sort_by(driver, "price-desc")
    desc = prices(driver)
    assert desc == sorted(desc, reverse=True)
    assert desc[0] == max(asc) and desc[-1] == min(asc)
    assert sorted(asc) == sorted(desc)  # cùng tập sản phẩm, chỉ đổi thứ tự


def test_TC_FS_12_ket_hop_loc_gia_va_sap_xep(driver):
    open_products(driver)
    select_prices(driver, "300-500")
    sort_by(driver, "price-asc")

    got = prices(driver)
    assert got and all(in_range(p, "300-500") for p in got), got
    assert got == sorted(got), got

    # Đổi chiều sắp xếp vẫn giữ nguyên bộ lọc
    sort_by(driver, "price-desc")
    got = prices(driver)
    assert all(in_range(p, "300-500") for p in got)
    assert got == sorted(got, reverse=True)


# --------------------------------------------------------------------------
# Điều hướng
# --------------------------------------------------------------------------
@pytest.mark.skip(reason="TC_FS_13: website mô phỏng không có phân trang (tất cả sản phẩm hiện trên một trang).")
def test_TC_FS_13_chuyen_trang_sau_khi_loc(driver):
    pass


def test_TC_FS_14_quay_lai_tu_trang_chi_tiet(driver):
    open_products(driver)
    full = total_count(driver)
    select_prices(driver, "300-500")
    filtered_ids = ids(driver)
    assert 0 < len(filtered_ids) < full

    driver.find_element(By.CSS_SELECTOR, '[id^="product-name-"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains("product-detail.html"))

    driver.back()
    WebDriverWait(driver, 10).until(EC.url_contains("products.html"))
    wait_for(driver, RESULT_COUNT)
    WebDriverWait(driver, 10).until(lambda d: total_count(d) > 0)

    still_checked = driver.find_element(By.ID, "filter-price-300-500").is_selected()
    if still_checked:
        # Ghi nhận: bộ lọc được giữ -> danh sách phải đúng là danh sách đã lọc
        assert all(in_range(p, "300-500") for p in prices(driver))
        assert ids(driver) == filtered_ids
    else:
        # Ghi nhận: bộ lọc bị đặt lại -> danh sách phải đầy đủ
        assert total_count(driver) == full
    # Dù giữ hay đặt lại, ô lọc và danh sách phải nhất quán
    assert_count_matches_list(driver)
