# IMPLEMENTATION_GUIDE.md

# Hệ thống hỗ trợ chỉnh sửa tài liệu DOCX dựa trên báo cáo kiểm tra tương đồng
**Phiên bản:** 1.1  
**Ngôn ngữ tài liệu:** Tiếng Việt  
**Phạm vi:** Backend + Orchestration + Validation + UX + UI

---

## 1. Mục tiêu

Xây dựng một hệ thống phần mềm nhận vào:

- `source.docx`: tài liệu cần chỉnh sửa
- `report.pdf`: báo cáo kết quả kiểm tra tương đồng / trùng lặp

Hệ thống phải:

1. Phân tích file DOCX và PDF
2. Xác định các đoạn trong DOCX có rủi ro trùng lặp hoặc cần diễn đạt lại
3. Tạo các đơn vị chỉnh sửa (`repair units`)
4. Gọi các LLM theo thứ tự ưu tiên:
   - `Groq`
   - nếu lỗi thì chuyển sang `OpenRouter`
   - nếu tiếp tục lỗi thì chuyển sang `Gemini`
5. Kiểm tra chất lượng đầu ra
6. Ghi lại nội dung đã chỉnh sửa vào file DOCX mới
7. Xuất báo cáo thay đổi
8. Cung cấp giao diện UX/UI để người dùng tải file, theo dõi tiến trình, xem kết quả, xem diff và tải đầu ra

---

## 2. Nguyên tắc bắt buộc

Hệ thống này là công cụ hỗ trợ **chỉnh sửa hợp lệ**, không phải công cụ để lách kiểm tra đạo văn.

### Bắt buộc
- Giữ nguyên nghĩa gốc của đoạn văn
- Không bịa thông tin mới
- Không tự thêm nguồn tham khảo giả
- Nếu đoạn văn có dấu hiệu cần trích dẫn, phải đánh dấu để người dùng kiểm tra
- Giữ tối đa cấu trúc tài liệu DOCX
- Có cơ chế fallback giữa các model
- Có log đầy đủ cho từng lần gọi model
- Có giao diện rõ ràng, dễ hiểu, thể hiện minh bạch trạng thái xử lý và lý do thay đổi

### Không được
- Tối ưu theo hướng “qua mặt” công cụ kiểm tra
- Tự động thêm citation bịa đặt
- Chỉnh sửa làm sai lệch luận điểm, dữ kiện, số liệu
- Ghi đè nội dung gốc mà không lưu lịch sử thay đổi
- Hiển thị kết quả mơ hồ, không giải thích hoặc không cho người dùng cơ chế kiểm tra lại

---

## 3. Phạm vi MVP

Phiên bản MVP phải hỗ trợ:

- Upload `DOCX` và `PDF`
- Parse nội dung từ `DOCX`
- Parse text từ `PDF`
- Tìm và map các đoạn nghi ngờ trong PDF về DOCX
- Chia thành `repair units`
- Rewrite từng unit qua chuỗi:
  - `Groq -> OpenRouter -> Gemini`
- Validate đầu ra
- Xuất:
  - `revised.docx`
  - `change_report.json`
- Cung cấp UI tối thiểu:
  - trang upload
  - trang theo dõi job
  - trang review kết quả
  - nút tải output

---

## 4. Kiến trúc tổng thể

```text
Client/UI
   |
   v
API Gateway
   |
   +--> File Processor
   |       +--> DOCX Parser
   |       +--> PDF Parser
   |
   +--> Alignment Engine
   |       +--> Report-to-DOCX Mapping
   |       +--> Repair Unit Generator
   |
   +--> LLM Orchestrator
   |       +--> Groq Provider
   |       +--> OpenRouter Provider
   |       +--> Gemini Provider
   |
   +--> Validation Service
   |       +--> Schema Validator
   |       +--> Meaning Preservation Check
   |       +--> Citation Risk Check
   |       +--> Language Quality Check
   |
   +--> Document Builder
   |       +--> DOCX Rewriter
   |       +--> Output Generator
   |
   +--> Storage
           +--> Files
           +--> Metadata DB
           +--> Logs
```

---

## 5. Công nghệ khuyến nghị

### Backend
- `Python 3.11+`
- `FastAPI`
- `Pydantic`
- `SQLAlchemy`
- `PostgreSQL`
- `Redis` cho queue / cache
- `Celery` hoặc `RQ` cho background jobs

