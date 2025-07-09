from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import gspread
import os
import secrets
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

#Cloudinary credentials
cloudinary.config(
  cloud_name = '******',
  api_key = '********',
  api_secret = '**********'
)


    # --- Google Sheets Configuration ---
    # Path to your service account key file (should be in the same directory as app.py on PythonAnywhere)
GOOGLE_SHEETS_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials.json')
    # Name of your Google Sheet
GOOGLE_SHEET_NAME = "UserData"

    # --- Initialize Google Sheets client ---
try:
        gc = gspread.service_account(filename=GOOGLE_SHEETS_CREDENTIALS_PATH)
        spreadsheet = gc.open(GOOGLE_SHEET_NAME)
        user_data_worksheet = spreadsheet.worksheet("Sheet1") # Assuming your user data is on Sheet1
        print(f"Google Sheets initialized successfully for spreadsheet: {GOOGLE_SHEET_NAME}")
except Exception as e:
        print(f"Error initializing Google Sheets: {e}")
        print("Please ensure 'credentials.json' is in the same directory as app.py and your sheet is shared with the service account.")
        user_data_worksheet = None # Set to None if initialization fails

    # --- Strain Data (non-relational database) ---
def get_cannabis_strain_data():
        """
        Returns a pandas DataFrame containing consolidated cannabis strain data.
        The data includes 'Desired State', 'Strain Name', and 'THC Score'.
        Values for 'THC Score' that were originally non-numeric are set to None.
        """
        data = {
            'Desired State': [
                'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal', 'Arousal',
                'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation', 'Body Relaxation',
                'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired', 'Creative & Inspired',
                'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria', 'Euphoria',
                'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus', 'Focus',
                'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence', 'Increased Social Confidence',
                'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic', 'Uplifted & Energetic'
            ],
            'Strain Name': [
                'Donny Burger', 'Rainbow Sherbet', 'Gastro Pop', 'LA Kush Cake', 'Jet Fuel Gelato', 'Pure Michigan', 'Red Velvet', 'Rainbow', 'Bacio Gelato', 'Purple Runtz', 'Alien Cookies', 'Spritzer', 'Purple Panty Dropper', 'Banana Runtz', 'Pink Rozay',
                'The Original Z', 'Sherbert', 'Apple Fritter', 'Gelato #41', 'Kush Mints', 'Peanut Butter Breath', 'Blueberry Muffin', 'Animal Mints', 'Animal Cookies', 'Blue Cookies', 'Birthday Cake', 'Cherry Gelato', 'Ghost OG', 'Marshmallow OG', 'Blue Raspberry',
                'Cherry Poppers', 'Gelatti', 'F1 Durb', 'OG Chem', 'Zereal', 'Chocolate Thai', 'Sunset Runtz', 'Zlushi', 'White Cherry OG', 'Raspberry Parfait', 'Wham', 'Mafia Funeral', 'Bodhi\'s Charms', 'Designer Runtz', 'Banana MAC',
                'Grape Gasoline', 'Cotton Candy', 'Super Runtz', 'Cadillac Rainbow', 'Alien OG', 'Motorbreath', 'Blue Runtz', 'Nerds', 'Chimera', 'E85', 'LSD', 'Apple Tartz', 'Pop Rox', 'First Class Funk', 'Strawberry Runtz',
                'Jokerz', 'Candy Fumez', 'The Soap', 'Wedding Crasher', 'Pink Certz', 'Warhead', 'Zookies', 'Bubble Bath', 'Harlequin', 'Peach Ringz', 'Pancakes', 'Apple Jack', 'Mac and Cheese', 'Yellow Zushi', 'Oreo Blizzy',
                'Sherbanger', 'Banana Kush', 'Carbon Fiber', 'Silver Haze', 'Blue Lobster', 'Tropical Cherry', 'Crunch Berries', 'Jungle Cake', 'Tropical Runtz', 'Acai Berry Gelato', 'Alien Mints', 'Baby Yoda', 'Lychee', 'Panama Red', 'Pinnacle',
                'Green Crack', 'Durban Poison', 'Strawberry Cough', 'Mimosa', 'Super Lemon Haze', 'Maui Wowie', 'Tropicana Cookies', 'Super Silver Haze', 'Gelonade', 'Jet Fuel', 'Alaskan Thunder Fuck', 'Acapulco Gold', 'Candyland', 'Guava', 'Ghost Train Haze'
            ],
            'THC Score': [
                27.0, 18.0, 26.0, 23.0, 24.0, 29.0, 26.0, 18.0, None, None, 25.0, 32.0, 22.0, 29.0, 21.0,
                20.0, 18.0, 24.0, 21.0, 28.0, 20.0, 20.0, 18.0, 19.0, 17.0, 23.0, 14.0, 19.0, 20.0, None,
                20.0, 19.0, 19.0, 24.0, 20.0, 16.0, 23.0, None, 20.0, 21.0, None, 26.0, 23.0, 27.0, 20.0,
                25.0, 19.0, 21.0, 37.54, 19.0, 26.0, 21.0, 20.0, 27.0, 30.0, 18.0, 26.0, None, 26.0, None,
                22.0, 27.0, 24.0, 21.0, 24.0, 18.0, 21.0, 21.0, 9.0, 21.0, 22.0, 21.0, 23.0, None, None,
                22.0, 21.0, 24.0, 23.0, 30.0, 24.0, 21.0, 21.0, 24.0, None, None, 22.0, None, 17.0, 20.0,
                17.0, 19.0, 19.0, 19.0, 19.0, 19.0, 16.0, 21.0, 22.0, 20.0, 16.0, 18.0, 19.0, 21.0, 19.0
            ]
        }
        df = pd.DataFrame(data)
        return df

    # Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # For Flask session management

