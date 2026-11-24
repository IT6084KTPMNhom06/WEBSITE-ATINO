"""
Selenium WebDriver (Python + pytest) — kiểm thử ĐĂNG KÝ (bảng TC_REG_01 .. TC_REG_10).

Chạy (website phải đang bật):
    pip install -r requirements.txt
    pytest test_register.py -v

Biến môi trường (tùy chọn):  BASE_URL=http://localhost:5500   HEADLESS=1

Ghi chú:
  * Mỗi test chạy trong một phiên Chrome mới (localStorage trống) nên các test không ảnh hưởng nhau.
    Lần đầu website tự tạo sẵn 1 tài khoản test, vì vậy ban đầu có 1 user trong localStorage.
  * TC_REG_02 trong bảng ghi "Tự động = Không" (vì tạo tài khoản thật), nhưng với website mô phỏng này
    việc đăng ký chỉ ghi vào localStorage nên vẫn tự động hóa được.
  * TC_REG_08 bị bỏ qua (skip): form đăng ký không có trường "Xác nhận mật khẩu".
  * Có thêm 1 test bổ sung: ký tự đặc biệt trong họ tên.
"""
import json
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

VALID = {
    "name": "Nguyễn Văn Test",
    "phone": "0912345678",
    "email": "tester.atino01@example.com",
    "password": "Test@1234",
}
FIELDS = ["name", "phone", "email", "password"]


# --------------------------------------------------------------------------
# Fixture & hàm hỗ trợ
# --------------------------------------------------------------------------
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,        # tắt popup "Lưu mật khẩu"
        "profile.password_manager_enabled": False,
    })
    if os.environ.get("HEADLESS") == "1":
        options.add_argument("--headless=new")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


def wait_for(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def open_register(driver):
    driver.get(f"{BASE_URL}/register.html")
    wait_for(driver, (By.ID, "register-form"))


def set_value(driver, element_id, value):
    el = driver.find_element(By.ID, element_id)
    el.clear()
    if value:
        el.send_keys(value)


def fill_register(driver, **overrides):
    data = {**VALID, **overrides}
    for field in FIELDS:
        set_value(driver, f"register-{field}", data[field])


def submit_register(driver):
    driver.find_element(By.ID, "register-button").click()
    WebDriverWait(driver, 5).until(
        lambda d: d.find_element(By.ID, "register-message").text.strip() != ""
    )


def message(driver):
    return driver.find_element(By.ID, "register-message").text.strip()


def error_of(driver, field):
    return driver.find_element(By.ID, f"register-{field}-error").text.strip()


def stored_users(driver):
    raw = driver.execute_script("return window.localStorage.getItem('users');")
    return json.loads(raw) if raw else []


def assert_no_new_account(driver, baseline):
    assert len(stored_users(driver)) == baseline, "Không được tạo tài khoản mới"
    assert "register.html" in driver.current_url  # vẫn ở trang đăng ký


# --------------------------------------------------------------------------
# Test case
# --------------------------------------------------------------------------
def test_TC_REG_01_hien_thi_bieu_mau_dang_ky(driver):
    driver.get(f"{BASE_URL}/index.html")
    driver.find_element(By.ID, "register-link").click()
    WebDriverWait(driver, 10).until(EC.url_contains("register.html"))

    assert driver.current_url.endswith("/register.html")
    assert "Đăng ký" in driver.title
    for field in FIELDS:
        el = wait_for(driver, (By.ID, f"register-{field}"))
        assert el.is_displayed() and el.is_enabled(), field
    button = driver.find_element(By.ID, "register-button")
    assert button.is_displayed() and button.text.strip() == "Đăng ký"


def test_TC_REG_02_dang_ky_du_lieu_hop_le(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver)
    submit_register(driver)

    assert "Đăng ký thành công" in message(driver)
    assert "is-success" in driver.find_element(By.ID, "register-message").get_attribute("class")
    assert all(error_of(driver, f) == "" for f in FIELDS)
    users = stored_users(driver)
    assert len(users) == baseline + 1
    assert users[-1]["email"] == VALID["email"]
    assert users[-1]["name"] == VALID["name"]


def test_TC_REG_03_bo_trong_toan_bo_truong(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    submit_register(driver)

    assert "không thành công" in message(driver)
    assert all(error_of(driver, f) != "" for f in FIELDS), [error_of(driver, f) for f in FIELDS]
    assert_no_new_account(driver, baseline)


@pytest.mark.parametrize("field,expected", [
    ("name", "Vui lòng nhập họ tên."),
    ("email", "Vui lòng nhập email."),
    ("password", "Vui lòng nhập mật khẩu."),
    ("phone", "Vui lòng nhập số điện thoại."),   # bổ sung: SĐT cũng là trường bắt buộc
])
def test_TC_REG_04_bo_trong_tung_truong(driver, field, expected):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver, **{field: ""})
    submit_register(driver)

    assert error_of(driver, field) == expected
    # Chỉ trường bị bỏ trống bị cảnh báo
    assert all(error_of(driver, f) == "" for f in FIELDS if f != field)
    assert_no_new_account(driver, baseline)


def test_TC_REG_05_email_sai_dinh_dang(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver, email="abc@")
    submit_register(driver)

    assert error_of(driver, "email") == "Email không đúng định dạng."
    assert_no_new_account(driver, baseline)


@pytest.mark.parametrize("phone,expected", [
    ("091234567", "phải gồm 10 chữ số"),       # thiếu chữ số
    ("09123abc78", "chỉ được chứa chữ số"),    # chứa chữ
])
def test_TC_REG_06_so_dien_thoai_sai_dinh_dang(driver, phone, expected):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver, phone=phone)
    submit_register(driver)

    assert expected in error_of(driver, "phone")
    assert_no_new_account(driver, baseline)


