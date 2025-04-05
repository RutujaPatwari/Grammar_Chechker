from flask import Flask, render_template, request
import language_tool_python
import nltk
import re

# Expanded grammar rules with suggestions
grammar_rules = {
    "parts_of_speech": {
        r"\b(?:is|are|was|were)\s+[A-Z]?[a-z]+ly\b": "Adverb used incorrectly after a verb.",
        r"\b[A-Z]?[a-z]+ness\b": "Consider if a noun form is needed here.",
    },
    "common_mistakes": {
        r"\btheir\s+going\b": "Did you mean 'they're going'?",
        r"\byour\s+welcome\b": "Did you mean 'you're welcome'?",
        r"\bcould\s+of\b": "Did you mean 'could have'?",
        r"\bdoesn['’]t\s+\w+s\b": "Incorrect verb form after 'doesn't'.",
        r"\bfastly\b": "'Fastly' is not a standard word. Use 'quickly'.",
        r"\ba\s+umbrella\b": "Did you mean 'an umbrella'?",
        r"\bwhether\b.*\bweather\b": "Check usage: 'weather' (climate) vs. 'whether' (condition).",
        r"\bi\s+am\s+go\b": "Incorrect verb form: use 'going'.",
        r"\bforecast\s+say\b": "Incorrect verb agreement. Use 'says'.",
        r"\bseen\s+the\s+movie\b": "Did you mean 'have you seen the movie'?",
        r"\bwas\s+like\b": "Consider using 'were like' when plural.",
        r"\bdisappear\s+without\s+no\b": "Double negative. Consider removing 'no'.",
        r"\bsay\s+she\s+wanna\b": "Did you mean 'said she wants to'?",
        r"\byour\s+gonna\b": "Did you mean 'you're going to'?",
    },
    "syntax_rules": {
        r"\b(and|but)\s+[A-Z][a-z]*\b": "Possible run-on sentence. Consider punctuation.",
        r"\bme\s+and\s+\w+\b": "Use 'X and I' instead of 'me and X'.",
    },
    "mechanics": {
        r"\bI\s+am\s+go\b": "Incorrect verb form: use 'going'.",
        r"\b[A-Z]{2,}\b": "Avoid unnecessary uppercase unless it's an abbreviation.",
    },
    "punctuation": {
        r"\s,": "Avoid space before commas.",
        r"\b\w+\b(?<!\.)$": "Sentence should end with a period.",
        r"\b\w+\b\s+[.!?]{2,}": "Avoid repeated punctuation.",
        r"\b(popcorns|soda's)\b": "Use 'popcorn' and 'sodas' instead.",
    }
}

# NLTK setup
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
tool = language_tool_python.LanguageTool('en-US')

# Highlights the mistakes visually
def highlight_errors(text):
    matches = tool.check(text)
    highlighted_text = text

    for match in reversed(matches):
        start, end = match.offset, match.offset + match.errorLength
        highlighted_text = (
            highlighted_text[:start] + f"<span class='error'>{text[start:end]}</span>" + highlighted_text[end:]
        )

    return highlighted_text

# Minor NLTK-based tweaks
def analyze_text_with_nltk(text):
    words = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(words)

    corrected_text = text
    for i in range(len(tagged) - 1):
        if tagged[i][0].lower() in ["was", "were"] and tagged[i+1][1] == "VB":
            corrected_text = corrected_text.replace(
                f"{tagged[i][0]} {tagged[i+1][0]}",
                f"{tagged[i][0]} {tagged[i+1][0]}ing"
            )

    return corrected_text

# Apply custom regex rules
def apply_grammar_rules(text):
    feedback = []
    for category, rules in grammar_rules.items():
        for pattern, message in rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                feedback.append(f"{category.capitalize()}: {message}")
    return feedback

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]

        nltk_analysis = analyze_text_with_nltk(text)
        corrected_text = tool.correct(nltk_analysis)
        highlighted_text = highlight_errors(nltk_analysis)
        grammar_feedback = apply_grammar_rules(text)

        return render_template(
            "index.html",
            original=highlighted_text,
            corrected=corrected_text,
            input_text=text,
            nltk_analysis=nltk_analysis,
            grammar_feedback=grammar_feedback
        )

    return render_template(
        "index.html",
        original="",
        corrected="",
        input_text="",
        nltk_analysis="",
        grammar_feedback=[]
    )

if __name__ == "__main__":
    app.run(debug=True)