strain_data_df = get_cannabis_strain_data()

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    # --- Helper function to find a user row in Google Sheet ---
def find_user_row(email):
        if not user_data_worksheet:
            print("find_user_row: user_data_worksheet is None")
            return None
        try:
            # Get all records as a list of dictionaries
            all_records = user_data_worksheet.get_all_records()
            for i, record in enumerate(all_records):
                if record.get('Email') == email:
                    # Return row index (gspread is 1-indexed, headers are row 1)
                    print(f"find_user_row: Found user {email} at row {i+2}")
                    return i + 2
            print(f"find_user_row: User {email} not found.")
            return None
        except Exception as e:
            print(f"Error in find_user_row: {e}")
            return None

    # --- Helper function to get column index safely ---
def get_column_index(worksheet, column_name):
        try:
            cell = worksheet.find(column_name)
            print(f"get_column_index: Found column '{column_name}' at column index {cell.col}")
            return cell.col
        except gspread.exceptions.APIError as e:
            headers = worksheet.row_values(1)
            print(f"API Error: Column '{column_name}' not found. Headers: {headers}. Error: {e}")
            return None
        except Exception as e:
            print(f"General Error getting column index for '{column_name}': {e}")
            return None

    # Home Page: Displays the form for user input
@app.route('/')
def home():
        desired_states_list = strain_data_df['Desired State'].unique().tolist()
        return render_template('home.html', desired_states=desired_states_list)

# Signup Page: Prompts user to set a password to view the map
@app.route('/signup', methods=['GET', 'POST'])
def signup():
        user_email_from_param = request.args.get('email')
        print(f"Signup: GET request, email from param: {user_email_from_param}")

        if request.method == 'POST':
            password = request.form.get('password')
            signup_email = request.form.get('signup_email')
            print(f"Signup: POST request, email: {signup_email}, password: {'*' * len(str(password))}")


            if not signup_email:
                print("Signup: Email not provided in signup form.")
                return render_template('signup.html', error_message="Email is required for signup.", email_prefill=user_email_from_param)

            if password and len(password) >= 6:
                if user_data_worksheet:
                    row_index = find_user_row(signup_email)
                    if row_index:
                        print(f"Signup: User found for {signup_email} at row {row_index}.")
                        password_col = get_column_index(user_data_worksheet, 'Password')
                        signed_up_col = get_column_index(user_data_worksheet, 'Signed Up for Map')


                        if password_col is not None and signed_up_col is not None:
                            user_data_worksheet.update_cell(row_index, password_col, password)
                            user_data_worksheet.update_cell(row_index, signed_up_col, 'True') # Store as string 'True'
                            print(f"Signup: Updated password and signed up status to 'True' for {signup_email}.")
                            return redirect(url_for('results', email=signup_email))
                        else:
                            print("Signup: Failed to find Password or Signed Up for Map columns in sheet for update.")
                            return render_template('signup.html', error_message="Required Google Sheet columns not found. Check sheet headers.", email_prefill=signup_email)
                    else:
                        print(f"Signup: User email {signup_email} not found in sheet for password update. This should not happen if previous steps worked.")
                        return render_template('signup.html', error_message="User email not found. Please go back to home page or ensure email is correct.", email_prefill=signup_email)
                else:
                    print("Signup: Google Sheets worksheet is None.")
                    return render_template('signup.html', error_message="Google Sheets not configured. Cannot save password.", email_prefill=user_email_from_param)
            else:
                print("Signup: Password too short or not provided.")
                return render_template('signup.html', error_message="Password must be at least 6 characters.", email_prefill=user_email_from_param)

        return render_template('signup.html', email_prefill=user_email_from_param)


