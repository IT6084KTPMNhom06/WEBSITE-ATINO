"""
Selenium WebDriver (Python + pytest) — kiểm thử ĐĂNG NHẬP (bảng TC_LOG_01 .. TC_LOG_10).

Chạy (website phải đang bật):
    pip install -r requirements.txt
    pytest test_login.py -v

Biến môi trường (tùy chọn):  BASE_URL=http://localhost:5500   HEADLESS=1

Ghi chú:
  * Tài khoản dùng cho test: tester.atino01@example.com / Test@1234 (như bảng test case).
    Trước mỗi test, tài khoản này được thêm thẳng vào localStorage ("users") để không phụ thuộc test đăng ký.
    Mỗi test chạy trong một phiên Chrome mới nên localStorage luôn sạch.
  * Website không kiểm tra định dạng email ở form đăng nhập: chuỗi như "abc@" chỉ bị từ chối vì không có
    tài khoản tương ứng (TC_LOG_07 kiểm tra đúng hành vi này).
  * Mật khẩu có phân biệt hoa/thường (TC_LOG_08).
"""
import json
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5500").rstrip("/")

ACCOUNT = {
    "name": "Nguyễn Văn Test",
    "phone": "0912345678",
    "email": "tester.atino01@example.com",
    "password": "Test@1234",
}


# --------------------------------------------------------------------------
# Fixture & hàm hỗ trợ
# --------------------------------------------------------------------------
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
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


def open_login(driver):
    """Mở trang đăng nhập và thêm tài khoản test vào localStorage."""
    driver.get(f"{BASE_URL}/login.html")
    wait_for(driver, (By.ID, "login-form"))
    driver.execute_script(
        """
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        users.push(arguments[0]);
        localStorage.setItem('users', JSON.stringify(users));
        """,
        ACCOUNT,
    )


def set_value(driver, element_id, value):
    el = driver.find_element(By.ID, element_id)
    el.clear()
    if value:
        el.send_keys(value)


def submit_login(driver, account, password):
    set_value(driver, "login-email", account)
    set_value(driver, "login-password", password)
    driver.find_element(By.ID, "login-button").click()
    WebDriverWait(driver, 5).until(
        lambda d: d.find_element(By.ID, "login-message").text.strip() != ""
    )


def login_ok(driver):
    """Đăng nhập đúng tài khoản và chờ về trang chủ."""
    open_login(driver)
    submit_login(driver, ACCOUNT["email"], ACCOUNT["password"])
    WebDriverWait(driver, 10).until(EC.url_contains("index.html"))
    wait_for(driver, (By.ID, "user-name"))


def message(driver):
    return driver.find_element(By.ID, "login-message").text.strip()


def error_of(driver, field):
    return driver.find_element(By.ID, f"login-{field}-error").text.strip()


def current_user(driver):
    raw = driver.execute_script("return window.localStorage.getItem('currentUser');")
    return json.loads(raw) if raw else None


def assert_not_logged_in(driver):
    assert current_user(driver) is None
    assert "login.html" in driver.current_url             # vẫn ở trang đăng nhập
    assert not driver.find_element(By.ID, "user-name").is_displayed()
    assert not driver.find_element(By.ID, "logout-button").is_displayed()


# --------------------------------------------------------------------------
# Test case
# --------------------------------------------------------------------------
def test_TC_LOG_01_hien_thi_bieu_mau_dang_nhap(driver):
    driver.get(f"{BASE_URL}/index.html")
    driver.find_element(By.ID, "login-link").click()
    WebDriverWait(driver, 10).until(EC.url_contains("login.html"))

    for element_id in ["login-email", "login-password", "login-button"]:
        el = wait_for(driver, (By.ID, element_id))
        assert el.is_displayed() and el.is_enabled(), element_id
    assert driver.find_element(By.ID, "login-button").text.strip().lower() == "đăng nhập"
    assert driver.find_element(By.ID, "go-register-link").is_displayed()
    assert driver.find_element(By.ID, "forgot-password-link").is_displayed()


