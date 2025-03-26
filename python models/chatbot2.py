import pandas as pd
import spacy
import re
import random
from fuzzywuzzy import fuzz, process

class CollegeCounselorBot:
    def __init__(self, csv_file_path):
        """Initialize the bot with the college data CSV and load Spacy model."""
        # Load college data
        try:
            self.data = pd.read_csv(csv_file_path)
            # Ensure percentile is numeric
            self.data['Percentile'] = pd.to_numeric(self.data['Percentile'], errors='coerce')
            # Drop rows with NaN percentiles
            self.data = self.data.dropna(subset=['Percentile'])
        except Exception as e:
            print(f"Error loading CSV: {e}")
            # Create empty dataframe with expected columns as fallback
            self.data = pd.DataFrame(columns=['College', 'Year', 'Round', 'Branch', 'Category', 'Percentile'])
        
        # Load Spacy model with larger vocabulary for better understanding
        try:
            self.nlp = spacy.load("en_core_web_md")
        except IOError:
            print("Downloading Spacy model...")
            import subprocess
            subprocess.call([
                "python", "-m", "spacy", "download", "en_core_web_md"
            ])
            self.nlp = spacy.load("en_core_web_md")
        
        # Create sets for quick lookups
        self.all_branches = set(self.data['Branch'].str.lower())
        self.all_categories = set(self.data['Category'].str.lower())
        self.all_colleges = set(self.data['College'].str.lower())
        self.all_years = set(self.data['Year'].astype(str))
        self.all_rounds = set(self.data['Round'].astype(str))
        
        # Maintain conversation context
        self.context = {
            "last_question": None,
            "current_percentile": None,
            "current_category": None,
            "current_branch": None,
            "current_year": None,
            "current_round": None,
            "conversation_history": []
        }
        
        # Natural language variations for responses
        self.greetings = [
            "Hello! I'm your college counseling assistant. How can I help you today?",
            "Hi there! I'm here to help with your college search. What would you like to know?",
            "Welcome! I can help you find colleges based on your percentile and preferences. What can I do for you?",
            "Greetings! I'm your BOT:. How may I assist you with your college search?"
        ]
        
        self.percentile_requests = [
            "What percentile did you score on your entrance exam?",
            "Could you share your percentile score with me?",
            "I'll need your percentile to recommend colleges. What score did you get?",
            "What was your percentile in the entrance exam?"
        ]
        
        self.acknowledgments = [
            "Got it! ",
            "I understand. ",
            "Thanks for that information. ",
            "Alright. ",
            "Perfect. "
        ]
        
        # Command patterns for understanding user intent
        self.command_patterns = {
            "show_categories": [
                r"show (?:all|me|) (?:the |)categories",
                r"list (?:all|) categories",
                r"what (?:are the|) categories",
                r"categories available",
                r"different categories"
            ],
            "show_branches": [
                r"show (?:all|me|) (?:the |)branches",
                r"list (?:all|) branches",
                r"what (?:are the|) branches",
                r"branches available",
                r"different branches",
                r"what (?:programs|courses|majors)",
                r"available (?:programs|courses|majors)"
            ],
            "show_colleges": [
                r"show (?:all|me|) (?:the |)colleges",
                r"list (?:all|) colleges",
                r"what (?:are the|) colleges",
                r"colleges available",
                r"all institutes",
                r"all institutions"
            ]
        }
    
    def remember_user_input(self, user_input, extracted_info):
        """Store the user input and extracted information in context."""
        # Update context with any new information
        if extracted_info["percentile"]:
            self.context["current_percentile"] = extracted_info["percentile"]
        if extracted_info["category"]:
            self.context["current_category"] = extracted_info["category"]
        if extracted_info["branch"]:
            self.context["current_branch"] = extracted_info["branch"]
        if extracted_info["year"]:
            self.context["current_year"] = extracted_info["year"]
        if extracted_info["round"]:
            self.context["current_round"] = extracted_info["round"]
        
        # Add to conversation history
        self.context["conversation_history"].append({
            "user_input": user_input,
            "extracted_info": extracted_info.copy()
        })
    
    def extract_percentile(self, query):
        """Extract percentile from query with multiple methods for better recognition."""
        # Method 1: Check for 'XX percentile' pattern
        percentile_match = re.search(r'(\d+\.?\d*)\s*percentile', query.lower())
        if percentile_match:
            return float(percentile_match.group(1))
        
        # Method 2: Check for 'XX%' pattern
        percent_match = re.search(r'(\d+\.?\d*)\s*%', query.lower())
        if percent_match:
            return float(percent_match.group(1))
        
        # Method 3: Check for 'percentile is XX' or 'score is XX' pattern
        is_match = re.search(r'(percentile|score)\s+(is|of|was|got)\s+(\d+\.?\d*)', query.lower())
        if is_match:
            return float(is_match.group(3))
        
        # Method 4: Check for 'I have XX' or 'I got XX' pattern
        have_match = re.search(r'i\s+(have|got|scored|received|obtained)\s+(\d+\.?\d*)', query.lower())
        if have_match:
            return float(have_match.group(2))
        
        # Method 5: If the last question was about percentile, try to extract just a number
        if self.context["last_question"] == "percentile" and query.strip().replace('.', '', 1).isdigit():
            return float(query.strip())
        
        # Method 6: Check for any standalone number in a short response
        if len(query.split()) <= 3:
            number_match = re.search(r'(\d+\.?\d*)', query)
            if number_match:
                return float(number_match.group(1))
        
        return None
    
    def extract_category(self, query):
        """Extract category with fuzzy matching for better recognition."""
        # Check for direct category matches
        doc = self.nlp(query.lower())
        
        # First, check for exact matches in the categories set
        for token in doc:
            if token.text.lower() in self.all_categories:
                return token.text.lower()
        
        # Look for category mentions with common patterns
        category_patterns = [
            r"category\s*(?:is|:)?\s*(\w+)",
            r"(\w+)\s*category",
            r"for\s+(\w+)\s+(?:category|quota)",
            r"under\s+(\w+)\s+(?:category|quota)"
        ]
        
        for pattern in category_patterns:
            match = re.search(pattern, query.lower())
            if match:
                candidate = match.group(1).lower()
                # Check if it's a close match using fuzzy matching
                if candidate in self.all_categories:
                    return candidate
                else:
                    # Use fuzzy matching to find the closest category
                    closest_match = process.extractOne(candidate, self.all_categories, scorer=fuzz.ratio)
                    if closest_match and closest_match[1] > 80:  # 80% similarity threshold
                        return closest_match[0]
        
        # Check for common category abbreviations
        abbreviations = {
            "gen": "general",
            "sc": "scheduled caste",
            "st": "scheduled tribe",
            "obc": "other backward class",
            "ews": "economically weaker section",
            "pwd": "persons with disability",
            "gen-ews": "general-economically weaker section"
        }
        
        for abbr, full in abbreviations.items():
            if re.search(r'\b' + abbr + r'\b', query.lower()):
                if full in self.all_categories:
                    return full
                else:
                    for category in self.all_categories:
                        if abbr in category:
                            return category
        
        return None
    
    def extract_branch(self, query):
        """Extract branch with fuzzy matching for better recognition."""
        doc = self.nlp(query.lower())
        
        # First, check for exact matches in the branches set
        for token in doc:
            if token.text.lower() in self.all_branches:
                return token.text.lower()
        
        # Look for branch mentions with common patterns
        branch_patterns = [
            r"branch\s*(?:is|:)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*branch",
            r"program\s*(?:is|:)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*program",
            r"major\s*(?:is|:)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*major",
            r"course\s*(?:is|:)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*course",
            r"department\s*(?:is|:)?\s*(\w+(?:\s+\w+)?)",
            r"(\w+(?:\s+\w+)?)\s*department"
        ]
        
        for pattern in branch_patterns:
            match = re.search(pattern, query.lower())
            if match:
                candidate = match.group(1).lower()
                # Check if it's a close match using fuzzy matching
                if candidate in self.all_branches:
                    return candidate
                else:
                    # Use fuzzy matching to find the closest branch
                    closest_match = process.extractOne(candidate, self.all_branches, scorer=fuzz.ratio)
                    if closest_match and closest_match[1] > 75:  # 75% similarity threshold
                        return closest_match[0]
        
        # Check for common branch names in the query
        common_branches = {
            "cse": "computer science",
            "cs": "computer science",
            "it": "information technology",
            "ece": "electronics and communication",
            "ee": "electrical engineering",
            "me": "mechanical engineering",
            "ce": "civil engineering",
            "ai": "artificial intelligence"
        }
        
        for abbr, full in common_branches.items():
            if re.search(r'\b' + abbr + r'\b', query.lower()):
                for branch in self.all_branches:
                    if abbr in branch.lower() or full in branch.lower():
                        return branch
        
        # Check for branch names directly in the query
        for branch in self.all_branches:
            if branch.lower() in query.lower():
                return branch
            # Check for parts of branch names (min 3 chars)
            parts = branch.lower().split()
            for part in parts:
                if len(part) >= 3 and part in query.lower():
                    return branch
        
        return None
    
    def extract_year_and_round(self, query):
        """Extract year and round information from the query."""
        # Extract year
        year_match = re.search(r'(?:year|in)\s*(?::|is)?\s*(\d{4})', query.lower())
        year = None
        if year_match:
            year_val = year_match.group(1)
            if year_val in self.all_years:
                year = int(year_val)
        
        # Extract round
        round_match = re.search(r'(?:round|phase)\s*(?::|is)?\s*(\d+)', query.lower())
        round_num = None
        if round_match:
            round_val = round_match.group(1)
            if round_val in self.all_rounds:
                round_num = int(round_val)
        
        return year, round_num
    
    def extract_info_with_nlp(self, query):
        """Extract all relevant information from the query using NLP techniques."""
        # Core information
        percentile = self.extract_percentile(query)
        category = self.extract_category(query)
        branch = self.extract_branch(query)
        year, round_num = self.extract_year_and_round(query)
        
        # If we have information in context, use it as fallback
        if not percentile and self.context["current_percentile"]:
            percentile = self.context["current_percentile"]
        if not category and self.context["current_category"]:
            category = self.context["current_category"]
        if not branch and self.context["current_branch"]:
            branch = self.context["current_branch"]
        if not year and self.context["current_year"]:
            year = self.context["current_year"]
        if not round_num and self.context["current_round"]:
            round_num = self.context["current_round"]
        
        return {
            "percentile": percentile,
            "category": category,
            "branch": branch,
            "year": year,
            "round": round_num
        }
    
    def find_colleges(self, extracted_info):
        """Find colleges matching the extracted criteria."""
        percentile = extracted_info["percentile"]
        category = extracted_info["category"]
        branch = extracted_info["branch"]
        year = extracted_info["year"]
        round_num = extracted_info["round"]
        
        # Start with the full dataset
        filtered_data = self.data.copy()
        
        # Apply filters if provided
        if category:
            category_filter = filtered_data['Category'].str.lower() == category.lower()
            filtered_data = filtered_data[category_filter]
        if branch:
            branch_filter = filtered_data['Branch'].str.lower() == branch.lower()
            filtered_data = filtered_data[branch_filter]
        if year:
            filtered_data = filtered_data[filtered_data['Year'] == year]
        if round_num:
            filtered_data = filtered_data[filtered_data['Round'] == round_num]
        
        # Find colleges with percentile cutoffs just below the given percentile
        if percentile:
            eligible_colleges = filtered_data[filtered_data['Percentile'] <= percentile]
            
            if not eligible_colleges.empty:
                # Sort by percentile in descending order to get the closest matches
                eligible_colleges = eligible_colleges.sort_values(by='Percentile', ascending=False)
                return eligible_colleges.head(10)
        
        return filtered_data.head(10)  # Return some colleges even without percentile filter
    
    def handle_special_commands(self, query):
        """Handle special commands like showing all categories, branches, etc."""
        # Check for category listing request
        for pattern in self.command_patterns["show_categories"]:
            if re.search(pattern, query.lower()):
                categories = sorted(list(self.all_categories))
                response = "Here are all the available categories:\n\n"
                response += ", ".join(categories)
                return response
        
        # Check for branch listing request
        for pattern in self.command_patterns["show_branches"]:
            if re.search(pattern, query.lower()):
                branches = sorted(list(self.all_branches))
                response = "Here are all the available branches/programs:\n\n"
                response += ", ".join(branches)
                return response
        
        # Check for college listing request
        for pattern in self.command_patterns["show_colleges"]:
            if re.search(pattern, query.lower()):
                # If we have a percentile, show colleges for that percentile
                if self.context["current_percentile"]:
                    return self.generate_college_response({
                        "percentile": self.context["current_percentile"],
                        "category": self.context["current_category"],
                        "branch": self.context["current_branch"],
                        "year": self.context["current_year"],
                        "round": self.context["current_round"]
                    })
                else:
                    colleges = sorted(list(self.all_colleges))[:20]  # Limit to 20
                    response = "Here are some of the colleges in our database:\n\n"
                    response += ", ".join(colleges)
                    response += "\n\nTo see colleges that match your specific criteria, please provide your percentile."
                    return response
        
        return None
    
    def generate_college_response(self, extracted_info):
        """Generate a response about colleges based on the extracted information."""
        colleges = self.find_colleges(extracted_info)
        
        if colleges.empty:
            response = "I couldn't find any colleges matching your criteria. "
            
            if not extracted_info["percentile"]:
                response += "Could you please provide your percentile score?"
                self.context["last_question"] = "percentile"
            elif not extracted_info["branch"] and not extracted_info["category"]:
                response += "Could you specify your preferred branch or category?"
                self.context["last_question"] = "branch_category"
            elif not extracted_info["branch"]:
                response += "Could you specify your preferred branch/program?"
                self.context["last_question"] = "branch"
            elif not extracted_info["category"]:
                response += "Could you specify your category?"
                self.context["last_question"] = "category"
            else:
                response += "Try broadening your search by removing some filters or adjusting your percentile."
                self.context["last_question"] = None
            
            return response
        
        # Get the filters used
        filters = []
        if extracted_info["percentile"]:
            filters.append(f"{extracted_info['percentile']} percentile")
        if extracted_info["category"]:
            filters.append(f"category: {extracted_info['category']}")
        if extracted_info["branch"]:
            filters.append(f"branch: {extracted_info['branch']}")
        if extracted_info["year"]:
            filters.append(f"year: {extracted_info['year']}")
        if extracted_info["round"]:
            filters.append(f"round: {extracted_info['round']}")
        
        if filters:
            filter_text = ", ".join(filters)
            response = f"Here are colleges matching your criteria ({filter_text}):\n\n"
        else:
            response = "Here are some colleges from our database:\n\n"
        
        # Format college information
        for i, (_, college) in enumerate(colleges.iterrows(), 1):
            response += f"{i}. {college['College']} - {college['Branch']}\n"
            response += f"   Cutoff: {college['Percentile']} percentile\n"
            response += f"   Year: {college['Year']}, Round: {college['Round']}, Category: {college['Category']}\n\n"
        
        # Add a helpful suggestion
        if not extracted_info["branch"] and not extracted_info["category"]:
            response += "Tip: You can specify a branch or category for more targeted results."
        elif not extracted_info["branch"]:
            response += "Tip: You can specify a branch for more targeted results."
        elif not extracted_info["category"]:
            response += "Tip: You can specify a category for more targeted results."
        
        self.context["last_question"] = None
        return response
    
    def handle_user_query(self, query):
        """Main function to handle user queries."""
        # Check for special commands first
        special_command_response = self.handle_special_commands(query)
        if special_command_response:
            return special_command_response
        
        # Extract information from the query
        extracted_info = self.extract_info_with_nlp(query)
        
        # Remember what we learned from this query
        self.remember_user_input(query, extracted_info)
        
        # Generate a response based on the extracted information
        return self.generate_college_response(extracted_info)
    
    def get_response(self, query):
        """Get a response to the user's query with better natural language handling."""
        # Normalize the query
        query = query.strip()
        
        # Handle greetings
        greeting_words = ["hello", "hi", "hey", "greetings", "howdy", "good morning", "good afternoon", "good evening"]
        if any(word in query.lower() for word in greeting_words) and len(query.split()) <= 3:
            return random.choice(self.greetings)
        
        # Handle thanks
        thanks_words = ["thanks", "thank you", "appreciate", "grateful", "thank"]
        if any(word in query.lower() for word in thanks_words) and len(query.split()) <= 5:
            return "You're welcome! Is there anything else you'd like to know about colleges or admissions?"
        
        # Handle goodbyes
        goodbye_words = ["bye", "goodbye", "see you", "farewell", "exit", "quit"]
        if any(word in query.lower() for word in goodbye_words) and len(query.split()) <= 3:
            return "Goodbye! Best of luck with your college admissions process!"
        
        # Handle help requests
        help_words = ["help", "how", "what can you do", "instructions"]
        if any(phrase in query.lower() for phrase in help_words) and len(query.split()) <= 5:
            return ("I can help you find colleges based on your entrance exam percentile. You can ask me things like:\n\n"
                   "- 'What colleges can I get with 85 percentile?'\n"
                   "- 'I have 92.5 percentile in category SC, which colleges can I get?'\n"
                   "- 'Show me Computer Science colleges for 88 percentile'\n"
                   "- 'Show all categories'\n"
                   "- 'List all branches'\n\n"
                   "Feel free to ask in your own words. I'll do my best to understand and provide relevant information.")
        
        # Handle empty or very short queries
        if len(query) <= 1:
            return "Could you please provide more details about what you're looking for?"
        
        # Handle the main query
        return self.handle_user_query(query)
    
    def start_chat(self):
        """Start an interactive chat session with the user."""
        print("BOT:: Hello! I'm your college counseling assistant. I can help you find colleges based on your percentile and preferences.")
        print("Type 'quit' or 'exit' to end the conversation.")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                print("BOT: Thank you for using the BOT:. Good luck with your admissions!")
                break
            
            response = self.get_response(user_input)
            print(f"BOT:: {response}")


# Example usage
if __name__ == "__main__":
    bot = CollegeCounselorBot("colleges.csv")
    bot.start_chat()