# Results Page: Processes form submission and displays strain recommendations,
# conditionally showing/unblurring the map.
@app.route('/results', methods=['GET', 'POST'])
def results():
    name = 'Guest'
    email = ''
    desired_state = ''
    show_map = False
    strains_for_template = []
    profile_picture_url = url_for('static', filename='uploads/blank-profile-picture-973460_1280.webp')

    if request.method == 'POST':
        name = request.form.get('Name')
        email = request.form.get('email')
        desired_state = request.form.get('desired_state')
        print(f"Results (POST from home.html): Name: {name}, Email: {email}, Desired State: {desired_state}")

        if not desired_state:
            print("Results (POST): Desired state not provided, redirecting to home.")
            return redirect(url_for('home'))

        if user_data_worksheet:
            row_index = find_user_row(email)
            if row_index:
                print(f"Results (POST): User {email} found at row {row_index}.")
                desired_state_col = get_column_index(user_data_worksheet, 'Desired State')
                if desired_state_col is not None:
                    user_data_worksheet.update_cell(row_index, desired_state_col, desired_state)
                    print(f"Results (POST): Updated desired state for {email} in sheet.")

                user_record = user_data_worksheet.row_values(row_index)
                headers = user_data_worksheet.row_values(1)
                user_dict = dict(zip(headers, user_record))

                # Get map visibility
                sheet_signed_up_value = user_dict.get('Signed Up for Map', 'False').lower()
                show_map = sheet_signed_up_value == 'true'

                # Get profile name and picture
                name = user_dict.get('Name', 'Guest')
                profile_picture_url = user_dict.get('Profile Picture URL', profile_picture_url)
            else:
                # Add new user record
                print(f"Results (POST): Adding new user {email} to sheet.")
                new_row = [name, email, desired_state, 'False', '', '']  # Adding empty Profile Picture URL
                user_data_worksheet.append_row(new_row)
                show_map = False
        else:
            print("Warning: Google Sheets not available.")

    elif request.method == 'GET':
        email = request.args.get('email')
        print(f"Results (GET): Email from param: {email}")
        if user_data_worksheet and email:
            row_index = find_user_row(email)
            if row_index:
                print(f"Results (GET): User {email} found at row {row_index}.")
                user_record = user_data_worksheet.row_values(row_index)
                headers = user_data_worksheet.row_values(1)
                user_dict = dict(zip(headers, user_record))

                name = user_dict.get('Name', 'Guest')
                desired_state = user_dict.get('Desired State', '')
                profile_picture_url = user_dict.get('Profile Picture URL', profile_picture_url)

                sheet_signed_up_value = user_dict.get('Signed Up for Map', 'False').lower()
                show_map = sheet_signed_up_value == 'true'

    # Filter strains
    if desired_state and desired_state in strain_data_df['Desired State'].unique().tolist():
        filtered_strains_df = strain_data_df[strain_data_df['Desired State'] == desired_state].head(5)
    else:
        filtered_strains_df = pd.DataFrame()

    if not filtered_strains_df.empty:
        for index, row in filtered_strains_df.iterrows():
            strains_for_template.append({
                'strain': row['Strain Name'],
                'score': f"{row['THC Score']}%" if pd.notna(row['THC Score']) else 'N/A'
            })
    else:
        strains_for_template.append({
            'strain': 'No strains found for this desired state or no selection made.',
            'score': ''
        })

    print(f"Rendering results.html with: Name={name}, Email={email}, Desired State={desired_state}, Show Map={show_map}")
    return render_template(
        'results.html',
        name=name,
        email=email,
        desired_state=desired_state,
        strains=strains_for_template,
        show_map=show_map,
        profile_picture_url=profile_picture_url
    )



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    email = request.args.get('email')
    message = ''
    default_picture = 'uploads/blank-profile-picture-973460_1280.webp'
    profile_picture_path = default_picture  # This will hold the relative path stored in the sheet
    user_name = "Guest"
    favorite_strain = ""

    if email and user_data_worksheet:
        row = find_user_row(email)
        if row:
            headers = user_data_worksheet.row_values(1)
            values = user_data_worksheet.row_values(row)
            user_data = dict(zip(headers, values))

            # Get stored favorite strain and profile picture if available
            favorite_strain = user_data.get('Favorite Strain', '')
            profile_picture_path = user_data.get('Profile Picture', default_picture)
            profile_picture_url = url_for('static', filename=profile_picture_path)

    if request.method == 'POST':
        # Update profile picture if a new one is uploaded
        file = request.files.get('profile_picture')
        if file and file.filename != '':
         upload_result = cloudinary.uploader.upload(file)
         profile_picture_url = upload_result['secure_url']  # HTTPS image URL

    # Save this URL into the Google Sheet
    if user_data_worksheet and email:
        row = find_user_row(email)
        if row:
            pic_col = get_column_index(user_data_worksheet, 'Profile Picture')
            if pic_col:
                user_data_worksheet.update_cell(row, pic_col, profile_picture_url)


        # Update favorite strain
        favorite_strain = request.form.get('favorite_strain')
        if user_data_worksheet and email:
            row = find_user_row(email)
            if row:
                fav_col = get_column_index(user_data_worksheet, 'Favorite Strain')
                if fav_col:
                    user_data_worksheet.update_cell(row, fav_col, favorite_strain)
                    message = "Profile updated!"


    # Final profile picture URL to use in the template
    if profile_picture_path.startswith('http'):
      profile_picture_url = profile_picture_path
    else:
      profile_picture_url = url_for('static', filename=profile_picture_path)


    return render_template(
        "profile.html",
        name=user_name,
        email=email,
        profile_picture_url=profile_picture_url,
        favorite_strain=favorite_strain,
        message=message
    )




    # PythonAnywhere manages running your Flask app. Remove or comment out this block.
    # if __name__ == '__main__':
    #     app.run(debug=True)










