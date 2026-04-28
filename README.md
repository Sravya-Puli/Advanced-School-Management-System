# EduSmart School Management System

EduSmart is a comprehensive school management system designed to streamline academic and administrative tasks. It features dedicated dashboards for Admins, Teachers, and Students, along with an integrated AI Assistant.

## 🚀 Features

- **Admin Dashboard**: Manage students, teachers, classes, fees, and school-wide analytics.
- **Teacher Dashboard**: Track student attendance, manage marks, and analyze class performance.
- **Student Dashboard**: View personal academic records, attendance history, and fee status.
- **AI Assistant**: A built-in AI chatbot that provides strategic insights for admins, performance analysis for teachers, and personalized study tips for students. (Powered by GPT4Free - No API Key required!)

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (DM Sans Font)
- **AI Integration**: g4f (GPT4Free)
- **Charts**: Chart.js

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd "RTP Project"
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   python create_db.py
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000/`.

## 🌐 Deployment

This project is ready for deployment on platforms like **Render**, **Railway**, or **Heroku**.

1. **Connect your GitHub repository** to the hosting platform.
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn app:app`
4. **Environment Variables**: The app will automatically detect the `PORT` variable provided by the host.

Note: Since this project uses SQLite, data will be reset on every deployment unless your host supports persistent disks (like Render's "Disk" feature).

## 🤖 AI Assistant

The AI Assistant uses the `g4f` library to provide free AI functionality without requiring any external API keys. It is integrated into all three dashboards:
- **Admin**: School-wide performance and financial analysis.
- **Teacher**: Student-specific performance analysis and improvement strategies.
- **Student**: Personalized study tips and exam predictions.

## 📄 License

This project is open-source and available under the MIT License.
