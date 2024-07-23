import streamlit as st
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel, Part
import vertexai
from PIL import Image
import base64
import io
import yaml

# Configuration (load from YAML file)
try:
  with open("config.yaml","r") as f:
    config = yaml.safe_load(f)
except FileNotFoundError:
  print("Error: config.yaml file not found. Using default values.")


project_id = config.get("project_id")
location = config.get("location")
dataset_id = config.get("dataset_id")
table_id = config.get("table_id")
pdf_file_uri = config.get("pdf_file_uri")
llm_model_name = config.get("llm_model_name")
background_image_location=config.get("background_image_location")


vertexai.init(project=project_id, location=location)

llm_model = GenerativeModel(llm_model_name)


# Sample Formula E Gen 3 info (replace with actual data retrieval)
gen3_car_info = {
    "model": "formula e gen 3",
    "height_mm": 1023.4,
    "width_mm": 1700,
    "length_mm": 5016.2,
    "wheelbase_mm": 2970.5,
    "weight_kg": 840,
    "power_hp": 350,
    "regeneration_kw": 600,
    "energy_recovery": "40%",
    "top_speed_mph": 200,
    "power_train": "front and rear",
}


def query_bigquery(make, model):
    """
    Returns:
        A dictionary containing car information or None if not found.
    """

    client = bigquery.Client(project=project_id)
    query = f"""
    SELECT YEAR, MAKE, MODEL, `VEHICLE CLASS`, ENGINE_SIZE, CYLINDERS, TRANSMISSION, FUEL AS FUEL_TYPE, FUEL_CONSUMPTION, CO2_EMISSIONS
    FROM `{project_id}.{dataset_id}.{table_id}`
    WHERE MAKE = '{make}' AND MODEL = '{model}'
    """
    query_job = client.query(query)
    results = query_job.result()

    if results:
        user_car_info = {}
        for row in results:
            for key, value in row.items():
                user_car_info[key] = value
        return user_car_info
    else:
        return None


def get_make_and_models():
    """Fetches distinct make and models from a BigQuery table.

    Returns:
        A list of tuples, where each tuple contains (make, models).
    """

    client = bigquery.Client(project=project_id)
    query = f"""
    #standardSQL
    SELECT DISTINCT MAKE, STRING_AGG(MODEL, ', ') AS MODELS
    FROM `{project_id}.{dataset_id}.{table_id}`
    GROUP BY MAKE
    """
    query_job = client.query(query)
    results = query_job.result()

    make_model_dict = {}
    for row in results:
        make_model_dict[row.MAKE] = row.MODELS.split(', ')
    
    make_list=make_model_dict.keys()

    return make_model_dict,make_list

car_model_options,make_list=get_make_and_models()


#st.title("Car Sustainability Comparison")
st.set_page_config(layout="wide")

def get_base64_of_image(img):
    with io.BytesIO() as buffer:
        img.save(buffer, 'PNG')
        return base64.b64encode(buffer.getvalue()).decode()

def set_page_background(img_file):
    img = Image.open(img_file)
    # Adjust image brightness if needed (e.g., using PIL's image enhancement functions)
    # img = enhance_brightness(img)  # Replace with your brightness adjustment function
    img_file_buffer = get_base64_of_image(img)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-repeat: no-repeat;
    background-position: center center;
    opacity: 0.85; /* Adjust opacity for light visibility */
    }
    </style>
    ''' % img_file_buffer
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_page_background(background_image_location)

st.markdown("<h1 style='text-align: center; color: green;'>Sustainability Face-off: Formula E Gen 3 vs. Your Vehicle</h1>", unsafe_allow_html=True)

# Car manufacturer selection
car_make = st.selectbox("Select Car Manufacturer",make_list )


if car_make != "Other":
    car_model = st.selectbox("Select Car Model", car_model_options[car_make])
else:
    car_model = st.text_input("Enter Car Model")

# Disable comparison button if no selection is made
if car_make and car_model:
    compare_button = st.button("Compare Sustainability")
else:
    compare_button = st.button("Compare Sustainability", disabled=True)

if compare_button:
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #c5e1a5;  /* Light green color */
    }
    </style>
    """, unsafe_allow_html=True)
    # Query BigQuery for user car information
    user_car_info = query_bigquery(car_make, car_model)

    if user_car_info:

        prompt = f"""
        Role: Cars Sustainability Metrics Analyst

        Task: Conduct a comparative sustainability analysis between the Formula E Gen 3 model and {car_make}, {car_model} car.

        Data: {gen3_car_info}

        Formula E Gen 3 car specification details below:

        {car_make} , {car_model} car specifications.
        Output: {user_car_info}

        Also formula e gen 3 sustanability pdf report is given in context

        Also calculate a sustainability score and give me percentage.

        A tabular comparison of only key sustainability metrics for both cars.
        A concise summary of the overall sustainability performance of each car, highlighting key differences and strengths.
        """

        pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
        contents = [pdf_file, prompt]
        responses = llm_model.generate_content(contents) 

        st.write(responses.text, unsafe_allow_html=True)

    else:
        st.error("Car information not found in BigQuery.")
