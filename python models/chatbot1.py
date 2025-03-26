import pandas as pd
import re
import nltk

from nltk.tokenize import word_tokenize

# Download required NLTK data (only runs once)
nltk.download("punkt")

# Load CSV data
data = pd.read_csv("python models/colleges.csv")

# Small talk responses
greetings = ["Hey there! 😊", "Hello! How can I assist you?", "Hi! Ask me about college admissions."]
fallback_responses = [
    "I'm not sure I understand. Could you rephrase? 🤔",
    "Hmm, that’s interesting! Could you clarify what you mean?",
    "I’m here to help with college admissions! Ask me about cutoffs or best colleges."
]

# Function to extract percentile from user input
def extract_number(text):
    """Extract a number (percentile) from text."""
    match = re.search(r"(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else None

# Function to get colleges based on percentile
def get_colleges_by_percentile(user_percentile, branch=None):
    """Suggest colleges for a given percentile and optional branch."""
    df = data.copy()
    if branch:
        df = df[df['Branch'].str.contains(branch, case=False, na=False)]
    df['Percentile'] = pd.to_numeric(df['Percentile'], errors='coerce')
    eligible = df[df['Percentile'] <= user_percentile].sort_values(by="Percentile", ascending=False)
    return eligible.head(5) if not eligible.empty else pd.DataFrame()

# Function to find the best college for a branch
def get_best_college_for_branch(branch):
    """Find the best college for a branch (highest cutoff)."""
    df = data[data['Branch'].str.contains(branch, case=False, na=False)]
    df['Percentile'] = pd.to_numeric(df['Percentile'], errors='coerce')
    return df.loc[df['Percentile'].idxmax()] if not df.empty else None

# Main chatbot function using NLTK
def process_query(query):
    """Process user query using NLTK for tokenization and understanding."""

    query = query.lower().strip()
    words = word_tokenize(query)  # Tokenize the user input

    # Handle greetings & small talk
    if any(word in words for word in ["hi", "hello", "hey"]):
        return random.choice(greetings)

    if "bye" in words or "exit" in words or "quit" in words:
        return "Goodbye! Have a great day ahead! 🎓😊"

    if "thank" in words:
        return "You're welcome! 😊 Let me know if you have more questions."

    # Extract percentile and check for college recommendations
    user_percentile = extract_number(query)
    branch_keywords = ["cs", "it", "ece", "mechanical", "civil", "eee"]
    branch = next((b for b in branch_keywords if b in words), None)

    if user_percentile:
        suggestions = get_colleges_by_percentile(user_percentile, branch)
        if suggestions.empty:
            return f"Sorry, no colleges found with a cutoff below {user_percentile}."
        response = f"Based on your percentile ({user_percentile})"
        if branch:
            response += f" for branch '{branch.upper()}', here are some suggestions:\n"
        else:
            response += ", here are some suggestions:\n"
        for _, row in suggestions.iterrows():
            response += f"- {row['College']} (Cutoff: {row['Percentile']})\n"
        return response

    # Best college for a specific branch
    if "best" in words and "college" in words and "for" in words:
        for i in range(len(words) - 1):
            if words[i] == "for":
                branch = words[i + 1]
                best = get_best_college_for_branch(branch)
                return (f"The best college for {branch.upper()} is {best['College']} (Cutoff: {best['Percentile']})."
                        if best is not None else f"Sorry, no data found for branch '{branch}'.")
    
    return random.choice(fallback_responses)

# Chatbot loop
def main():
    print("Welcome to the College Chatbot! 🎓 Type 'exit' to quit.")
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye! Have a great day! 🎉")
            break
        print("Chatbot:", process_query(query))

if __name__ == "__main__":
    main()
