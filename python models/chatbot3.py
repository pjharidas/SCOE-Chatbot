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
        # Use word boundaries for more precise matching if needed, e.g., re.search(r'\b' + re.escape(attribute.lower()) + r'\b', query_lower)
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
    
    # Combine full names and short forms for matching
    known_colleges_full = college_df['College Name'].dropna().tolist()
    known_colleges_short = college_df['College Name(shortform)'].dropna().tolist()
    known_colleges_map = {name.lower(): name for name in known_colleges_full}
    known_short_map = {short.lower(): name for short, name in zip(known_colleges_short, known_colleges_full)}
    
    found_colleges = set()

    # Check spaCy entities against known lists
    for ent_text in colleges:
        ent_lower = ent_text.lower()
        if ent_lower in known_colleges_map:
            found_colleges.add(known_colleges_map[ent_lower])
        elif ent_lower in known_short_map:
             found_colleges.add(known_short_map[ent_lower])

    # Check word by word for known short forms (more robust check needed ideally)
    text_lower = text.lower()
    for short_lower, full_name in known_short_map.items():
         # Use word boundaries to avoid partial matches (e.g., 'it' in 'merit')
         if re.search(r'\b' + re.escape(short_lower) + r'\b', text_lower):
              found_colleges.add(full_name)

    # Check for full names (might be less reliable with simple substring check)
    for full_lower, full_name in known_colleges_map.items():
        if full_lower in text_lower:
             found_colleges.add(full_name)
             
    # Return the list of unique full college names found
    return list(found_colleges)


def answer_csv_query(query: str) -> str:
    query_lower = query.lower()

    # Handle list queries first.
    if "list" in query_lower:
        if "college" in query_lower:
            return list_all_colleges()
        if "branch" in query_lower:
            return list_all_branches()
        if "category" or "categories" in query_lower: # Note: This condition might always be true due to 'or'. Should be `if "category" in query_lower or "categories" in query_lower:`
            return list_all_categories()

    single_field = get_attribute_from_query(query)
    requested_fields = []
    populated_requested_fields = False # Flag to track if group mapping added fields

    # Mapping keywords to groups of fields.
    group_mapping = {
        "contact": ['Phone Number'],
        "fee": ["Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)"],
        "fee structure": ["Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)"],
        "intake": ['Biotechnology Intake', 'Civil Engineering Intake', 'Chemical Engineering Intake',
                   'Computer Engineering Intake', 'Information Technology Intake', 'E & TC Engineering Intake',
                   'Mechanical Engineering Intake', 'Electrical Engineering Intake'],
        "admission documents": ['Admission Documents Required'],
        "admission": ['Admission Documents Required'], # Consider if this should also include fees/intake
        "club": ['Clubs'],
        "cultural": ['Cultural Activities']
    }

    for key, fields in group_mapping.items():
        # Use word boundaries for keys like 'fee' to avoid matching 'feeder' etc.
        if re.search(r'\b' + re.escape(key) + r'\b', query_lower):
            if key == "fee" or key == "fee structure": # Handle fee structure explicitly
                temp = []
                # Check for specific category keywords within the fee request
                if "open" in query_lower:
                    temp.append("Fee (Open)")
                if any(cat_key in query_lower for cat_key in ["obc", "ews", "ebc"]):
                    temp.append("Fee (OBC/EWS/EBC)")
                if any(cat_key in query_lower for cat_key in ["sc", "st"]):
                    temp.append("Fee (SC/ST)")
                if any(cat_key in query_lower for cat_key in ["vj", "nt", "sbc", "tfws"]):
                    temp.append("Fee (VJ/NT/SBC/TFWS)")

                # If specific categories were mentioned, use them, otherwise use all fee fields
                if temp:
                    requested_fields.extend(temp)
                    populated_requested_fields = True
                else:
                    # If just "fee" or "fee structure" was mentioned without category, add all
                    requested_fields.extend(fields)
                    populated_requested_fields = True
            else:
                requested_fields.extend(fields)
                populated_requested_fields = True