def test_TC_LOG_02_dang_nhap_dung_tai_khoan(driver):
    open_login(driver)
    submit_login(driver, ACCOUNT["email"], ACCOUNT["password"])
    assert "Đăng nhập thành công" in message(driver)

    WebDriverWait(driver, 10).until(EC.url_contains("index.html"))   # tự chuyển về trang chủ
    name = wait_for(driver, (By.ID, "user-name"))
    WebDriverWait(driver, 5).until(lambda d: name.is_displayed())
    assert ACCOUNT["name"] in name.text
    assert driver.find_element(By.ID, "logout-button").is_displayed()
    assert not driver.find_element(By.ID, "login-link").is_displayed()
    assert not driver.find_element(By.ID, "register-link").is_displayed()
    assert current_user(driver)["email"] == ACCOUNT["email"]
    assert "password" not in current_user(driver)   # không lưu mật khẩu vào currentUser


def test_TC_LOG_03_sai_mat_khau(driver):
    open_login(driver)
    submit_login(driver, ACCOUNT["email"], "Sai@12345")

    assert message(driver) == "Mật khẩu không chính xác."
    assert_not_logged_in(driver)


def test_TC_LOG_04_tai_khoan_khong_ton_tai(driver):
    open_login(driver)
    submit_login(driver, "khongtontai@example.com", "Test@1234")

    assert message(driver) == "Tài khoản không tồn tại."
    assert_not_logged_in(driver)


def test_TC_LOG_05_bo_trong_ca_hai_truong(driver):
    open_login(driver)
    submit_login(driver, "", "")

    assert "không thành công" in message(driver)
    assert error_of(driver, "email") == "Vui lòng nhập email hoặc tên đăng nhập."
    assert error_of(driver, "password") == "Vui lòng nhập mật khẩu."
    assert_not_logged_in(driver)


def test_TC_LOG_06_bo_trong_tung_truong(driver):
    open_login(driver)

    # 1) Chỉ nhập tài khoản
    submit_login(driver, ACCOUNT["email"], "")
    assert error_of(driver, "password") == "Vui lòng nhập mật khẩu."
    assert error_of(driver, "email") == ""
    assert_not_logged_in(driver)

    # 2) Chỉ nhập mật khẩu
    submit_login(driver, "", ACCOUNT["password"])
    assert error_of(driver, "email") == "Vui lòng nhập email hoặc tên đăng nhập."
    assert error_of(driver, "password") == ""
    assert_not_logged_in(driver)


def test_TC_LOG_07_tai_khoan_sai_dinh_dang_email(driver):
    open_login(driver)
    submit_login(driver, "abc@", "Test@1234")

    # Website không kiểm tra định dạng email, nhưng từ chối đăng nhập vì không có tài khoản này
    assert message(driver) == "Tài khoản không tồn tại."
    assert_not_logged_in(driver)


def test_TC_LOG_08_mat_khau_phan_biet_hoa_thuong(driver):
    open_login(driver)
    submit_login(driver, ACCOUNT["email"], "test@1234")   # "T" viết thường

    # Ghi nhận: website CÓ phân biệt hoa/thường => từ chối
    assert message(driver) == "Mật khẩu không chính xác."
    assert_not_logged_in(driver)


def test_TC_LOG_09_giu_phien_sau_khi_tai_lai(driver):
    login_ok(driver)
    before = driver.find_element(By.ID, "user-name").text

    driver.refresh()
    name = wait_for(driver, (By.ID, "user-name"))
    WebDriverWait(driver, 5).until(lambda d: name.is_displayed())

    assert name.text == before
    assert driver.find_element(By.ID, "logout-button").is_displayed()
    assert current_user(driver)["email"] == ACCOUNT["email"]


def test_TC_LOG_10_dang_xuat(driver):
    login_ok(driver)

    driver.find_element(By.ID, "logout-button").click()

    WebDriverWait(driver, 5).until(lambda d: d.find_element(By.ID, "login-link").is_displayed())
    assert driver.find_element(By.ID, "register-link").is_displayed()
    assert not driver.find_element(By.ID, "logout-button").is_displayed()
    assert not driver.find_element(By.ID, "user-name").is_displayed()
    assert current_user(driver) is None
    # Đăng xuất rồi tải lại vẫn ở trạng thái chưa đăng nhập
    driver.refresh()
    wait_for(driver, (By.ID, "login-link"))
    assert driver.find_element(By.ID, "login-link").is_displayed()
