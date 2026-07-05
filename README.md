# FileSure — Compliance & Tax Services

FileSure is a complete Flask-based web application designed to offer MSMEs, startups, and freelancers affordable tax and compliance filing services. It includes a smart compliance engine that calculates and visually plots upcoming deadlines on an interactive calendar.

## Features

- **Compliance Engine (`compliance.py`)**: Computes filing deadlines (GST, TDS, ROC, Income Tax) over a rolling 6-month window based on business type and registration rules.
- **Interactive Visual Calendar**: A dynamically rendered JavaScript grid showing safe, upcoming, urgent, and critical deadlines.
- **Service & Pricing Showcase**: Clean comparison tables and pricing cards contrasting FileSure with traditional CA firms.
- **Lead Capture & Database**: Fully functioning SQLAlchemy models capturing form submissions and calendar inquiries.
- **Modern Glassmorphism UI**: High-end aesthetic using deep navy themes, glass cards, micro-animations, and responsive layouts.

## Tech Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy
- **Database**: SQLite (Development) / easily upgradeable to PostgreSQL
- **Frontend**: HTML5, Jinja2, Vanilla CSS (Glassmorphism design), Vanilla JS

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FileSure.git
   cd FileSure
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the site**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```text
FileSure/
├── app.py                 # Flask server, routes, and DB models
├── compliance.py          # Deadline calculation engine for GST, ROC, TDS, etc.
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── main.css       # Core design system and styles
│   └── js/
│       ├── animations.js  # Scroll reveal and frontend micro-animations
│       └── calendar.js    # Logic for rendering the interactive visual calendar
└── templates/             # Jinja2 HTML templates
    ├── base.html
    ├── index.html
    ├── services.html
    ├── about.html
    ├── contact.html
    └── calendar_results.html
```

## Contributing
Contributions are welcome. Please open an issue or submit a pull request for any enhancements or bug fixes.

## Maintainers / Credits
**Kavya Kajavadra** — Tech Lead & Project Head  
Built with 💙 for MSMEs and Freelancers.

## License
This project is licensed under the MIT License.
