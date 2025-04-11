import re
import pandas as pd
import spacy
import ML_Model2

# Load spaCy model and CSV data.
nlp = spacy.load("en_core_web_sm")
college_df = pd.read_csv('ChatBot-Dataset.csv')

ATTRIBUTES = [
    "Principal Name", "Address", "Phone Number",
    "Biotechnology Intake", "Civil Engineering Intake", "Chemical Engineering Intake", "Computer Engineering Intake",
    "Information Technology Intake", "E & TC Engineering Intake", "Mechanical Engineering Intake", "Electrical Engineering Intake",
    "Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)",
    "Admission Documents Required", "Clubs", "Cultural Activities"
]

def get_attribute_from_query(query: str) -> str:
    """Returns the attribute found in the query if any."""
    query_lower = query.lower()
    for attribute in ATTRIBUTES:
        if attribute.lower() in query_lower:
            return attribute
    return None

def list_all_colleges() -> str:
    """Returns a list of all college names in the dataset."""
    all_colleges = college_df['College Name'].unique().tolist()
    return "Here is the list of all colleges:\n" + "\n".join(all_colleges)

def list_all_branches() -> str:
    """Returns a list of all branches (intake fields) based on the CSV columns."""
    branch_columns = [col for col in college_df.columns if "Intake" in col]
    branches = [col.replace(" Intake", "") for col in branch_columns]
    return "Here is the list of all branches:\n" + "\n".join(branches)

def list_all_categories() -> str:
    """Returns a list of all fee categories."""
    categories = ["OPEN", "OBC/EWS/EBC", "SC/ST", "VJ/NT/SBC/TFWS"]
    return "Here are the available categories:\n" + "\n".join(categories)

def extract_college_name(text: str) -> list:
    """Extracts possible college names from input text using spaCy and known college names."""
    doc = nlp(text)
    colleges = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    known_colleges = college_df['College Name'].tolist() + college_df['College Name(shortform)'].tolist()
    
    # Check word by word for known college names
    text_words = text.split()
    for word in text_words:
        if word.upper() in (k.upper() for k in known_colleges):
            colleges.append(word)
    return list(set(colleges))

def answer_csv_query(query: str) -> str:
    query_lower = query.lower()
    
    # Handle list queries first.
    if "list" in query_lower:
        if "college" in query_lower:
            return list_all_colleges()
        if "branch" in query_lower:
            return list_all_branches()
        if "category" in query_lower:
            return list_all_categories()

    single_field = get_attribute_from_query(query)
    requested_fields = []
    
    # Mapping keywords to groups of fields.
    group_mapping = {
        "contact": ['Phone Number'],
        "fee": ["Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)"],
        "intake": ['Biotechnology Intake', 'Civil Engineering Intake', 'Chemical Engineering Intake',
                   'Computer Engineering Intake', 'Information Technology Intake', 'E & TC Engineering Intake',
                   'Mechanical Engineering Intake', 'Electrical Engineering Intake'],
        "admission": ['Admission Documents Required'],
        "club": ['Clubs'],
        "cultural": ['Cultural Activities']
    }

    for key, fields in group_mapping.items():
        if key in query_lower:
            if key == "fee":
                temp = []
                if "open" in query_lower:
                    temp.append("Fee (Open)")
                if any(x in query_lower for x in ["obc", "ews", "ebc"]):
                    temp.append("Fee (OBC/EWS/EBC)")
                if any(x in query_lower for x in ["sc", "st"]):
                    temp.append("Fee (SC/ST)")
                if any(x in query_lower for x in ["vj", "nt", "sbc", "tfws"]):
                    temp.append("Fee (VJ/NT/SBC/TFWS)")
                requested_fields.extend(temp if temp else fields)
            else:
                requested_fields.extend(fields)
    
    # Fallback detection if no field specified from group mapping.
    if not requested_fields and not single_field:
        if "address" in query_lower:
            single_field = "Address"
        elif "principal" in query_lower:
            single_field = "Principal Name"
        elif "contact deta" in query_lower:
            single_field = "Phone Number"
        elif "fee" in query_lower:
            if "open" in query_lower:
                single_field = "Fee (Open)"
            elif any(x in query_lower for x in ["obc", "ews", "ebc"]):
                single_field = "Fee (OBC/EWS/EBC)"
            elif any(x in query_lower for x in ["sc", "st"]):
                single_field = "Fee (SC/ST)"
            elif any(x in query_lower for x in ["vj", "nt", "sbc", "tfws"]):
                single_field = "Fee (VJ/NT/SBC/TFWS)"
            else:
                single_field = "Fee (Open)"
        elif "intake" in query_lower:
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

    # Determine the college(s) mentioned.
    colleges_found = extract_college_name(query)
    if not colleges_found:
        return ("I'm sorry, I couldn't determine which college you are asking about.\n"
                "Could you please specify the college name?")

    responses = []
    for college in colleges_found:
        college_data = college_df[
            (college_df['College Name'].str.contains(college, case=False, na=False)) |
            (college_df['College Name(shortform)'].str.contains(college, case=False, na=False))
        ]
        if college_data.empty:
            responses.append(f"I couldn't find details for {college}.\n")
        else:
            if requested_fields:
                details = []
                for field in requested_fields:
                    if field in college_data.columns:
                        details.append(f"{field}: {college_data.iloc[0][field]}")
                responses.append(f"{college} details:\n" + "\n".join(details) + "\n")
            elif single_field and single_field in college_data.columns:
                value = college_data.iloc[0][single_field]
                responses.append(f"The {single_field} of {college} is {value}.\n")
            else:
                summary = college_data.iloc[0].to_dict()
                summary_lines = [f"{k}: {v}" for k, v in summary.items()]
                responses.append(f"Here are the details for {college}:\n" + "\n".join(summary_lines) + "\n")

    return "\n".join(responses)

