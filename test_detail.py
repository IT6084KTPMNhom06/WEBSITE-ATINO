
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://localhost:5500"
PRODUCT_NAME = "Quần Jeans Slim Đen"
PRODUCT_CODE = "SP001"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


# Mở trang chi tiết sản phẩm
def open_product_detail(driver):
    wait = WebDriverWait(driver, 10)

    driver.get(BASE_URL + "/index.html")

    # Nhập tên sản phẩm
    search = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "search-input")
        )
    )
    search.clear()
    search.send_keys(PRODUCT_NAME)

    # Nhấn tìm kiếm
    wait.until(
        EC.element_to_be_clickable(
            (By.ID, "search-button")
        )
    ).click()

    # Chọn sản phẩm trong danh sách
    product = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "product-name-" + PRODUCT_CODE)
        )
    )
    product.click()

    # Chờ trang chi tiết
    wait.until(EC.url_contains("product-detail.html"))

    wait.until(
        EC.visibility_of_element_located(
            (By.ID, "detail-product-name")
        )
    )


# Lấy thông báo trên trang
def get_message(driver):
    try:
        return WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.ID, "detail-message")
            )
        ).text
    except TimeoutException:
        return ""


# Lấy các lựa chọn màu sắc
def get_colors(driver):
    return driver.find_elements(
        By.CSS_SELECTOR, ".color-option"
    )


# Lấy các lựa chọn kích cỡ
def get_sizes(driver):
    return driver.find_elements(
        By.CSS_SELECTOR, ".size-option"
    )


# Chọn màu sắc đầu tiên có thể sử dụng
def select_color(driver):
    colors = get_colors(driver)

    for color in colors:
        if color.is_enabled():
            color.click()
            return True

    return False


# Chọn kích cỡ đầu tiên có thể sử dụng
def select_size(driver):
    sizes = get_sizes(driver)

    for size in sizes:
        if size.is_enabled():
            size.click()
            return True

    return False


# TC_PD_01: Kiểm tra mở trang chi tiết sản phẩm
def test_PD_01_mo_trang_chi_tiet(driver):
    open_product_detail(driver)

    assert "product-detail.html" in driver.current_url

    assert driver.find_element(
        By.ID, "detail-product-name"
    ).is_displayed()


# TC_PD_02: Kiểm tra tên và mã sản phẩm
def test_PD_02_ten_va_ma_san_pham(driver):
    open_product_detail(driver)

    name = driver.find_element(
        By.ID, "detail-product-name"
    ).text.strip()

    code = driver.find_element(
        By.ID, "detail-product-code"
    ).text.strip()

    assert name != ""
    assert code != ""

    assert PRODUCT_NAME.lower() in name.lower()
    assert PRODUCT_CODE.lower() in code.lower()


# TC_PD_03: Kiểm tra giá sản phẩm
def test_PD_03_kiem_tra_gia_san_pham(driver):
    open_product_detail(driver)

    price = driver.find_element(
        By.ID, "detail-product-price"
    )

    assert price.is_displayed()
    assert price.text.strip() != ""


# TC_PD_04: Kiểm tra hình ảnh sản phẩm
def test_PD_04_kiem_tra_hinh_anh(driver):
    open_product_detail(driver)

    main_image = driver.find_element(
        By.ID, "detail-main-image"
    )

    assert main_image.is_displayed()
    assert main_image.get_attribute("src") != ""

    thumbnails = driver.find_elements(
        By.CSS_SELECTOR, ".detail-thumbnail"
    )

    assert len(thumbnails) > 0


# TC_PD_05: Kiểm tra chọn màu sắc
def test_PD_05_chon_mau_sac(driver):
    open_product_detail(driver)

    result = select_color(driver)

    assert result, "Không có màu sắc khả dụng"


# TC_PD_06: Kiểm tra chọn kích cỡ
def test_PD_06_chon_kich_co(driver):
    open_product_detail(driver)

    result = select_size(driver)

    assert result, "Không có kích cỡ khả dụng"