# Patch: Also handle fallback below for single_field fee detection
    # If no fields were identified by group mapping OR direct attribute lookup,
    # try to infer the desired field from other keywords.
    # This only runs if requested_fields is empty AND single_field is None (or was cleared above).
    if not requested_fields and not single_field:
        if "address" in query_lower:
            single_field = "Address"
        elif "principal" in query_lower:
            single_field = "Principal Name"
        # Use "contact" or "phone" as fallback keywords for Phone Number
        elif "contact" in query_lower or "phone" in query_lower:
             single_field = "Phone Number"
        # Fallback for fee (if not handled by group mapping)
        elif "fee" in query_lower:
            # If only "fee" is mentioned, return all fee fields
            requested_fields.extend([
                "Fee (Open)", "Fee (OBC/EWS/EBC)", "Fee (SC/ST)", "Fee (VJ/NT/SBC/TFWS)"
            ])
            populated_requested_fields = True
        # Fallback for intake (if not handled by group mapping)
        elif "intake" in query_lower:
            # Prioritize more specific terms
            if "computer" in query_lower: single_field = "Computer Engineering Intake"
            elif "information technology" in query_lower or " it " in query_lower: single_field = "Information Technology Intake"
            elif "e & tc" in query_lower or "electronics" in query_lower or "entc" in query_lower: single_field = "E & TC Engineering Intake"
            elif "electrical" in query_lower: single_field = "Electrical Engineering Intake"
            elif "mechanical" in query_lower: single_field = "Mechanical Engineering Intake"
            elif "civil" in query_lower: single_field = "Civil Engineering Intake"
            elif "chemical" in query_lower: single_field = "Chemical Engineering Intake"
            elif "biotechnology" in query_lower or "biotech" in query_lower: single_field = "Biotechnology Intake"
            # Add a default intake? Or maybe prompt user? For now, no default.

    # If group mapping populated fields, prioritize it over a single attribute found earlier.
    # Also ensure uniqueness in requested_fields.
    if populated_requested_fields:
        single_field = None # Clear single_field if group mapping was successful
        requested_fields = list(dict.fromkeys(requested_fields)) # Remove potential duplicates

    # Fallback detection: If no fields were identified by group mapping OR direct attribute lookup,
    # try to infer the desired field from other keywords.
    # This only runs if requested_fields is empty AND single_field is None (or was cleared above).
    if not requested_fields and not single_field:
        if "address" in query_lower:
            single_field = "Address"
        elif "principal" in query_lower:
            single_field = "Principal Name"
        # Use "contact" or "phone" as fallback keywords for Phone Number
        elif "contact" in query_lower or "phone" in query_lower:
             single_field = "Phone Number"
        # Fallback for fee (if not handled by group mapping)
        elif "fee" in query_lower:
            if "open" in query_lower: single_field = "Fee (Open)"
            elif any(x in query_lower for x in ["obc", "ews", "ebc"]): single_field = "Fee (OBC/EWS/EBC)"
            elif any(x in query_lower for x in ["sc", "st"]): single_field = "Fee (SC/ST)"
            elif any(x in query_lower for x in ["vj", "nt", "sbc", "tfws"]): single_field = "Fee (VJ/NT/SBC/TFWS)"
            else: single_field = "Fee (Open)" # Default fee if category not specified
        # Fallback for intake (if not handled by group mapping)
        elif "intake" in query_lower:
            # Prioritize more specific terms
            if "computer" in query_lower: single_field = "Computer Engineering Intake"
            elif "information technology" in query_lower or " it " in query_lower: single_field = "Information Technology Intake"
            elif "e & tc" in query_lower or "electronics" in query_lower or "entc" in query_lower: single_field = "E & TC Engineering Intake"
            elif "electrical" in query_lower: single_field = "Electrical Engineering Intake"
            elif "mechanical" in query_lower: single_field = "Mechanical Engineering Intake"
            elif "civil" in query_lower: single_field = "Civil Engineering Intake"
            elif "chemical" in query_lower: single_field = "Chemical Engineering Intake"
            elif "biotechnology" in query_lower or "biotech" in query_lower: single_field = "Biotechnology Intake"
            # Add a default intake? Or maybe prompt user? For now, no default.

    # Determine the college(s) mentioned.
    colleges_found = extract_college_name(query)
    if not colleges_found:
        # If no specific college found, check if the query implies *all* colleges
        if any(word in query_lower for word in ["all colleges", "list colleges", "which colleges"]):
             if requested_fields or single_field:
                 # Try to list the requested field for all colleges
                 responses = []
                 field_to_show = single_field if single_field else requested_fields[0] # Simplistic: show first requested field
                 if field_to_show in college_df.columns:
                     responses.append(f"Here's the {field_to_show} for all colleges:")
                     for index, row in college_df.iterrows():
                         responses.append(f"- {row['College Name']}: {row[field_to_show]}")
                     return "\n".join(responses)
                 else:
                     return "Please specify which information you want listed for all colleges."
             else:
                 return list_all_colleges() # Default to listing names if no field specified

        # Otherwise, ask for clarification
        return ("I'm sorry, I couldn't determine which college you are asking about.\n"
                "Could you please specify the college name? You can also ask to 'list all colleges'.")

    responses = []
    for college_name in colleges_found:
        # Match using the full college name identified by extract_college_name
        college_data = college_df[college_df['College Name'] == college_name]
    
        if college_data.empty:
            responses.append(f"I couldn't find details for {college_name}.\n")
        else:
            college_row = college_data.iloc[0]
            # Prioritize requested_fields if available
            if requested_fields:
                details = []
                for field in requested_fields:
                    if field in college_row and pd.notna(college_row[field]):
                        details.append(f"{field}: {college_row[field]}")
                    else:
                        details.append(f"{field}: Not Available")
                responses.append(f"--- {college_name} ---\n" + "\n".join(details) + "\n")
            # Else, use single_field if identified
            elif single_field and single_field in college_row and pd.notna(college_row[single_field]):
                value = college_row[single_field]
                responses.append(f"The *{single_field}* for *{college_name}* is: {value}.\n")
            elif single_field:
                responses.append(f"The *{single_field}* for *{college_name}* is not available.\n")
            # If no specific field is requested, show all available details.
            else:
                details = []
                for field in college_df.columns:
                    if pd.notna(college_row[field]):
                        details.append(f"*{field}: *{college_row[field]}")
                responses.append(f"--- {college_name} Details ---\n" + "\n".join(details) + "\n")


    return "\n".join(responses)

