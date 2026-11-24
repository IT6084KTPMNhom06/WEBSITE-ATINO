"""
Selenium WebDriver (Python + pytest) — kiểm thử chức năng TÌM KIẾM (bảng 3.3.3.2).

Chạy:
    pip install -r requirements.txt
    # bật website trước (ví dụ: python -m http.server 5500 trong thư mục atino-mock)
    pytest test_search.py -v

Tùy chọn (biến môi trường):
    BASE_URL=http://localhost:5500    địa chỉ website (mặc định như trên)
    HEADLESS=1                        chạy trình duyệt ẩn

Dữ liệu đầu vào đã đổi cho khớp website mô phỏng:
    "Quần Jeans Straight 30.1.1359" -> "Quần Jeans Slim Đen"   (tên sản phẩm)
    "30.1.1359"                     -> "SP001"                  (mã sản phẩm)
"""
import os
import re

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

PRODUCT_NAME = "Quần Jeans Slim Đen"
PRODUCT_CODE = "SP001"
NO_RESULT_TEXT = "Không tìm thấy sản phẩm phù hợp."

# Locator (đều là id ổn định của website)
SEARCH_INPUT = (By.ID, "search-input")
SEARCH_BUTTON = (By.ID, "search-button")
RESULT_COUNT = (By.ID, "search-result-count")
NO_RESULT = (By.ID, "no-search-result")
PRODUCT_CARDS = (By.CSS_SELECTOR, "#product-grid article.product-card")


# --------------------------------------------------------------------------
# Fixture & hàm hỗ trợ
# --------------------------------------------------------------------------
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    if os.environ.get("HEADLESS") == "1":
        options.add_argument("--headless=new")
    drv = webdriver.Chrome(options=options)  # Selenium Manager tự tìm chromedriver
    drv.implicitly_wait(0)                   # dùng explicit wait cho dễ kiểm soát
    yield drv
    drv.quit()