### Xử lý file
- `python-docx` để đọc/ghi DOCX
- `PyMuPDF` hoặc `pdfplumber` để đọc PDF
- OCR chỉ dùng khi bắt buộc:
  - `Tesseract` hoặc dịch vụ OCR ngoài

### Logging / Observability
- `structlog` hoặc logging JSON
- `Prometheus` + `Grafana` nếu cần monitoring
- `Sentry` cho exception tracking

### Frontend
- `Next.js`
- `React`
- `TypeScript`
- `Tailwind CSS`
- `shadcn/ui` hoặc component library tương đương

---

## 6. Cấu trúc thư mục đề xuất

```text
app/
  api/
    routes/
      jobs.py
      files.py
      health.py
  core/
    config.py
    logging.py
    exceptions.py
  models/
    job.py
    repair_unit.py
    provider_attempt.py
    rewrite_result.py
  schemas/
    job.py
    llm.py
    repair.py
  services/
    file_processor.py
    docx_parser.py
    pdf_parser.py
    alignment_service.py
    orchestrator.py
    validator.py
    document_builder.py
    report_service.py
  providers/
    base.py
    groq_provider.py
    openrouter_provider.py
    gemini_provider.py
  repositories/
    job_repo.py
    repair_repo.py
    attempt_repo.py
  workers/
    tasks.py
  utils/
    text_matching.py
    retries.py
    hashing.py
    diff_utils.py

frontend/
  app/
    upload/
    jobs/[jobId]/
    review/[jobId]/
  components/
    upload/
    job/
    review/
    common/
  lib/
    api.ts
    format.ts
    constants.ts
  styles/

tests/
docs/
  IMPLEMENTATION_GUIDE.md
```

---

## 7. Luồng xử lý chính

### Bước 1. Tạo job
Người dùng upload:
- `source.docx`
- `report.pdf`

Server:
- tạo `job_id`
- lưu file vào storage
- set trạng thái `UPLOADED`

### Bước 2. Parse file
- Đọc toàn bộ DOCX thành cấu trúc paragraph/block
- Đọc PDF report
- Trích ra các vùng:
  - đoạn bị đánh dấu
  - mức tương đồng
  - nguồn liên quan
  - page index

### Bước 3. Alignment
Map nội dung PDF sang các paragraph trong DOCX bằng:
- fuzzy match
- similarity score
- anchor phrases
- sentence overlap

Kết quả là danh sách `repair units`.

### Bước 4. Rewrite từng unit
Với mỗi `repair unit`:
1. Gọi `Groq`
2. Nếu lỗi thì gọi `OpenRouter`
3. Nếu lỗi tiếp thì gọi `Gemini`
4. Nếu cả 3 thất bại, chuyển `MANUAL_REVIEW`

### Bước 5. Validation
Kiểm tra:
- output đúng schema
- không rỗng
- không lệch nghĩa nghiêm trọng
- ngôn ngữ hợp lý
- có cờ `citation_needed` nếu phù hợp

### Bước 6. Rebuild DOCX
- Ghi đoạn đã sửa vào đúng paragraph
- Giữ nguyên định dạng tốt nhất có thể
- Tạo `revised.docx`

### Bước 7. Xuất báo cáo
Sinh:
- `change_report.json`
- tùy chọn `review.html`

---

## 8. Data model

### 8.1 Bảng `jobs`

```json
{
  "id": "uuid",
  "status": "UPLOADED | PARSING | ALIGNING | REWRITING | VALIDATING | BUILDING | COMPLETED | FAILED | MANUAL_REVIEW",
  "source_docx_path": "string",
  "report_pdf_path": "string",
  "output_docx_path": "string|null",
  "change_report_path": "string|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 8.2 Bảng `repair_units`

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "paragraph_ref": "string",
  "section_ref": "string|null",
  "original_text": "string",
  "report_excerpt": "string|null",
  "matched_source_text": "string|null",
  "risk_type": "VERBATIM | CLOSE_PARAPHRASE | MISSING_CITATION | OTHER",
  "similarity_score": 0.0,
  "status": "PENDING | PROCESSING | REWRITTEN | VALIDATION_FAILED | MANUAL_REVIEW",
  "selected_provider": "groq|openrouter|gemini|null"
}
```

### 8.3 Bảng `provider_attempts`

