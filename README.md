# Binance Future Advisor — AI Trading Assistant (Groq)

A professional trading advisor for Binance Futures, powered by **Groq Llama-3.3-70b**. It analyzes real-time market data, computes technical indicators (RSI, MACD, EMA), and provides actionable trading signals.

## Project Structure
- `backend/`: FastAPI server and AI logic.
- `frontend/`: Premium Dark Mode interface.
- `.venv/`: Python virtual environment.

## Installation
1. Ensure you have Python 3.10+ installed.
2. The dependencies are already installed in the `.venv`. To update:
   ```powershell
   cd backend
   ..\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

## How to Run (Recommended)
You MUST run the project using the Python interpreter from the virtual environment to ensure all libraries (like `groq`) are recognized.

### Start the Server
From the root directory of the project:
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```
*Note: If you are already inside the `backend/` folder, use `..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000`.*

### Access the App
Open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

## Hosting & Deployment (Docker)

To deploy the application professionally, use the provided Docker configuration. This ensures the environment is identical regardless of where you host it.

### 1. Build the Docker Image
From the root directory:
```bash
docker build -t binance-advisor .
```

### 2. Run the Container
```bash
docker run -p 8000:8000 -e GROQ_API_KEY="your_groq_api_key_here" binance-advisor
```

### 3. Deploy to Cloud
- **Railway/Render**: Simply connect your GitHub repository; they will automatically detect the `Dockerfile` and deploy it.
- **VPS**: Install Docker and use the commands above.
- **Environment Variables**: Make sure to set `GROQ_API_KEY` in your hosting provider's dashboard.

## Technical Features
- **AI Engine**: Groq (Llama-3.3-70b-versatile).
- **Data Source**: Official Binance Futures Public API.
- **Indicators**: RSI(14), MACD(12,26,9), EMA(50,200).
- **Risk Management**: Leverage suggestions, SL/TP levels, and confidence scoring.

---

## 🤖 Automation & Alerts Setup (Phase 3)

Để hệ thống có thể tự động gửi kèo (Tín hiệu giao dịch) về điện thoại của bạn, hãy làm theo các bước sau:

### 1. Cách tạo Telegram Bot (Nhận tín hiệu qua App Telegram)
1. Mở ứng dụng Telegram, tìm kiếm tài khoản **`@BotFather`** (có dấu tích xanh dương).
2. Chat với BotFather câu lệnh: `/newbot`.
3. Nhập Tên cho Bot của bạn (ví dụ: `AlphaTrader AI`).
4. Nhập Username cho Bot, BẮT BUỘC phải kết thúc bằng chữ `bot` (ví dụ: `alphatrader_kiencntt_bot`).
5. Nếu thành công, BotFather sẽ gửi cho bạn một đoạn mã dài gọi là **Token** (ví dụ: `712345678:AABbCcDdEe_FfGg...`).
6. Nhập token trên vào file `backend/.env` tại dòng `TELEGRAM_BOT_TOKEN="mã_token"`.

### 2. Lấy Chat ID của bạn
1. Search tìm tài khoản bot **`@userinfobot`** trên Telegram và ấn **Start**.
2. Bot sẽ trả về cho bạn dòng `Id: 123456789`.
3. Copy đoạn số đó, dán vào file `backend/.env` tại dòng `TELEGRAM_CHAT_ID="123456789"`.
*Lưu ý: Mở Chat với Bot vừa tạo của bạn (ở bước 1) và bấm Start để Bot có quyền gửi tin nhắn cho bạn.*

### 3. Push Notifications (Thông báo Trình duyệt)
Để nhận thông báo trực tiếp trên máy tính Windows/Mac mà không cần bật Telegram:
1. Bạn phải luôn mở ít nhất 1 Tab của giao diện web `http://127.0.0.1:8000/`. Đừng đóng hẳn tab đi, bạn có thể thu nhỏ trình duyệt xuống thanh Taskbar (chạy ngầm).
2. Khi lầu đầu truy cập, Trình duyệt (Chrome/Edge/Brave) sẽ hiện bảng Popup hỏi xin quyền "Show Notifications". Bạn hãy **nhấn Allow (Cho phép)**.
3. Nếu lỡ tay bấm Block (Chặn), hãy ấn vào biểu tượng "Ổ khóa" ở thanh địa chỉ góc trên bên trái trình duyệt -> Chọn Site Settings -> Sửa quyền Notifications thành Allow.

### 4. Cách điều khiển Bot săn kèo tự động (Auto-Scanner)
Khi Bot đã được tạo và nhập Token thành công, bạn không cần phải luôn xem biểu đồ trên Website nữa. Server đã được trang bị cơ chế tự động hoá 2 chiều với Telegram. Bạn hãy mở chat với Bot của mình và ra lệnh:

- **`/start`** : Lời chào mừng và xác nhận Bot đã thức dậy.
- **`/add <Mã_Coin>`** (Ví dụ: `/add BTCUSDT`): Giao nhiệm vụ cho Cỗ máy quét ngầm đồng coin này. Cứ mỗi **1 tiếng đồng hồ**, Bot sẽ quét toàn bộ danh sách bạn đã Thêm. Nếu điểm tự tin **(Confidence) >= 75%** và chưa bị kẹt lệnh cũ nào, nó sẽ rung điện thoại cất tiếng "Ting Ting" gọi bạn.
- **`/remove <Mã_Coin>`** (Ví dụ: `/remove SOLUSDT`): Hủy theo dõi, xóa khỏi danh sách săn báo động.
- **`/list`** : Xem lại các đồng Coin bạn đang cắm chốt.