def handle_ml_query(query: str) -> str:
    """Processes queries related to admission chances using an ML model."""
    percentile_match = re.search(r'(\d{1,3}(?:\.\d+)?)', query)
    # More robust category extraction needed, handle variations like VJNT, TFWS etc.
    category_match = re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ[/ ]?NT[/ ]?SBC[/ ]?TFWS|VJ|NT|SBC|TFWS|EBC)\b', query, re.IGNORECASE)

    if not percentile_match:
        return ("To predict eligible colleges, please provide your percentile (e.g., '95 percentile').")
    if not category_match:
        return ("To predict eligible colleges, please provide your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS).")

    user_percentile = float(percentile_match.group(1))
    user_category = category_match.group(1).upper()
    # Normalize category if needed (e.g., VJ -> VJ/NT/SBC/TFWS) - depends on ML model's expected input
    # Example normalization (adjust based on ML_Model2 requirements):
    category_map = {
        "VJ": "VJ", "NT": "NT", "SBC": "SBC", "TFWS": "TFWS","open": "OPEN",
        "obc": "OBC", "sc": "SC", "st": "ST", "ews": "EWS",
        "EBC": "EWS" # Assuming EBC maps to OBC for the model
    }
    user_category = category_map.get(user_category, user_category)


    current_year = 2025 # Consider making this dynamic or configurable

    try:
        ml_df_clean = ML_Model2.load_and_clean('colleges.csv')
        ml_pipe = ML_Model2.build_pipeline()
        ml_pipe = ML_Model2.fit_full(ml_df_clean, ml_pipe)
        predictions = ML_Model2.get_recommendations(ml_df_clean, ml_pipe, user_category, user_percentile, current_year)
    except FileNotFoundError:
        return "Error: The 'colleges.csv' file required for prediction was not found."
    except Exception as e:
        print(f"Error during ML prediction: {e}") # Log the error
        return "Sorry, I encountered an error while trying to generate predictions."


    if not predictions:
        return (f"Based on your percentile of *{user_percentile}* and category *{user_category}*, no matching colleges were found in the prediction model.")

    # Check if the query already contains a branch filter keyword.
    branch_filter = None
    query_lower = query.lower()
    # Expand keywords and map to consistent branch names used in predictions
    branch_keywords = {
        "computer": "Computer Engineering", # Assuming prediction output uses full names
        "cs": "Computer Engineering",
        "information": "Information Technology",
        "it": "Information Technology",
        "mechanical": "Mechanical Engineering",
        "mech": "Mechanical Engineering",
        "electrical": "Electrical Engineering",
        "e & tc": "E & TC Engineering",
        "entc": "E & TC Engineering",
        "electronics": "E & TC Engineering",
        "civil": "Civil Engineering",
        "chemical": "Chemical Engineering",
        "chem": "Chemical Engineering",
        "biotechnology": "Biotechnology",
        "biotech": "Biotechnology",
        "bio-tech": "Biotechnology",
    }
    # Search for keywords in the query
    found_branch_keyword = None
    for keyword, branch_name in branch_keywords.items():
         # Use word boundaries for more specific matching
         if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
            branch_filter = branch_name
            found_branch_keyword = keyword # Store the keyword found
            break

    filtered_predictions = predictions
    if branch_filter:
        # Filter predictions based on the identified branch name
        # Compare case-insensitively and handle potential variations in prediction output format
        filtered_predictions = [
            pred for pred in predictions
            if branch_filter.lower() in pred.get('Branch', '').lower()
        ]
        if not filtered_predictions:
            return (f"Based on your percentile of *{user_percentile}* and category *{user_category}*, no colleges were found for the branch '*{branch_filter}*'.")
        response_lines = [
            f"Based on your percentile (*{user_percentile}*) and category (*{user_category}*), "
            f"here are potential colleges for '*{branch_filter}*':"
        ]
    else:
        response_lines = [
            f"Based on your percentile *({user_percentile})* and category *({user_category})*, "
            "you might have a chance in these colleges/branches:"
        ]
        # Consider prompting for branch filtering if many results are returned
        if len(predictions) > 10: # Example threshold
             response_lines.append("You can ask again specifying a branch (e.g., 'computer', 'mechanical') to narrow down results.")

    # Format the predictions
    for pred in filtered_predictions:
        college = pred.get('College', 'Unknown College')
        branch = pred.get('Branch', 'Unknown Branch')
        cutoff = pred.get('Predicted_Cutoff', 'N/A')
        # Handle potential empty dicts or missing data gracefully
        if isinstance(college, dict) or college == "Unknown College" or not college:
             # Skip or log invalid prediction entries
             continue
        cutoff_str = f"{cutoff:.2f}" if isinstance(cutoff, (int, float)) else str(cutoff)
        response_lines.append(f"- {college} ({branch}) - Predicted Cutoff: {cutoff_str}")

    if len(response_lines) <= 1: # Only the header line was added
         return (f"Based on your percentile of {user_percentile} and category {user_category}"
                 f"{f' for branch {branch_filter}' if branch_filter else ''}, no specific recommendations could be generated.")


    return "\n".join(response_lines)