def test_TC_REG_07_mat_khau_qua_ngan(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver, password="12345")
    submit_register(driver)

    assert "ít nhất 8 ký tự" in error_of(driver, "password")
    assert_no_new_account(driver, baseline)


@pytest.mark.skip(reason="TC_REG_08: form đăng ký của website mô phỏng không có trường 'Xác nhận mật khẩu'.")
def test_TC_REG_08_xac_nhan_mat_khau_khong_khop(driver):
    pass


def test_TC_REG_09_dang_ky_email_da_ton_tai(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    # Đăng ký lần 1 (như TC_REG_02)
    fill_register(driver)
    submit_register(driver)
    assert "Đăng ký thành công" in message(driver)
    assert len(stored_users(driver)) == baseline + 1

    # Đăng ký lần 2 với cùng email (các trường còn lại hợp lệ, khác dữ liệu)
    fill_register(driver, name="Trần Thị Khác", phone="0987654321")
    submit_register(driver)

    assert "đã được đăng ký" in error_of(driver, "email")
    assert "không thành công" in message(driver)
    assert_no_new_account(driver, baseline + 1)  # không tạo thêm tài khoản trùng

    # Email khác hoa/thường vẫn bị coi là trùng
    set_value(driver, "register-email", VALID["email"].upper())
    set_value(driver, "register-password", VALID["password"])
    driver.find_element(By.ID, "register-button").click()
    assert "đã được đăng ký" in error_of(driver, "email")
    assert len(stored_users(driver)) == baseline + 1


def test_TC_REG_10_chuyen_sang_dang_nhap(driver):
    open_register(driver)
    driver.find_element(By.ID, "go-login-link").click()

    WebDriverWait(driver, 10).until(EC.url_contains("login.html"))
    assert driver.current_url.endswith("/login.html")
    assert driver.find_element(By.ID, "login-form").is_displayed()


def test_bo_sung_ky_tu_dac_biet_trong_ho_ten(driver):
    open_register(driver)
    baseline = len(stored_users(driver))

    fill_register(driver, name="An@#$%")
    submit_register(driver)

    assert "đặc biệt" in error_of(driver, "name")
    assert_no_new_account(driver, baseline)
