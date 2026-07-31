# Ảnh sandbox để chạy test của repo do AI sinh ra.
#
# Vì sao cần ảnh riêng thay vì dùng thẳng python:3.11-slim?
# Vì mỗi lượt sinh có thể chạy test nhiều lần (vòng tự sửa). Cài sẵn pytest vào
# ảnh khiến mỗi lần chạy chỉ mất ~1 giây thay vì phải pip install lại.
FROM python:3.11-slim

# pytest là thứ DUY NHẤT được cài thêm. Bài mini-lab bị ràng buộc chỉ dùng thư
# viện chuẩn của Python, nên không cần gì khác — và càng ít gói thì bề mặt
# tấn công càng nhỏ.
RUN pip install --no-cache-dir pytest==8.3.4 && \
    useradd --create-home --shell /usr/sbin/nologin runner

# Chạy bằng user thường, không phải root.
USER runner
WORKDIR /work

# Không có ENTRYPOINT: lệnh cụ thể do backend truyền vào lúc `docker run`.