```json
{
  "id": "uuid",
  "repair_unit_id": "uuid",
  "provider_name": "groq|openrouter|gemini",
  "status": "SUCCESS | TIMEOUT | RATE_LIMIT | API_ERROR | INVALID_SCHEMA | QUALITY_FAIL",
  "error_message": "string|null",
  "latency_ms": 0,
  "started_at": "datetime",
  "ended_at": "datetime"
}
```

### 8.4 Bảng `rewrite_results`

```json
{
  "id": "uuid",
  "repair_unit_id": "uuid",
  "provider_name": "groq|openrouter|gemini",
  "rewritten_text": "string",
  "summary_of_changes": "string",
  "citation_needed": true,
  "confidence": 0.0,
  "validator_score": 0.0,
  "accepted": true
}
```

---

## 9. Repair unit schema

Mỗi `repair unit` là đơn vị tối thiểu để gửi sang LLM.

```json
{
  "unit_id": "uuid",
  "document_context": {
    "section_title": "string|null",
    "previous_paragraph": "string|null",
    "current_paragraph": "string",
    "next_paragraph": "string|null"
  },
  "report_context": {
    "report_excerpt": "string|null",
    "source_reference": "string|null",
    "risk_type": "VERBATIM | CLOSE_PARAPHRASE | MISSING_CITATION | OTHER",
    "similarity_score": 0.0
  },
  "constraints": {
    "preserve_meaning": true,
    "do_not_add_facts": true,
    "mark_if_citation_needed": true,
    "tone": "academic",
    "language": "vi"
  }
}
```

---

## 10. Hướng dẫn implement parser

### 10.1 DOCX Parser
Phải:
- đọc paragraph theo thứ tự
- giữ metadata vị trí:
  - section
  - paragraph index
  - style name
  - text
- tách text sạch để matching
- giữ mapping giữa text và object paragraph gốc

### Output đề xuất
```json
{
  "paragraphs": [
    {
      "paragraph_ref": "p_0001",
      "style": "Normal",
      "section": "1. Giới thiệu",
      "text": "Nội dung đoạn văn..."
    }
  ]
}
```

### 10.2 PDF Parser
Ưu tiên:
1. text extraction
2. layout-based extraction
3. OCR fallback

Phải cố gắng trích:
- page number
- highlighted text / suspicious text
- similarity percentage
- source label / URL nếu có

Nếu parser không chắc chắn, phải gắn cờ:
- `low_confidence_parse = true`

---

## 11. Hướng dẫn implement alignment engine

Mục tiêu:
- map đoạn bị flag trong report vào đúng paragraph của DOCX

### Chiến lược đề xuất
Kết hợp:
- normalized text match
- sentence token overlap
- Levenshtein / rapidfuzz
- n-gram similarity

### Thuật toán cơ bản
1. Normalize text của report excerpt
2. Normalize tất cả paragraph trong DOCX
3. Tính similarity score
4. Lấy top-k paragraph
5. Nếu score vượt ngưỡng thì map
6. Nếu nhiều paragraph gần nhau thì gộp thành một unit nhiều paragraph
7. Nếu không chắc chắn thì đưa vào `manual_review`

### Ngưỡng khuyến nghị
- `> 0.85`: confident match
- `0.65 - 0.85`: probable match
- `< 0.65`: low confidence

---

## 12. Hướng dẫn implement orchestrator

Orchestrator phải là trung tâm điều phối mọi lời gọi LLM.

### 12.1 Thứ tự provider
Bắt buộc:
1. `Groq`
2. `OpenRouter`
3. `Gemini`

### 12.2 Điều kiện failover
Chuyển provider tiếp theo nếu gặp:
- timeout
- rate limit
- network error
- HTTP 5xx
- invalid JSON/schema
- output trống
- validation fail nghiêm trọng

### 12.3 Retry policy
- Mỗi provider retry tối đa `1` lần cho lỗi tạm thời
- Nếu vẫn lỗi thì chuyển provider kế tiếp
- Không retry vô hạn

### 12.4 Circuit breaker
Nếu 1 provider lỗi liên tục vượt ngưỡng:
- đánh dấu unhealthy
- tạm bỏ qua provider đó trong một khoảng thời gian
- route sang provider tiếp theo

### 12.5 Pseudocode