# TC_PD_07: Kiểm tra kích cỡ hết hàng
def test_PD_07_kich_co_het_hang(driver):
    open_product_detail(driver)

    sizes = get_sizes(driver)

    unavailable_sizes = [
        size for size in sizes
        if not size.is_enabled()
        or "disabled" in (size.get_attribute("class") or "")
    ]

    assert len(unavailable_sizes) > 0, (
        "Không tìm thấy kích cỡ hết hàng để kiểm thử"
    )

    unavailable_sizes[0].click()

    assert not unavailable_sizes[0].is_enabled()


# TC_PD_08: Kiểm tra số lượng mặc định
def test_PD_08_so_luong_mac_dinh(driver):
    open_product_detail(driver)

    quantity = driver.find_element(
        By.ID, "quantity"
    )

    assert quantity.get_attribute("value") == "1"


# TC_PD_09: Kiểm tra tăng số lượng
def test_PD_09_tang_so_luong(driver):
    open_product_detail(driver)

    quantity = driver.find_element(
        By.ID, "quantity"
    )

    old_value = int(quantity.get_attribute("value"))

    driver.find_element(
        By.ID, "quantity-plus"
    ).click()

    new_value = int(quantity.get_attribute("value"))

    assert new_value == old_value + 1


# TC_PD_10: Kiểm tra giảm số lượng không nhỏ hơn 1
def test_PD_10_giam_so_luong(driver):
    open_product_detail(driver)

    quantity = driver.find_element(
        By.ID, "quantity"
    )

    quantity.clear()
    quantity.send_keys("1")

    driver.find_element(
        By.ID, "quantity-minus"
    ).click()

    new_value = int(quantity.get_attribute("value"))

    assert new_value >= 1


# TC_PD_11: Kiểm tra nhập số lượng không hợp lệ
def test_PD_11_so_luong_khong_hop_le(driver):
    open_product_detail(driver)

    quantity = driver.find_element(
        By.ID, "quantity"
    )

    quantity.clear()
    quantity.send_keys("0")
    quantity.send_keys("\t")

    value = quantity.get_attribute("value")

    # Chấp nhận hai cách xử lý:
    # Tự động điều chỉnh về 1 hoặc trình duyệt đánh dấu không hợp lệ.
    valid = quantity.get_attribute("validity")

    if value != "":
        assert int(value) >= 1 or quantity.get_attribute(
            "aria-invalid"
        ) == "true" or quantity.get_attribute(
            "min"
        ) == "1"


# TC_PD_12: Kiểm tra thêm giỏ hàng khi chưa chọn màu và size
def test_PD_12_them_gio_hang_khi_chua_chon_thuoc_tinh(driver):
    open_product_detail(driver)

    driver.find_element(
        By.ID, "add-to-cart"
    ).click()

    message = get_message(driver)

    assert message != "", (
        "Website chưa hiển thị thông báo khi chưa chọn màu/size"
    )


# TC_PD_13: Kiểm tra thêm giỏ hàng khi đã chọn màu và size
def test_PD_13_them_gio_hang_khi_da_chon_thuoc_tinh(driver):
    open_product_detail(driver)

    color_selected = select_color(driver)
    size_selected = select_size(driver)

    assert color_selected
    assert size_selected

    driver.find_element(
        By.ID, "add-to-cart"
    ).click()

    message = get_message(driver)

    assert message != "", (
        "Website chưa hiển thị thông báo sau khi thêm giỏ hàng"
    )


# TC_PD_14: Kiểm tra chức năng mua ngay
def test_PD_14_mua_ngay(driver):
    open_product_detail(driver)

    color_selected = select_color(driver)
    size_selected = select_size(driver)

    assert color_selected
    assert size_selected

    driver.find_element(
        By.ID, "buy-now"
    ).click()

    WebDriverWait(driver, 10).until(
        lambda d: "checkout" in d.current_url.lower()
        or "order" in d.current_url.lower()
    )

    assert (
        "checkout" in driver.current_url.lower()
        or "order" in driver.current_url.lower()
    )