def wait_for(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def open_page(driver, page="index.html"):
    driver.get(f"{BASE_URL}/{page}")
    wait_for(driver, SEARCH_INPUT)


def type_query(driver, text):
    box = wait_for(driver, SEARCH_INPUT)
    box.clear()
    box.send_keys(text)
    return box


def submit_by_button(driver):
    driver.find_element(*SEARCH_BUTTON).click()
    wait_for(driver, RESULT_COUNT)  # từ trang khác sẽ chuyển sang products.html


def submit_by_enter(driver):
    driver.find_element(*SEARCH_INPUT).send_keys(Keys.ENTER)
    wait_for(driver, RESULT_COUNT)


def search(driver, text, use_enter=False):
    """Nhập từ khóa và tìm kiếm (bằng nút hoặc phím Enter)."""
    type_query(driver, text)
    (submit_by_enter if use_enter else submit_by_button)(driver)


def result_ids(driver):
    """Danh sách mã sản phẩm đang hiển thị (đã sắp xếp để so sánh không phụ thuộc thứ tự)."""
    cards = driver.find_elements(*PRODUCT_CARDS)
    return sorted(c.get_attribute("data-product-id") for c in cards)


def result_names(driver):
    return [e.text for e in driver.find_elements(By.CSS_SELECTOR, '[id^="product-name-"]')]


def result_count(driver):
    """Đọc số lượng từ dòng 'Tìm thấy X sản phẩm'."""
    text = driver.find_element(*RESULT_COUNT).text
    match = re.search(r"\d+", text)
    assert match, f"Không đọc được số lượng từ: {text!r}"
    return int(match.group())


def has_horizontal_scroll(driver):
    return driver.execute_script(
        "return document.documentElement.scrollWidth > window.innerWidth + 1;"
    )


# --------------------------------------------------------------------------
# Test case
# --------------------------------------------------------------------------
def test_TC_SR_01_hien_thi_o_tim_kiem(driver):
    open_page(driver)
    box = driver.find_element(*SEARCH_INPUT)
    button = driver.find_element(*SEARCH_BUTTON)
    assert box.is_displayed() and box.is_enabled()
    assert button.is_displayed() and button.is_enabled()
    box.send_keys("polo")
    assert box.get_attribute("value") == "polo"


def test_TC_SR_02_tim_theo_ten_san_pham(driver):
    open_page(driver)
    search(driver, PRODUCT_NAME)
    assert PRODUCT_CODE in result_ids(driver)
    assert PRODUCT_NAME in result_names(driver)


def test_TC_SR_03_tim_theo_ma_san_pham(driver):
    open_page(driver)
    search(driver, PRODUCT_CODE)
    assert result_ids(driver) == [PRODUCT_CODE]
    assert result_count(driver) == 1


def test_TC_SR_04_tim_theo_tu_khoa_chung(driver):
    open_page(driver)
    search(driver, "áo polo")
    names = result_names(driver)
    assert result_count(driver) == len(names) > 0
    assert all("polo" in n.lower() for n in names), names


def test_TC_SR_05_tu_khoa_khong_ton_tai(driver):
    open_page(driver)
    search(driver, "xyzabc123")
    assert result_count(driver) == 0
    assert driver.find_elements(*PRODUCT_CARDS) == []
    message = driver.find_element(*NO_RESULT)
    assert message.is_displayed()
    assert message.text.strip() == NO_RESULT_TEXT
    # Trang vẫn hoạt động bình thường (không lỗi)
    assert driver.find_element(*SEARCH_INPUT).is_displayed()


def test_TC_SR_06_khoang_trang_dau_cuoi(driver):
    open_page(driver)
    search(driver, "áo polo")
    expected = result_ids(driver)

    search(driver, " áo polo ")
    # Website có cắt khoảng trắng: kết quả phải giống TC_SR_04
    assert result_ids(driver) == expected
    assert result_count(driver) == len(expected)


def test_TC_SR_07_khong_phan_biet_hoa_thuong(driver):
    open_page(driver)
    search(driver, "quần jeans")
    lower_ids = result_ids(driver)
    assert lower_ids, "Từ khóa 'quần jeans' phải có kết quả"

    search(driver, "QUẦN JEANS")
    assert result_ids(driver) == lower_ids


def test_TC_SR_08_tu_khoa_khong_dau(driver):
    open_page(driver)
    search(driver, "quần jeans")
    with_accent = result_ids(driver)

    search(driver, "quan jeans")
    no_accent = result_ids(driver)
    # Website hỗ trợ tìm không dấu -> cùng kết quả với có dấu
    assert no_accent, "Tìm 'quan jeans' phải trả về sản phẩm"
    assert no_accent == with_accent


def test_TC_SR_09_ky_tu_dac_biet(driver):
    open_page(driver)
    search(driver, "@#$%^&*")
    assert result_count(driver) == 0
    assert driver.find_element(*NO_RESULT).is_displayed()
    assert "error" not in driver.title.lower()
    assert driver.find_element(*SEARCH_INPUT).is_displayed()


def test_TC_SR_10_tu_khoa_rong(driver):
    # Số sản phẩm gốc khi chưa tìm kiếm
    open_page(driver, "products.html")
    wait_for(driver, RESULT_COUNT)
    total = result_count(driver)
    assert total > 0

    search(driver, "polo")
    assert result_count(driver) < total

    search(driver, "")  # để trống rồi bấm tìm
    assert result_count(driver) == total
    assert len(driver.find_elements(*PRODUCT_CARDS)) == total
    assert not driver.find_element(*NO_RESULT).is_displayed()


def test_TC_SR_11_tu_khoa_rat_dai(driver):
    open_page(driver)
    search(driver, "a" * 255)
    assert result_count(driver) == 0
    assert driver.find_element(*NO_RESULT).is_displayed()
    # Giao diện không bị vỡ: không bị tràn ngang
    assert not has_horizontal_scroll(driver)


def test_TC_SR_12_enter_va_nut_tim_kiem(driver):
    open_page(driver)
    search(driver, "áo polo", use_enter=True)
    ids_enter = result_ids(driver)

    open_page(driver)
    search(driver, "áo polo", use_enter=False)
    ids_button = result_ids(driver)

    assert ids_enter, "Phải có kết quả"
    assert ids_enter == ids_button


def test_TC_SR_13_mo_san_pham_tu_ket_qua(driver):
    open_page(driver)
    search(driver, "áo polo")
    first_card = driver.find_elements(*PRODUCT_CARDS)[0]
    product_id = first_card.get_attribute("data-product-id")
    link = driver.find_element(By.ID, f"product-name-{product_id}")
    product_name = link.text
    link.click()

    WebDriverWait(driver, 10).until(EC.url_contains("product-detail.html"))
    assert f"id={product_id}" in driver.current_url
    name_on_detail = wait_for(driver, (By.ID, "detail-product-name"))
    WebDriverWait(driver, 10).until(lambda d: name_on_detail.text.strip() != "")
    assert name_on_detail.text == product_name
    assert driver.find_element(By.ID, "detail-product-code").text == product_id