```python
PROVIDERS = ["groq", "openrouter", "gemini"]

def process_repair_unit(unit):
    for provider in PROVIDERS:
        for attempt in range(2):
            try:
                result = call_provider(provider, unit)
                validate_schema_or_raise(result)
                validate_quality_or_raise(unit, result)

                save_success(unit, provider, result)
                return result

            except TemporaryProviderError as e:
                save_attempt(unit, provider, "API_ERROR", str(e))
                if attempt == 1:
                    break

            except InvalidSchemaError as e:
                save_attempt(unit, provider, "INVALID_SCHEMA", str(e))
                break

            except QualityValidationError as e:
                save_attempt(unit, provider, "QUALITY_FAIL", str(e))
                break

    mark_manual_review(unit)
    return None
```

---

## 13. Provider interface

Tạo một interface thống nhất cho mọi provider.

```python
class BaseLLMProvider:
    name: str

    async def rewrite(self, payload: dict) -> dict:
        raise NotImplementedError
```

Mỗi provider phải trả về cùng một schema normalized:

```json
{
  "rewritten_text": "string",
  "summary_of_changes": "string",
  "citation_needed": true,
  "confidence": 0.92
}
```

---

## 14. Prompt contract cho LLM

Mọi provider phải nhận cùng một prompt contract.

### 14.1 System prompt

```text
Bạn là một trợ lý biên tập học thuật.
Nhiệm vụ của bạn là viết lại đoạn văn để giảm trùng lặp về câu chữ theo hướng hợp lệ, giữ nguyên ý nghĩa gốc, không bịa thêm thông tin, không thay đổi số liệu hay kết luận.
Nếu đoạn văn có dấu hiệu cần trích dẫn, hãy đặt citation_needed = true.
Không được thêm nguồn tham khảo giả.
Chỉ trả về JSON hợp lệ theo schema đã cho.
```

### 14.2 User prompt template

```text
Hãy xử lý repair unit sau.

[Ngữ cảnh tài liệu]
Tiêu đề mục: {section_title}
Đoạn trước: {previous_paragraph}
Đoạn hiện tại: {current_paragraph}
Đoạn sau: {next_paragraph}

[Ngữ cảnh báo cáo]
Loại rủi ro: {risk_type}
Mức tương đồng: {similarity_score}
Đoạn bị đánh dấu: {report_excerpt}
Nguồn liên quan: {source_reference}

[Ràng buộc]
- Giữ nguyên ý nghĩa
- Không thêm dữ kiện mới
- Không bịa citation
- Giữ văn phong học thuật
- Ngôn ngữ đầu ra: {language}

Trả về đúng JSON:
{
  "rewritten_text": "...",
  "summary_of_changes": "...",
  "citation_needed": true,
  "confidence": 0.0
}
```

---

## 15. Validation rules

### 15.1 Schema validation
Bắt buộc:
- là JSON hợp lệ
- có đủ 4 field:
  - `rewritten_text`
  - `summary_of_changes`
  - `citation_needed`
  - `confidence`

### 15.2 Meaning preservation
Phải kiểm tra đoạn mới có giữ nghĩa gần với đoạn cũ hay không.

Cách triển khai MVP:
- dùng embedding similarity
- hoặc gọi một validator model nhỏ hơn để chấm:
  - `SAME_MEANING`
  - `MINOR_DRIFT`
  - `MAJOR_DRIFT`

Nếu `MAJOR_DRIFT` thì reject.

### 15.3 Quality checks
Reject nếu:
- đoạn quá ngắn bất thường
- mất số liệu quan trọng
- đổi ý khẳng định sang phủ định
- bỏ mất chủ ngữ / điều kiện quan trọng
- ngôn ngữ lỗi nặng

### 15.4 Citation risk check
Nếu đoạn gốc chứa:
- định nghĩa
- lập luận đặc thù
- số liệu
- diễn giải bám rất sát nguồn

thì nên gắn `citation_needed = true`.

---

## 16. Hướng dẫn implement document builder

Document builder phải:
- thay đúng paragraph mục tiêu
- giữ style paragraph nếu có thể
- không phá numbering/headings
- không làm hỏng file DOCX

### Chiến lược
- dùng `paragraph_ref` để truy vết paragraph object
- chỉ thay `text payload` của paragraph mục tiêu
- nếu một repair unit trải trên nhiều paragraph, xử lý theo rule rõ ràng

### Output
- `revised.docx`
- `change_report.json`

