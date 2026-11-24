"""
Selenium WebDriver (Python + pytest) — kiểm thử QUẢN LÝ GIỎ HÀNG (bảng TC_CART_01 .. TC_CART_15).

Chạy (website phải đang bật):
    pip install -r requirements.txt
    pytest test_cart.py -v

Biến môi trường (tùy chọn):  BASE_URL=http://localhost:5500   HEADLESS=1

Dữ liệu đã đổi cho khớp website mô phỏng:
    "Quần Jeans Straight 30.1.1359" -> SP001 "Quần Jeans Slim Đen" (399.000đ, tồn kho 20)
    Sản phẩm B                      -> SP005 "Áo Polo Basic Trắng" (289.000đ)

Hành vi thực tế của website (các test "ghi nhận" kiểm tra đúng hành vi này):
  * Mỗi sản phẩm chỉ có MỘT dòng trong giỏ. Thêm lại cùng sản phẩm => cộng dồn số lượng.
    Thêm cùng sản phẩm với size khác (TC_CART_07) cũng gộp vào 1 dòng và lấy size mới nhất.
  * Số lượng trong giỏ tối thiểu là 1 (nút giảm bị khóa ở 1). Số lượng tối đa = tồn kho (SP001: 20).
  * Giỏ hàng lưu ở localStorage nên còn nguyên sau khi tải lại trang.
"""
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

A = {"id": "SP001", "name": "Quần Jeans Slim Đen", "price": 399000, "stock": 20}
B = {"id": "SP005", "name": "Áo Polo Basic Trắng", "price": 289000}
COLOR_CODE = {"Đen": "black", "Trắng": "white", "Xanh": "blue", "Xám": "gray", "Be": "beige"}


def money(n):
    """399000 -> '399.000đ'"""
    return f"{n:,}".replace(",", ".") + "đ"


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


def open_detail(driver, product_id):
    driver.get(f"{BASE_URL}/product-detail.html?id={product_id}")
    name = wait_for(driver, (By.ID, "detail-product-name"))
    WebDriverWait(driver, 10).until(lambda d: name.text.strip() != "")


def set_quantity(driver, value):
    box = driver.find_element(By.ID, "quantity-input")
    box.clear()
    box.send_keys(str(value))
    box.send_keys(Keys.TAB)   # rời ô để website kiểm tra giới hạn số lượng


def add_from_detail(driver, product_id, size, color=None, qty=1):
    """Mở trang chi tiết, chọn màu / size / số lượng rồi bấm 'Thêm vào giỏ'."""
    open_detail(driver, product_id)
    if color:
        driver.find_element(By.ID, f"color-option-{COLOR_CODE[color]}").click()
    if size:
        driver.find_element(By.ID, f"size-option-{size.lower()}").click()
    if qty != 1:
        set_quantity(driver, qty)
    driver.find_element(By.ID, "add-to-cart").click()
    WebDriverWait(driver, 5).until(
        lambda d: "Đã thêm" in d.find_element(By.ID, "detail-message").text
    )


def open_cart(driver):
    driver.get(f"{BASE_URL}/cart.html")
    wait_for(driver, (By.ID, "cart-title"))


def cart_ids(driver):
    rows = driver.find_elements(By.CSS_SELECTOR, "#cart-items li.cart-item")
    return [r.get_attribute("data-product-id") for r in rows]


def qty_of(driver, product_id):
    return int(driver.find_element(By.ID, f"cart-quantity-{product_id}").text)


def subtotal_of(driver, product_id):
    return int(driver.find_element(By.ID, f"cart-subtotal-{product_id}").get_attribute("data-amount"))


def total_amount(driver):
    return int(driver.find_element(By.ID, "cart-total").get_attribute("data-amount"))


def header_count(driver):
    return int(driver.find_element(By.ID, "cart-count").text)


def click(driver, element_id):
    driver.find_element(By.ID, element_id).click()


# --------------------------------------------------------------------------
# Test case
# --------------------------------------------------------------------------
def test_TC_CART_01_gio_hang_trong(driver):
    open_cart(driver)

    empty = driver.find_element(By.ID, "cart-empty")
    assert empty.is_displayed()
    assert "Giỏ hàng của bạn đang trống." in empty.text
    assert not driver.find_element(By.ID, "cart-content").is_displayed()
    assert header_count(driver) == 0
    assert driver.find_element(By.ID, "cart-total").get_attribute("textContent") == "0đ"
    assert cart_ids(driver) == []

    # Liên kết quay lại mua sắm
    link = driver.find_element(By.ID, "cart-continue")
    assert link.is_displayed()
    link.click()
    WebDriverWait(driver, 10).until(EC.url_contains("products.html"))


