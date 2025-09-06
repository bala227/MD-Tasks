# Assignment 4B

This project scrapes data from specified sources using Python and processes it into CSV files.  
It provides a backend system to manage and store the scraped data efficiently.  
The frontend displays the processed data in a user-friendly interface for easy viewing.


## Backend Setup

1. **Create virtual environment** (if not already created):

```bash
cd backend
python -m venv venv
```
2. **Activate virtual environment**:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run backend script**:
```bash
uvicorn main:app --reload
```
5. **Frontend Setup**

Open the frontend folder in your code editor.
```bash
cd frontend
npm install
npm run dev
```