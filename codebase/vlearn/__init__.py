"""VLearn Mini Codelab Generator — backend.

Quy trình 2 GIAI ĐOẠN, cố ý tách rời:

  Giai đoạn 1  (/api/generate_repo)
      Slide PDF + mô tả lab chiều (repo .zip HOẶC README.md)
      -> tóm tắt bài lab + REPO CODE hoàn chỉnh, đã chạy pytest thật.
      Lab Coach xem, sửa trong trình duyệt, hoặc tải .zip về sửa bằng IDE rồi
      upload lại. Chỉ khi Coach DUYỆT REPO mới sang giai đoạn 2.

  Giai đoạn 2  (/api/generate_tutorial)
      REPO ĐÃ DUYỆT -> tutorial step-by-step, Bước 0 là tải bộ khung khởi động
      (tests + file setup, KHÔNG có file logic).

Vì sao phải tách? Vì tutorial được sinh TỪ repo đã chốt, nên nội dung từng đoạn
code trong tutorial buộc phải trùng khít file trong repo. Sinh cả hai cùng lúc
thì hai bên sẽ trôi khỏi nhau và học viên làm theo sẽ ra một repo khác.

Bản đồ module:
    config.py         hằng số, nạp .env, chọn model
    extractors.py     đọc slide PDF / repo .zip / README.md
    packaging.py      đóng-mở gói .zip, tách bộ khung khởi động
    openai_client.py  biên giới duy nhất với OpenAI
    prompts/          system prompt 2 giai đoạn (kèm ví dụ vàng)
    security.py       quét tĩnh code do lõi sinh
    testrunner.py     chạy thật pytest trong thư mục tạm
    quality.py        đo toàn vẹn, mật độ giải thích, thời lượng
    auditors.py       chấm bài lõi bằng tiêu chí đo được
    pipeline.py       vòng sinh - chấm - bắt sửa
    http_api.py       định tuyến HTTP
"""

__version__ = '2.0.0'
