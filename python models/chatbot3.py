import pandas as pd
import spacy
import re

# Load spaCy English model for NLP
nlp = spacy.load("en_core_web_sm")

# Load the CSV data (college details)
college_df = pd.read_csv('ChatBot-Dataset.csv')
# We no longer need to load ml_df since ML_MODEL2.load_and_clean will handle it

# Import the ML model prediction functions from ML_Model2.
import ML_Model2

def extract_college_name(text):
    """
    Use spaCy to extract potential organization names (colleges)
    from the user query.
    """
    doc = nlp(text)
    colleges = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    # Also look for known college names from our CSV
    known_colleges = college_df['College Name'].tolist() + college_df['College Name(shortform)'].tolist()
    for word in text.split():
        if word.upper() in [k.upper() for k in known_colleges]:
            colleges.append(word)
    return list(set(colleges))

def list_all_colleges():
    """
    Returns a list of all college names in the dataset.
    """
    all_colleges = college_df['College Name'].unique().tolist()
    return "Here is the list of all colleges:\n" + "\n".join(all_colleges)

def answer_csv_query(query):
    """
    Answers queries that can be satisfied by looking up the CSV data.
    If query asks for specific grouped information (e.g. contact details),
    only those columns are returned.
    """
    query_lower = query.lower()

    # Check if user asked for list of all colleges.
    if "list" in query_lower and "college" in query_lower:
        return list_all_colleges()

    # Mapping keywords to groups of fields.
    group_mapping = {
        "contact": ['College Name', 'College Name(shortform)', 'Principal Name', 'Address', 'Phone Number'],
        "fee": None,  # will be handled separately to consider qualifiers
        "intake": ['Biotechnology Intake', 'Civil Engineering Intake', 'Chemical Engineering Intake',
                   'Computer Engineering Intake', 'Information Technology Intake', 'E & TC Engineering Intake',
                   'Mechanical Engineering Intake', 'Electrical Engineering Intake'],
        "admission": ['Admission Documents Required'],
        "club": ['Clubs'],
        "cultural": ['Cultural Activities']
    }

    requested_fields = []

    # Process grouped queries.
    for key, fields in group_mapping.items():
        if key in query_lower:
            # Special case for fee: check if a specific fee type was requested.
            if key == "fee":
                temp = []
                if "open" in query_lower:
                    temp.append("Fee (Open)")
                if "obc" in query_lower or "ews" in query_lower or "ebc" in query_lower:
                    temp.append("Fee (OBC/EWS/EBC)")
                if "sc" in query_lower or "st" in query_lower:
                    temp.append("Fee (SC/ST)")
                if "vj" in query_lower or "nt" in query_lower or "sbc" in query_lower or "tfws" in query_lower:
                    temp.append("Fee (VJ/NT/SBC/TFWS)")
                # if no qualifier given, return all fee related fields.
                if not temp:
                    temp = ["Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)"]
                requested_fields.extend(temp)
            else:
                requested_fields.extend(fields)

    # If no grouped field is detected, fall back to previous single-field conditions.
    single_field = None
    if not requested_fields:
        if "address" in query_lower:
            single_field = "Address"
        elif "principal" in query_lower:
            single_field = "Principal Name"
        elif "contact deta" in query_lower:
            single_field = "Phone Number"
        elif "fee" in query_lower:  # includes fee queries with qualifiers
            if "open" in query_lower:
                single_field = "Fee (Open)"
            elif "obc" in query_lower or "ews" in query_lower or "ebc" in query_lower:
                single_field = "Fee (OBC/EWS/EBC)"
            elif "sc" in query_lower or "st" in query_lower:
                single_field = "Fee (SC/ST)"
            elif "vj" in query_lower or "nt" in query_lower or "sbc" in query_lower or "tfws" in query_lower:
                single_field = "Fee (VJ/NT/SBC/TFWS)"
            else:
                single_field = "Fee (Open)"
        elif "club" in query_lower:
            single_field = "Clubs"
        elif "cultural" in query_lower:
            single_field = "Cultural Activities"
        elif "intake" in query_lower:
            # If a specific branch is mentioned, handle that.
            if "computer" in query_lower:
                single_field = "Computer Engineering Intake"
            elif "civil" in query_lower:
                single_field = "Civil Engineering Intake"
            elif "chemical" in query_lower:
                single_field = "Chemical Engineering Intake"
            elif "information" in query_lower:
                single_field = "Information Technology Intake"
            elif "e & tc" in query_lower or "etc" in query_lower:
                single_field = "E & TC Engineering Intake"
            elif "mechanical" in query_lower:
                single_field = "Mechanical Engineering Intake"
            elif "electrical" in query_lower:
                single_field = "Electrical Engineering Intake"
            elif "biotechnology" in query_lower:
                single_field = "Biotechnology Intake"

    # Extract the college name from the query.
    colleges_found = extract_college_name(query)
    if not colleges_found:
        return ("I'm sorry, I couldn't determine which college you are asking about.\n"
                "Could you please specify the college name?")

    responses = []
    for college in colleges_found:
        # Filter data by matching the college name in both columns.
        college_data = college_df[(college_df['College Name'].str.contains(college, case=False, na=False)) |
                                  (college_df['College Name(shortform)'].str.contains(college, case=False, na=False))]
        if college_data.empty:
            responses.append(f"I couldn't find details for {college}.\n")
        else:
            # If grouped fields were requested, show only those.
            if requested_fields:
                details = []
                for field in requested_fields:
                    if field in college_data.columns:
                        details.append(f"{field}: {college_data.iloc[0][field]}")
                details_str = "\n".join(details)
                responses.append(f"{college} details:\n{details_str}\n")
            elif single_field and single_field in college_data.columns:
                val = college_data.iloc[0][single_field]
                responses.append(f"The {single_field} of {college} is {val}.\n")
            else:
                # Otherwise, return a summary (all columns).
                summary = college_data.iloc[0].to_dict()
                summary_lines = [f"{k}: {v}" for k, v in summary.items()]
                summary_str = "\n".join(summary_lines)
                responses.append(f"Here are the details for {college}:\n{summary_str}\n")

    return "\n".join(responses)