def test_TC_CART_02_them_mot_san_pham(driver):
    add_from_detail(driver, A["id"], size="M", color="Đen", qty=1)

    assert header_count(driver) == 1
    assert "Đã thêm vào giỏ hàng." in driver.find_element(By.ID, "detail-message").text


def test_TC_CART_03_thong_tin_dong_san_pham(driver):
    open_detail(driver, A["id"])
    name = driver.find_element(By.ID, "detail-product-name").text
    price = driver.find_element(By.ID, "detail-product-price").text
    click(driver, "color-option-blue")
    click(driver, "size-option-m")
    color = driver.find_element(By.ID, "detail-selected-color").text   # Xanh
    size = driver.find_element(By.ID, "detail-selected-size").text     # M
    click(driver, "add-to-cart")
    WebDriverWait(driver, 5).until(lambda d: "Đã thêm" in d.find_element(By.ID, "detail-message").text)

    open_cart(driver)
    pid = A["id"]
    assert driver.find_element(By.ID, f"cart-name-{pid}").text == name
    assert driver.find_element(By.ID, f"cart-price-{pid}").text == price
    variant = driver.find_element(By.ID, f"cart-variant-{pid}").text
    assert f"Size {size}" in variant and f"Màu {color}" in variant, variant
    assert qty_of(driver, pid) == 1


def test_TC_CART_04_tong_tien_mot_san_pham(driver):
    add_from_detail(driver, A["id"], size="M", qty=2)
    open_cart(driver)

    pid = A["id"]
    assert qty_of(driver, pid) == 2
    assert subtotal_of(driver, pid) == A["price"] * 2
    assert total_amount(driver) == A["price"] * 2
    assert driver.find_element(By.ID, "cart-total").text == money(A["price"] * 2)   # 798.000đ


def test_TC_CART_05_them_hai_san_pham_khac_nhau(driver):
    add_from_detail(driver, A["id"], size="M")
    add_from_detail(driver, B["id"], size="M")
    open_cart(driver)

    assert sorted(cart_ids(driver)) == sorted([A["id"], B["id"]])
    assert subtotal_of(driver, A["id"]) + subtotal_of(driver, B["id"]) == total_amount(driver)
    assert total_amount(driver) == A["price"] + B["price"]
    assert header_count(driver) == 2


def test_TC_CART_06_them_lai_cung_san_pham_cung_size_mau(driver):
    add_from_detail(driver, A["id"], size="M", color="Đen")
    add_from_detail(driver, A["id"], size="M", color="Đen")
    open_cart(driver)

    # Ghi nhận: website cộng dồn vào 1 dòng
    assert cart_ids(driver) == [A["id"]]
    assert qty_of(driver, A["id"]) == 2
    assert total_amount(driver) == A["price"] * 2
    assert header_count(driver) == 2


def test_TC_CART_07_cung_san_pham_khac_size(driver):
    add_from_detail(driver, A["id"], size="M")
    add_from_detail(driver, A["id"], size="L")
    open_cart(driver)

    # Ghi nhận: website gộp thành 1 dòng (số lượng 2) và hiển thị size chọn sau cùng.
    # Tổng tiền và số lượng vẫn nhất quán.
    assert cart_ids(driver) == [A["id"]]
    assert qty_of(driver, A["id"]) == 2
    assert "Size L" in driver.find_element(By.ID, f"cart-variant-{A['id']}").text
    assert total_amount(driver) == A["price"] * 2
    assert header_count(driver) == 2


def test_TC_CART_08_tang_so_luong(driver):
    add_from_detail(driver, A["id"], size="M")
    open_cart(driver)
    assert qty_of(driver, A["id"]) == 1

    click(driver, f"cart-increase-{A['id']}")

    assert qty_of(driver, A["id"]) == 2
    assert subtotal_of(driver, A["id"]) == A["price"] * 2
    assert total_amount(driver) == A["price"] * 2
    assert header_count(driver) == 2


def test_TC_CART_09_giam_so_luong_ve_duoi_1(driver):
    add_from_detail(driver, A["id"], size="M")
    open_cart(driver)

    # Ghi nhận: khi số lượng là 1, nút giảm bị khóa; số lượng không xuống dưới 1
    decrease = driver.find_element(By.ID, f"cart-decrease-{A['id']}")
    assert not decrease.is_enabled()
    assert qty_of(driver, A["id"]) == 1
    assert cart_ids(driver) == [A["id"]]