def handle_ml_query(query: str) -> str:
    """Processes queries related to admission chances using an ML model."""
    percentile_match = re.search(r'(\d{1,3}(?:\.\d+)?)', query)
    category_match = re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS|VJ|NT|SBC|TFWS)\b', query, re.IGNORECASE)
    
    if not percentile_match:
        return ("To predict eligible colleges, please provide your percentile.")
    if not category_match:
        return ("To predict eligible colleges, please provide your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS).")
    
    user_percentile = float(percentile_match.group(1))
    user_category = category_match.group(1).upper()
    current_year = 2025

    ml_df_clean = ML_Model2.load_and_clean('colleges.csv')
    ml_pipe = ML_Model2.build_pipeline()
    ml_pipe = ML_Model2.fit_full(ml_df_clean, ml_pipe)
    predictions = ML_Model2.get_recommendations(ml_df_clean, ml_pipe, user_category, user_percentile, current_year)
    
    if not predictions:
        return (f"Based on your percentile of {user_percentile} and category {user_category}, no matching colleges were found.")
    
    # Check if the query already contains a branch filter keyword.
    branch_filter = None
    query_lower = query.lower()
    branch_keywords = {
        "computer": "CS",
        "information": "IT",
        "mechanical": "MECH",
        "mech": "MECH",
        "electrical": "E & TC",
        "civil": "CIVIL",
        "chemical": "CHEM",
        "biotech": "BIO-TECH",
        "bio": "BIO-TECH",
        "biotechnology": "BIO-TECH",
        "electronics": "E & TC",
        "e & tc": "E & TC",
        "etc": "E & TC",
        "cs": "CS",
        "it": "IT",
    }
    for keyword, branch_name in branch_keywords.items():
        if keyword in query_lower:
            branch_filter = branch_name
            break

    # If branch filter found in query, apply filtering.
    if branch_filter:
        predictions = [pred for pred in predictions if branch_filter.lower() in pred.get('Branch', '').lower()]
        response_lines = [
            f"Based on your percentile of {user_percentile} and category {user_category} for {branch_filter}, "
            "you might have a good chance of getting into the following colleges:"
        ]
    else:
        response_lines = [
            f"Based on your percentile of {user_percentile} and category {user_category}, "
            "you might have a good chance of getting into the following colleges:"
        ]
        # Prompt user for branch filtering if desired.
        response_lines.append("Would you like to filter by a specific branch? Please specify if yes.")
    for pred in predictions:
        college = pred.get('College', 'Unknown College')
        branch = pred.get('Branch', 'Unknown Branch')
        cutoff = pred.get('Predicted_Cutoff', 'N/A')
        response_lines.append(f"- {college} ({branch}) with an expected cutoff of {cutoff}.")
    
    return "\n".join(response_lines)

def process_user_query(query: str) -> str:
    """Determines the query type (CSV data lookup or ML model prediction) and processes it."""
    query_lower = query.lower()

    if any(keyword in query_lower for keyword in ["percentile", "chance", "get into", "admission"]):
        if re.search(r'\d', query_lower) and re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ/NT/SBC/TFWS)\b', query, re.IGNORECASE):
            return handle_ml_query(query)
        else:
            return ("Could you please provide both your percentile and your category "
                    "(e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS) for admission prediction?")
    else:
        return answer_csv_query(query)

def chatbot():
    print("Welcome to the Engineering Colleges Chatbot!")
    print("You can ask for college details (e.g., address, fees, clubs) or ask for a list of colleges, branches, or categories.")
    print("You can also ask about your admission chances by providing your percentile and category.")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("Chatbot: Thank you for using the chatbot. Goodbye!")
            break
        
        response = process_user_query(user_query)
        print("Chatbot:\n" + response)

if __name__ == "__main__":
    chatbot()
