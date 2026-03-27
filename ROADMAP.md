# Binance Future Advisor — Development Roadmap

H lộ trình phát triển ứng dụng cố vấn giao dịch Binance Futures tích hợp AI (Groq Llama 3.3).

---

## 🎯 Giai đoạn hiện tại: Nâng cấp Phân tích & Giao dịch (Trading Logic)
*Trọng tâm: Tối ưu hóa các quyết định từ AI và đa dạng hóa chiến lược.*

- [ ] **Chiến lược Hội tụ đa khung thời gian (Multi-TF Convergence)**:
  - Nâng cấp `SYSTEM_PROMPT` để AI ưu tiên các tín hiệu đồng thuận từ 15m, 1h và 4h.
  - Thêm logic kiểm tra xu hướng dài hạn (1d) trước khi cho phép vào lệnh ngắn hạn.
- [ ] **Chế độ giao dịch tùy chỉnh (Trading Styles)**:
  - Thêm lựa chọn "Scalping", "Swing Trading", hoặc "Conservative" trên UI.
  - Gửi cấu hình này vào Prompt để AI điều chỉnh mức TP/SL và đòn bẩy tương ứng.
- [ ] **Bộ lọc nhiễu tín hiệu (Signal Noise Filter)**:
  - Thêm các chỉ báo phụ như Volume Spread Analysis (VSA) hoặc Market Sentiment Ratio để AI loại bỏ các tín hiệu yếu.
- [ ] **Tính toán R:R (Risk/Reward Ratio) nâng cao**:
  - AI phải giải thích lý do chọn mức TP/SL dựa trên các vùng hỗ trợ/kháng cự (EMA200, Swings).

---

## 🎨 Giai đoạn 2: Nâng cấp UI & Trải nghiệm người dùng (UX)
*Trọng tâm: Trực quan hóa dữ liệu và biểu đồ.*

- [ ] **Tích hợp biểu đồ nến (TradingView Integration)**:
  - Nhúng biểu đồ nến thời gian thực bằng `Lightweight Charts`.
  - Hiển thị các điểm Entry, SL, TP của AI ngay trên biểu đồ.
- [ ] **Dashboard Tổng quan thị trường**:
  - Widgets hiển thị BTC Dominance, Fear & Greed Index.
  - Bảng "Top 10 Crypto Movers" (tăng/giảm mạnh nhất trong 24h).

---

## 🤖 Giai đoạn 3: Tự động hóa & Thông báo (Automation)
*Trọng tâm: Kết nối và đưa tín hiệu đến người dùng nhanh nhất.*

- [ ] **Hệ thống liên lạc (Alerts System)**:
  - Tích hợp Telegram Bot để gửi tín hiệu ngay khi AI phát hiện kèo "High Conviction".
  - Thông báo đẩy (Push Notifications) trên trình duyệt.
- [ ] **Lưu trữ lịch sử (Trade Journal & Database)**:
  - Sử dụng SQLite để lưu lại mọi tín hiệu AI đã phát ra.
  - Tính toán tỷ lệ thắng (Win Rate) tự động.

---

## ⚡ Giai đoạn 4: Tối ưu hóa & Robot Giao dịch (Pro Features)
*Trọng tâm: Giao dịch chuyên nghiệp và cập nhật thời gian thực.*

- [ ] **WebSockets Integration**:
  - Cập nhật giá và chỉ báo theo thời gian thực (Real-time update) thay vì gọi API liên tục.
- [ ] **Copy Trade / One-Click Trading**:
  - Kết nối API Key Binance (quyền Trade) để người dùng thực hiện lệnh ngay trên app.
- [ ] **Backtesting Engine**:
  - Cho phép người dùng chạy thử chiến lược AI trên dữ liệu quá khứ.