def process_user_query(query: str) -> str:
    """Determines the query type (CSV data lookup or ML model prediction) and processes it."""
    query_lower = query.lower()

    # Keywords indicating ML prediction request
    ml_keywords = ["percentile", "chance", "get into", "admission into", "cutoff", "predict", "eligible colleges"]
    # Keywords indicating CSV lookup request (can overlap, so ML check is prioritized if numbers/category present)
    csv_keywords = ["address", "fee", "intake", "principal", "contact", "phone", "document", "club", "cultural", "list"]

    # Check for percentile and category presence for ML query
    has_percentile = re.search(r'\d{1,3}(?:\.\d+)?', query_lower) is not None
    has_category = re.search(r'\b(OPEN|OBC|SC|ST|EWS|VJ|NT|SBC|TFWS|EBC)\b', query, re.IGNORECASE) is not None

    # Prioritize ML query if relevant keywords AND data are present
    if any(keyword in query_lower for keyword in ml_keywords) and has_percentile and has_category:
        return handle_ml_query(query)

    # If ML keywords are present but data is missing, prompt for data
    if any(keyword in query_lower for keyword in ml_keywords):
         missing_info = []
         if not has_percentile:
             missing_info.append("your percentile")
         if not has_category:
             missing_info.append("your category (e.g., OPEN, OBC, SC, ST, EWS, VJ/NT/SBC/TFWS)")
         return f"To predict admission chances, please provide {' and '.join(missing_info)}."

    # Otherwise, assume it's a CSV data lookup query
    # Check if any CSV-related keywords are present, or default to CSV lookup
    # if any(keyword in query_lower for keyword in csv_keywords) or not any(kw in query_lower for kw in ml_keywords):
    return answer_csv_query(query)
    # else:
    #     # Fallback if query type is unclear
    #     return ("I'm not sure how to answer that. You can ask about college details (address, fees, intake), "
    #             "list colleges/branches/categories, or ask for admission predictions with your percentile and category.")


def chatbot():
    print("Welcome to the Engineering Colleges Chatbot!")
    print("Ask about college details (address, fees, intake, principal, contact, clubs, etc.).")
    print("Use 'list colleges', 'list branches', or 'list categories'.")
    print("For admission predictions, provide percentile and category (e.g., 'chance with 90 percentile in OPEN').")
    print("Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Thank you for using the chatbot. Goodbye!")
            break
        if not user_query:
            continue

        response = process_user_query(user_query)
        print("\nChatbot:\n" + response + "\n")

if __name__ == "__main__": # Corrected the dunder check
    chatbot()