---

## 17. Change report format

```json
{
  "job_id": "uuid",
  "summary": {
    "total_units": 12,
    "rewritten_units": 10,
    "manual_review_units": 2
  },
  "units": [
    {
      "unit_id": "uuid",
      "paragraph_ref": "p_0004",
      "provider_used": "groq",
      "original_text": "....",
      "rewritten_text": "....",
      "citation_needed": true,
      "confidence": 0.91,
      "status": "accepted"
    }
  ]
}
```

---

## 18. API contract

### 18.1 Tạo job
`POST /jobs`

#### Request
- multipart form:
  - `source_docx`
  - `report_pdf`

#### Response
```json
{
  "job_id": "uuid",
  "status": "UPLOADED"
}
```

### 18.2 Lấy trạng thái job
`GET /jobs/{job_id}`

#### Response
```json
{
  "job_id": "uuid",
  "status": "REWRITING",
  "progress": 65
}
```

### 18.3 Lấy danh sách repair units
`GET /jobs/{job_id}/units`

### 18.4 Tải file kết quả
`GET /jobs/{job_id}/download`

#### Response
- `revised.docx`
- `change_report.json`

---

## 19. Trạng thái hệ thống

```text
UPLOADED
PARSING
ALIGNING
REWRITING
VALIDATING
BUILDING
COMPLETED
FAILED
MANUAL_REVIEW
```

---

# 20. UX Requirements

## 20.1 Mục tiêu UX
UX của hệ thống phải giúp người dùng:
- hiểu ngay cần tải gì lên
- biết hệ thống đang làm gì
- biết model nào đã xử lý
- biết đoạn nào được sửa, đoạn nào cần tự xem lại
- tải kết quả dễ dàng
- không bị mất phương hướng khi job lâu hoặc lỗi

## 20.2 Persona chính
### Persona A: Người viết bài / sinh viên / researcher
- cần upload nhanh
- muốn xem kết quả dễ hiểu
- không muốn đọc log kỹ thuật phức tạp

### Persona B: Biên tập viên / reviewer nội bộ
- cần xem đoạn gốc và đoạn sửa song song
- cần biết đoạn nào cần citation
- cần xem lịch sử model nào xử lý

### Persona C: Admin / operator
- cần xem tỉ lệ lỗi provider
- cần biết job nào fail
- cần retry hoặc đưa manual review

## 20.3 User journey chuẩn
1. Người dùng vào trang upload
2. Chọn file DOCX
3. Chọn file PDF report
4. Nhấn “Bắt đầu xử lý”
5. Hệ thống chuyển sang trang job detail
6. Người dùng thấy tiến trình theo từng giai đoạn
7. Khi hoàn tất, người dùng vào trang review
8. Người dùng xem:
   - đoạn gốc
   - đoạn mới
   - model dùng
   - cờ citation
9. Người dùng tải file đầu ra

## 20.4 UX principles
- **Rõ ràng hơn thông minh**: ưu tiên giao diện dễ hiểu hơn là quá nhiều hiệu ứng
- **Minh bạch**: hiển thị rõ trạng thái, lỗi, fallback model
- **Review-first**: khuyến khích người dùng kiểm tra lại thay vì tin 100% vào máy
- **Không gây lo lắng**: trạng thái dài phải có progress và mô tả đang xử lý gì
- **Giảm ma sát**: ít bước, ít form, ít thiết lập rối
- **Nhất quán**: label, button, icon, màu sắc phải đồng nhất

## 20.5 UX content guidelines
Nên dùng text đơn giản:
- “Tải tài liệu DOCX”
- “Tải báo cáo PDF”
- “Đang phân tích tài liệu”
- “Đang đối chiếu đoạn cần chỉnh sửa”
- “Đang thử model khác do model trước gặp lỗi”
- “Cần bạn kiểm tra lại đoạn này”
- “Cần xem lại trích dẫn”

Không nên dùng text mơ hồ:
- “Processing”
- “Optimizing”
- “Smart repair”
- “Fixing plagiarism automatically”

---

# 21. UI Requirements

## 21.1 Màn hình bắt buộc

### A. Upload Page
#### Mục tiêu
Cho phép người dùng tải file và bắt đầu job.

#### Thành phần
- Header:
  - tên hệ thống
  - mô tả ngắn
- File upload card:
  - input `source.docx`
  - input `report.pdf`
