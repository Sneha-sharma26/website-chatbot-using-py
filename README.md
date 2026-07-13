# Simple Website Chatbot — Step-by-Step Guide

## Project structure
```
chatbot_project/
├── scraper.py          # Step 1: downloads & saves website text
├── chatbot.py           # Step 2: keyword-matching chatbot logic
├── app.py                # Step 3: Flask web app
├── templates/
│   └── index.html         # Web UI
├── requirements.txt
└── website_content.txt   # (created automatically after you run scraper.py)
```
**Live Demo:**  
https://your-app-name.onrender.com

## Step 1 — Set up your environment

1. Make sure Python 3.9+ is installed: `python --version`
2. Create a project folder and put all these files inside it (keep `templates/index.html` inside a `templates` folder).
3. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```

## Step 2 — Check you're allowed to scrape

Before scraping any real site, open `https://phoenixdigitaltech.net/robots.txt` in your browser.
- If it doesn't disallow scraping the pages you need, you're fine for a small educational project.
- Always scrape politely: don't hit the server repeatedly, and only scrape public pages (not login-protected areas).

## Step 3 — Run the scraper

```
python scraper.py
```

What happens:
- It downloads the HTML of the homepage
- Strips out `<script>`, `<style>`, and similar non-content tags
- Extracts the visible text
- Saves everything into `website_content.txt`

Open `website_content.txt` afterward and skim it — this is literally the chatbot's entire "knowledge."

**Important limitation:** if the website is built with JavaScript (React/Vue/Next.js, etc.) and loads its main content dynamically, `requests` + `BeautifulSoup` will only see the empty HTML shell, not the real text. If `website_content.txt` looks empty or tiny, that's likely why. In that case:
- Try scraping specific sub-pages (e.g. `/services`, `/about`, `/cloud-solutions`) if they exist as separate URLs — some content may be server-rendered even if the homepage isn't.
- Or use a browser-automation tool like `selenium` or `playwright` instead of `requests`, which can execute JavaScript before extracting text. That's an extension you can add later — not required for the base assignment.

## Step 4 — Run the Flask app

```
python app.py
```

Then open your browser to:
```
http://127.0.0.1:5000
```

Type a question in the box and click send. The Flask route in `app.py`:
1. Reads the question from the form (`request.form.get("question")`)
2. Passes it to `bot.answer(question)`
3. Sends the answer back to `index.html` to display

## Step 6 — Test with the example questions

- What services does the company provide?
- Does the company provide cloud solutions?
- What is AI/ML service?
- What security solutions are available?

If an answer looks wrong or irrelevant, it usually means:
- The relevant text wasn't captured well by the scraper (check `website_content.txt`), or
- The chunk size in `split_into_chunks()` is too big/small — try adjusting the `120` character threshold in `chatbot.py`.


## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError: website_content.txt` | You ran `app.py` before `scraper.py` | Run `python scraper.py` first |
| Empty/tiny `website_content.txt` | Site uses JavaScript rendering | See Step 3 note about Selenium/Playwright |
| `ModuleNotFoundError: No module named 'bs4'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `TemplateNotFound: index.html` | `templates` folder missing or misnamed | Must be named exactly `templates`, in same folder as `app.py` |