def test_TC_CART_09b_nhap_so_luong_0_o_trang_chi_tiet(driver):
    open_detail(driver, A["id"])
    set_quantity(driver, 0)

    assert driver.find_element(By.ID, "quantity-input").get_attribute("value") == "1"
    assert "Số lượng tối thiểu là 1." in driver.find_element(By.ID, "detail-message").text
    assert header_count(driver) == 0


@pytest.mark.parametrize("typed", [99, 100])
def test_TC_CART_10_so_luong_lon(driver, typed):
    open_detail(driver, A["id"])
    click(driver, "size-option-m")
    set_quantity(driver, typed)

    # Ghi nhận: website giới hạn theo tồn kho (SP001 còn 20)
    box = driver.find_element(By.ID, "quantity-input")
    assert box.get_attribute("value") == str(A["stock"])
    assert f"Chỉ còn {A['stock']} sản phẩm trong kho." in driver.find_element(By.ID, "detail-message").text

    click(driver, "add-to-cart")
    WebDriverWait(driver, 5).until(lambda d: "Đã thêm" in d.find_element(By.ID, "detail-message").text)
    open_cart(driver)
    assert qty_of(driver, A["id"]) == A["stock"]
    assert total_amount(driver) == A["price"] * A["stock"]
    assert not driver.find_element(By.ID, f"cart-increase-{A['id']}").is_enabled()   # đã chạm tồn kho


def test_TC_CART_11_xoa_mot_san_pham(driver):
    add_from_detail(driver, A["id"], size="M")
    add_from_detail(driver, B["id"], size="M")
    open_cart(driver)
    assert len(cart_ids(driver)) == 2

    click(driver, f"cart-remove-{A['id']}")

    assert cart_ids(driver) == [B["id"]]
    assert qty_of(driver, B["id"]) == 1       # dòng còn lại giữ nguyên
    assert total_amount(driver) == B["price"]
    assert header_count(driver) == 1


def test_TC_CART_12_xoa_toan_bo_san_pham(driver):
    add_from_detail(driver, A["id"], size="M")
    add_from_detail(driver, B["id"], size="M")
    open_cart(driver)

    click(driver, f"cart-remove-{A['id']}")
    click(driver, f"cart-remove-{B['id']}")

    assert cart_ids(driver) == []
    assert driver.find_element(By.ID, "cart-empty").is_displayed()
    assert driver.find_element(By.ID, "cart-total").get_attribute("textContent") == "0đ"
    assert header_count(driver) == 0


def test_TC_CART_12b_nut_xoa_toan_bo_gio_hang(driver):
    add_from_detail(driver, A["id"], size="M")
    add_from_detail(driver, B["id"], size="M")
    open_cart(driver)

    click(driver, "cart-clear")

    assert cart_ids(driver) == []
    assert driver.find_element(By.ID, "cart-empty").is_displayed()
    assert header_count(driver) == 0


def test_TC_CART_13_giu_gio_hang_sau_khi_tai_lai(driver):
    add_from_detail(driver, A["id"], size="M")
    driver.refresh()
    wait_for(driver, (By.ID, "cart-count"))
    assert header_count(driver) == 1          # Ghi nhận: giỏ hàng còn nguyên

    open_cart(driver)
    driver.refresh()
    wait_for(driver, (By.ID, "cart-title"))
    assert cart_ids(driver) == [A["id"]]
    assert qty_of(driver, A["id"]) == 1


def test_TC_CART_14_mua_them_san_pham(driver):
    add_from_detail(driver, A["id"], size="M")
    open_cart(driver)

    click(driver, "cart-add-more")

    WebDriverWait(driver, 10).until(EC.url_contains("products.html"))
    wait_for(driver, (By.ID, "search-result-count"))
    assert header_count(driver) == 1          # giỏ vẫn giữ sản phẩm
    open_cart(driver)
    assert cart_ids(driver) == [A["id"]]


def test_TC_CART_15_tien_hanh_dat_hang(driver):
    add_from_detail(driver, A["id"], size="M")
    open_cart(driver)

    click(driver, "checkout-button")

    WebDriverWait(driver, 10).until(EC.url_contains("checkout.html"))
    assert driver.find_element(By.ID, "checkout-form").is_displayed()
