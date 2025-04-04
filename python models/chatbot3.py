import pandas as pd
import spacy
import re

# Load spaCy English model for NLP
nlp = spacy.load("en_core_web_sm")

# Load the CSV data (college details)
college_df = pd.read_csv('ChatBot-Dataset.csv')

# Import the ML model function.
# We assume ML_Model.py has a function get_college_recommendations(data, category, user_percentile, current_year)
# that returns a list of dictionaries with the predictions.
import ML_Model

def extract_college_name(text):
    """
    Use spaCy to extract potential organization names (colleges)
    from the user query.
    """
    doc = nlp(text)
    # We look for entities with label ORG
    colleges = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    # Alternatively, look for known college names from our CSV
    known_colleges = college_df['College Name'].tolist() + college_df['College Name(shortform)'].tolist()
    for word in text.split():
        if word.upper() in [k.upper() for k in known_colleges]:
            colleges.append(word)
    return list(set(colleges))

def answer_csv_query(query):
    """
    Answers queries that can be satisfied by looking up the CSV data.
    We try to detect keywords for fields such as Address, Principal, Fee, Clubs, etc.
    """
    query_lower = query.lower()
    response = ""

    # Determine which field the user is asking about.
    if "address" in query_lower:
        field = "Address"
    elif "principal" in query_lower:
        field = "Principal Name"
    elif "phone" in query_lower:
        field = "Phone Number"
    elif "fee" in query_lower:
        # Here, we try to detect if the user wants a specific fee category.
        if "open" in query_lower:
            field = "Fee (Open)"
        elif "obc" in query_lower or "ews" in query_lower or "ebc" in query_lower:
            field = "Fee (OBC/EWS/EBC)"
        elif "sc" in query_lower or "st" in query_lower:
            field = "Fee (SC/ST)"
        elif "vj" in query_lower or "nt" in query_lower or "sbc" in query_lower or "tfws" in query_lower:
            field = "Fee (VJ/NT/SBC/TFWS)"
        else:
            field = "Fee (Open)"
    elif "club" in query_lower:
        field = "Clubs"
    elif "cultural" in query_lower:
        field = "Cultural Activities"
    elif "intake" in query_lower:
        # Check for specific branches
        if "computer" in query_lower:
            field = "Computer Engineering Intake"
        elif "civil" in query_lower:
            field = "Civil Engineering Intake"
        elif "chemical" in query_lower:
            field = "Chemical Engineering Intake"
        elif "information" in query_lower:
            field = "Information Technology Intake"
        elif "e & tc" in query_lower or "etc" in query_lower:
            field = "E & TC Engineering Intake"
        elif "mechanical" in query_lower:
            field = "Mechanical Engineering Intake"
        elif "electrical" in query_lower:
            field = "Electrical Engineering Intake"
        elif "biotechnology" in query_lower:
            field = "Biotechnology Intake"
        else:
            field = None
    else:
        field = None

    # Extract the college name from the query.
    colleges_found = extract_college_name(query)
    if not colleges_found:
        return "I'm sorry, I couldn't determine which college you are asking about. Could you please specify the college name?"
    
    responses = []
    for college in colleges_found:
        # Filter the data where the college name matches (we search in both 'College Name' and 'College Name(shortform)')
        college_data = college_df[(college_df['College Name'].str.contains(college, case=False, na=False)) |
                                  (college_df['College Name(shortform)'].str.contains(college, case=False, na=False))]
        if college_data.empty:
            responses.append(f"I couldn't find details for {college}.")
        else:
            if field and field in college_data.columns:
                val = college_data.iloc[0][field]
                responses.append(f"The {field} of {college} is {val}.")
            else:
                # If no specific field is detected, return a summary of the college info.
                summary = college_data.iloc[0].to_dict()
                summary_str = ", ".join(f"{k}: {v}" for k, v in summary.items())
                responses.append(f"Here are the details for {college}: {summary_str}")
    
    response = "\n".join(responses)
    return response

def handle_ml_query(query):
    """
    Process queries that mention percentile/chances, and try to extract the user's percentile and category.
    If not provided, ask the user for missing info.
    """
    # Use regex to search for a number (percentile) in the query.
    percentile_search = re.search(r'(\d{1,3}(?:\.\d+)?)', query)
    category_search = re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS)\b', query, re.IGNORECASE)
    
    if not percentile_search:
        return "To predict which colleges you might be eligible for, please provide your percentile."
    if not category_search:
        return "To predict which colleges you might be eligible for, please provide your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS)."
    
    user_percentile = float(percentile_search.group(1))
    user_category = category_search.group(1).upper()
    
    # For the purpose of prediction, we set the current year (you can change this if needed)
    current_year = 2025
    
    # Call the ML model prediction function from ML_Model.py
    predictions = ML_Model.get_college_recommendations(college_df, user_category, user_percentile, current_year)
    
    if not predictions:
        return f"Based on your percentile of {user_percentile} and category {user_category}, no matching colleges were found."
    
    # Build a natural language response from the predictions.
    response_lines = [f"Based on your percentile of {user_percentile} and category {user_category}, you might have a good chance of getting into the following colleges:"]
    for pred in predictions:
        college = pred.get('College', 'Unknown College')
        branch = pred.get('Branch', 'Unknown Branch')
        cutoff = pred.get('Predicted_Cutoff', 'N/A')
        response_lines.append(f"- {college} ({branch}) with an expected cutoff of {cutoff}.")
    
    return "\n".join(response_lines)

def process_user_query(query):
    """
    Determines if the query is about general college information (CSV query) or
    admission chances (ML model query) based on keywords.
    """
    query_lower = query.lower()
    # If the query contains words like "percentile", "chance", "get into", assume ML query.
    if any(word in query_lower for word in ["percentile", "chance", "get into", "admission"]):
        # If both percentile and category are found, process as ML model query.
        if re.search(r'\d', query_lower) and re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS)\b', query, re.IGNORECASE):
            return handle_ml_query(query)
        else:
            # Ask for missing details.
            return "Could you please provide both your percentile and your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS) so that I can predict which colleges you might be eligible for?"
    else:
        return answer_csv_query(query)

def chatbot():
    print("Welcome to the Engineering Colleges Chatbot!")
    print("You can ask me about college details (e.g., address, fee, clubs) or about your chances of admission based on your percentile.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Chatbot: Thank you for using the chatbot. Goodbye!")
            break
        
        response = process_user_query(user_query)
        print("Chatbot:", response)
        
if __name__ == "__main__":
    chatbot()