def handle_ml_query(query):
    """
    Process queries involving admission chances.
    Extracts the user's percentile and category and predicts eligible colleges.
    """
    percentile_search = re.search(r'(\d{1,3}(?:\.\d+)?)', query)
    category_search = re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS|VJ|NT|SBC|TFWS)\b', query, re.IGNORECASE)
    
    if not percentile_search:
        return ("To predict which colleges you might be eligible for,\n"
                "please provide your percentile.")
    if not category_search:
        return ("To predict which colleges you might be eligible for,\n"
                "please provide your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS).")
    
    user_percentile = float(percentile_search.group(1))
    user_category = category_search.group(1).upper()
    
    current_year = 2025

    # Load and prepare the ML model pipeline using ML_MODEL2
    ml_df_clean = ML_Model2.load_and_clean('colleges.csv')
    ml_pipe = ML_Model2.build_pipeline()
    ml_pipe = ML_Model2.fit_full(ml_df_clean, ml_pipe)
    predictions = ML_Model2.get_recommendations(ml_df_clean, ml_pipe, user_category, user_percentile, current_year)
    
    if not predictions:
        return (f"Based on your percentile of {user_percentile} and category {user_category},\n"
                "no matching colleges were found.")
    
    response_lines = [f"Based on your percentile of {user_percentile} and category {user_category}, "
                      "you might have a good chance of getting into the following colleges:"]
    for pred in predictions:
        college = pred.get('College', 'Unknown College')
        branch = pred.get('Branch', 'Unknown Branch')
        cutoff = pred.get('Predicted_Cutoff', 'N/A')
        response_lines.append(f"- {college} ({branch}) with an expected cutoff of {cutoff}.")
    
    return "\n".join(response_lines)

def process_user_query(query):
    """
    Determines if the query is about general college information
    (CSV query) or admission chances (ML model query) based on keywords.
    """
    query_lower = query.lower()
    
    # Detect if the query is an admission prediction query.
    if any(word in query_lower for word in ["percentile", "chance", "get into", "admission"]):
        if re.search(r'\d', query_lower) and re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS)\b', query, re.IGNORECASE):
            return handle_ml_query(query)
        else:
            return ("Could you please provide both your percentile and your category\n"
                    "(e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS) so that I can\n"
                    "predict which colleges you might be eligible for?")
    else:
        return answer_csv_query(query)

def chatbot():
    print("Welcome to the Engineering Colleges Chatbot!")
    print("You can ask for college details (e.g., address, fees, clubs) or ask for a list of colleges.")
    print("You can also ask about your admission chances by providing your percentile and category.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Chatbot: Thank you for using the chatbot. Goodbye!")
            break
        
        response = process_user_query(user_query)
        print("Chatbot:\n" + response)
        
if __name__ == "__main__":
    chatbot()