- Validation message:
  - file sai định dạng
  - thiếu file
- Primary CTA:
  - `Bắt đầu xử lý`
- Secondary info box:
  - hệ thống sẽ tạo file DOCX đã chỉnh sửa
  - người dùng cần review lại trước khi sử dụng

#### Trạng thái UI
- idle
- dragging file
- file selected
- invalid file
- uploading
- upload failed

### B. Job Detail Page
#### Mục tiêu
Hiển thị tiến trình job theo thời gian thực.

#### Thành phần
- Job header:
  - mã job
  - trạng thái hiện tại
  - thời gian tạo
- Progress bar
- Stepper các giai đoạn:
  - Uploaded
  - Parsing
  - Aligning
  - Rewriting
  - Validating
  - Building
  - Completed
- Summary cards:
  - tổng số units
  - đã xử lý
  - manual review
  - provider fail count
- Activity log timeline:
  - parser started
  - alignment done
  - Groq failed, switched to OpenRouter
  - Gemini completed unit 08
- CTA:
  - `Xem kết quả`
  - `Tải file` khi hoàn tất

### C. Review Page
#### Mục tiêu
Cho người dùng kiểm tra chi tiết trước/sau.

#### Thành phần
- Filter bar:
  - tất cả
  - cần review
  - cần citation
  - theo provider
- Search box
- Unit review list
- Mỗi unit card hiển thị:
  - paragraph ref
  - risk type
  - provider used
  - confidence
  - citation_needed badge
  - original text
  - rewritten text
  - summary of changes
  - status badge
- Download section:
  - tải `revised.docx`
  - tải `change_report.json`

### D. Error / Manual Review Page
#### Mục tiêu
Hiển thị các unit không xử lý được hoặc xử lý chưa chắc chắn.

#### Thành phần
- danh sách unit lỗi
- lý do lỗi
- provider đã thử
- nút retry
- hướng dẫn kiểm tra thủ công

---

## 21.2 Design system tối thiểu

### Typography
- Heading lớn rõ ràng
- Body text dễ đọc
- Mã trạng thái dùng font vừa phải, không quá nhỏ

### Spacing
- 8px scale
- khoảng cách rộng ở card và panel
- tránh nhồi quá nhiều thông tin vào một màn hình

### Color roles
- Primary: hành động chính
- Neutral: nền, viền, text phụ
- Success: hoàn tất
- Warning: cần kiểm tra lại
- Error: thất bại
- Info: trạng thái đang chạy

### Component bắt buộc
- button
- input file
- card
- badge
- progress bar
- tabs
- accordion
- toast
- modal confirm
- skeleton loading
- empty state
- error state

---

## 21.3 Trạng thái UI cần thiết

### Upload
- chưa chọn file
- đã chọn 1 file
- đã chọn đủ 2 file
- đang upload
- upload lỗi

### Job
- đang chạy
- chuyển provider
- hoàn tất
- có unit cần manual review
- job thất bại toàn phần

### Review
- có dữ liệu
- không có unit nào cần sửa
- filter rỗng
- tải file lỗi

---

## 21.4 Empty states
Ví dụ nội dung:
- “Chưa có job nào. Hãy tải file DOCX và PDF để bắt đầu.”
- “Không có đoạn nào khớp với bộ lọc hiện tại.”
- “Không có unit nào cần review thủ công.”

---

## 21.5 Error states
Ví dụ nội dung:
- “Không đọc được file PDF. Vui lòng thử file khác hoặc dùng báo cáo xuất dạng text rõ hơn.”
- “Không thể map một số đoạn trong báo cáo với tài liệu DOCX.”
- “Model hiện tại gặp lỗi. Hệ thống đang chuyển sang model khác.”
- “Không thể tạo file kết quả. Vui lòng thử lại.”

---

## 21.6 Accessibility
Bắt buộc:
- contrast đủ cao
- button có trạng thái focus rõ
- label rõ cho input file
- không chỉ dùng màu để truyền đạt trạng thái
- icon phải có text hỗ trợ
- keyboard navigable
- screen-reader friendly cho progress và error

---

# 22. Wireframe định hướng

## 22.1 Upload Page

```text
+------------------------------------------------------+
| Logo / Tên hệ thống                                  |
| Hỗ trợ chỉnh sửa tài liệu từ báo cáo tương đồng      |
+------------------------------------------------------+

+---------------------------+  +----------------------+
| Tải tài liệu DOCX         |  | Tải báo cáo PDF      |
| [ Chọn file ]             |  | [ Chọn file ]        |
+---------------------------+  +----------------------+

[ ] Tôi hiểu rằng cần review lại kết quả trước khi dùng

[ Bắt đầu xử lý ]

Lưu ý:
- Hệ thống sẽ phân tích tài liệu và báo cáo
- Kết quả cần được người dùng kiểm tra lại
```

## 22.2 Job Detail Page

```text
+------------------------------------------------------+
| Job #A1284                 Status: REWRITING         |
+------------------------------------------------------+

[==========------] 68%

Uploaded -> Parsing -> Aligning -> Rewriting -> Validating -> Building

+------------------+ +------------------+ +------------------+
| Total units: 18  | | Done: 12         | | Review: 3        |
+------------------+ +------------------+ +------------------+

Timeline
- 10:02 DOCX parsed
- 10:03 PDF parsed
- 10:04 18 repair units created
- 10:05 Groq failed on unit 04
- 10:05 Switched to OpenRouter
- 10:06 Unit 04 completed
```

## 22.3 Review Page

```text
+------------------------------------------------------+
| Review kết quả                                       |
+------------------------------------------------------+

[ Search ] [All] [Need citation] [Manual review] [Provider]

--------------------------------------------------------
Unit p_0004   CLOSE_PARAPHRASE   Groq   Confidence 0.91
[Needs citation]

Original:
...

Rewritten:
...

Changes:
...
--------------------------------------------------------
```

---

# 23. API contract cho frontend

## 23.1 Upload job
`POST /jobs`

## 23.2 Get job summary
`GET /jobs/{job_id}`

## 23.3 Get job units
`GET /jobs/{job_id}/units`

## 23.4 Retry failed units
`POST /jobs/{job_id}/retry`

## 23.5 Download outputs
`GET /jobs/{job_id}/download`

## 23.6 Suggested frontend types

```ts
export type JobStatus =
  | "UPLOADED"
  | "PARSING"
  | "ALIGNING"
  | "REWRITING"
  | "VALIDATING"
  | "BUILDING"
  | "COMPLETED"
  | "FAILED"
  | "MANUAL_REVIEW";

export type RepairUnit = {
  id: string;
  paragraphRef: string;
  riskType: string;
  originalText: string;
  rewrittenText?: string;
  providerUsed?: "groq" | "openrouter" | "gemini";
  citationNeeded?: boolean;
  confidence?: number;
  status: string;
};
```

---

# 24. Frontend implementation notes

## 24.1 Page structure
- `/upload`
- `/jobs/[jobId]`
- `/review/[jobId]`

## 24.2 Recommended component tree

```text
UploadPage
  ├── PageHeader
  ├── FileUploadCard
  ├── FileDropzone
  ├── InfoNotice
  └── SubmitButton

JobDetailPage
  ├── JobHeader
  ├── ProgressSection
  ├── Stepper
  ├── SummaryCards
  ├── TimelineList
  └── ActionBar

ReviewPage
  ├── ReviewHeader
  ├── FilterToolbar
  ├── SearchInput
  ├── UnitList
  │    └── UnitCard
  └── DownloadPanel
```

## 24.3 State management
Có thể dùng:
- React Query / TanStack Query cho fetch & polling
- Zustand hoặc Context nhẹ cho state UI cục bộ

## 24.4 Polling strategy
Trang job detail nên polling mỗi 2–5 giây cho đến khi:
- `COMPLETED`
- `FAILED`
- `MANUAL_REVIEW`

---

# 25. Yêu cầu phi chức năng

## Hiệu năng
- xử lý theo từng `repair unit`
- có queue để không block request chính
- không gửi cả tài liệu lớn vào model cùng lúc

## Bảo mật
- lưu file an toàn
- kiểm soát quyền truy cập file
- không log raw tài liệu đầy đủ trong production nếu không cần
- ẩn API keys bằng env vars / secret manager

## Tin cậy
- có retry
- có fallback
- có timeout rõ ràng
- có circuit breaker

## Khả năng mở rộng
- provider phải cắm thêm dễ dàng
- validator có thể thay đổi độc lập
- parser và builder tách biệt

---

# 26. Environment variables

```env
APP_ENV=development
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
STORAGE_PATH=/data/files

GROQ_API_KEY=...
OPENROUTER_API_KEY=...
GEMINI_API_KEY=...

LLM_TIMEOUT_SECONDS=30
MAX_PROVIDER_RETRIES=1
LOG_LEVEL=INFO
```

---

# 27. Checklist implement theo giai đoạn

## Giai đoạn 1
- tạo FastAPI app
- upload file
- tạo job
- lưu metadata DB

## Giai đoạn 2
- DOCX parser
- PDF parser
- normalize text

## Giai đoạn 3
- alignment engine
- tạo repair units
- lưu DB

## Giai đoạn 4
- provider abstraction
- Groq provider
- OpenRouter provider
- Gemini provider
- orchestrator failover

## Giai đoạn 5
- schema validator
- meaning validator
- quality validator

## Giai đoạn 6
- document builder
- export DOCX
- export change report

## Giai đoạn 7
- UI upload page
- UI job detail page
- UI review page
- unit diff viewer
- download output

## Giai đoạn 8
- accessibility pass
- error state polish
- logging & monitoring

---

# 28. Test cases bắt buộc

## Parser tests
- DOCX nhiều paragraph
- DOCX có heading
- PDF text-based
- PDF scan-based fallback

## Alignment tests
- match đúng paragraph
- match mơ hồ
- nhiều paragraph gần nhau

## Provider tests
- Groq thành công
- Groq timeout -> OpenRouter thành công
- Groq + OpenRouter lỗi -> Gemini thành công
- cả 3 lỗi -> manual review

## Validation tests
- invalid JSON
- empty rewritten text
- meaning drift
- citation flag missing

## Builder tests
- ghi lại đúng paragraph
- không làm hỏng DOCX
- output mở được bằng Word

## Frontend tests
- upload validation
- progress polling
- filter review units
- manual review state
- download button state

---

# 29. Acceptance criteria

Hệ thống được coi là đạt khi:

1. Upload được `DOCX` và `PDF`
2. Parse được tài liệu và report
3. Tạo được `repair units`
4. Gọi LLM theo đúng thứ tự `Groq -> OpenRouter -> Gemini`
5. Tự động failover khi provider lỗi
6. Validate được output
7. Xuất được `revised.docx`
8. Xuất được `change_report.json`
9. Có log chi tiết cho từng provider attempt
10. Không làm hỏng cấu trúc DOCX cơ bản
11. Có UI hoàn chỉnh cho upload, theo dõi job, review và download
12. UX rõ ràng, có trạng thái lỗi, loading, empty state và manual review

---

# 30. Hướng dẫn cho AI coding agent

AI coding agent phải làm việc theo thứ tự sau:

1. Tạo skeleton project FastAPI + Next.js
2. Định nghĩa models, schemas, config
3. Implement upload + create job
4. Implement parser DOCX
5. Implement parser PDF
6. Implement alignment engine
7. Implement provider abstraction
8. Implement Groq provider
9. Implement OpenRouter provider
10. Implement Gemini provider
11. Implement orchestrator failover
12. Implement validation layer
13. Implement document builder
14. Implement frontend upload page
15. Implement frontend job detail page
16. Implement frontend review page
17. Implement retry flow cho manual review
18. Implement download endpoint
19. Viết unit tests
20. Viết README chạy local
21. Không bỏ qua error handling
22. Không hardcode API keys
23. Không gộp tất cả logic vào một file
24. Ưu tiên code rõ ràng, dễ test, dễ mở rộng

---

# 31. Định nghĩa done

Một task chỉ được coi là hoàn thành nếu:
- có code
- có test hoặc ít nhất có test scaffold
- có logging
- có error handling
- có docstring hoặc mô tả ngắn
- có UI state tương ứng nếu task tác động tới frontend
- không phá vỡ kiến trúc chung

---

# 32. Ghi chú cuối cùng

Ưu tiên độ ổn định và khả năng kiểm soát hơn là “rewrite càng mạnh càng tốt”.

Các tiêu chí quan trọng nhất:
1. map đúng đoạn cần chỉnh sửa
2. giữ nguyên nghĩa
3. fallback model chính xác
4. validate chặt
5. xuất DOCX an toàn
6. giao diện rõ ràng, có thể review
7. UX giảm nhầm lẫn và tăng tính kiểm soát cho người dùng
