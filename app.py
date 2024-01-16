import random
import streamlit as st 
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
from PIL import Image
import os
from io import BytesIO
import openai
from openai import OpenAI
import base64
import requests

import nltk
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")

nltk.download('punkt')

emotional_or_action_words = {
    'adventure', 'amazed', 'brave', 'caring', 'cheerful', 'courage', 'cry',
    'danger', 'discover', 'dream', 'escape', 'excited', 'fear', 'friend',
    'fun', 'funny', 'happy', 'help', 'hero', 'hide', 'joy', 'laugh', 'lonely',
    'lost', 'love', 'magic', 'mystery', 'play', 'protect', 'rescue', 'sad',
    'scared', 'search', 'surprise', 'treasure', 'trick', 'wish', 'wonder'
}

def build_matcher():
    matcher = Matcher(nlp.vocab)
    
    # Patterns for fairy tale elements
    patterns = [
        [{"POS": "NOUN"}, {"POS": "VERB"}],  # Simple noun-verb pairs
        [{"LEMMA": {"IN": ["find", "discover", "rescue", "escape", "reveal"]}}],  # Action verbs
        [{"LEMMA": {"IN": ["magic", "princess", "castle", "dragon", "witch", "fairy"]}}],  # Fairy tale nouns
        [{"POS": "ADJ"}, {"POS": "NOUN"}]  # Adjective-noun pairs (e.g., 'golden hair')
    ]
    for pattern in patterns:
        matcher.add("FAIRY_TALE_PATTERN", [pattern])
    return matcher

def clean_scene(scene): 
    scene = scene.replace("\n", " ").strip() 
    scene = scene.replace('"', " ").strip() 
    return scene

def extract_key_scenes(text, top_n=5):
    doc = nlp(text)
    matcher = build_matcher()
    matches = matcher(doc)

    # Extract sentences that contain matched patterns
    key_sentences = set()
    for match_id, start, end in matches:
        span = doc[start:end].sent  # Get the whole sentence that contains the match
        cleaned_scene = clean_scene(span.text)
        key_sentences.add(cleaned_scene)

    # Sort and select top_n sentences
    return sorted(list(key_sentences))[:top_n]

def create_descriptive_prompt(scenes):
    # List of adjectives and phrases to enrich the scenes
    descriptive_adjectives = ['enchanting', 'mysterious', 'serene', 'joyful', 'dramatic']
    sensory_phrases = ['under the twinkling stars', 'in the lush, green garden', 'by the sparkling river']
    emotional_phrases = ['with a sense of wonder', 'feeling brave and bold', 'with a heart full of hope']

    prompts = []
    for scene in scenes:
        # Randomly choose descriptors to add richness
        adjective = random.choice(descriptive_adjectives)
        sensory_detail = random.choice(sensory_phrases)
        emotional_detail = random.choice(emotional_phrases)

        # Create and return the prompt
        prompt = f"{adjective} scene of {scene} {sensory_detail}, {emotional_detail}."
        prompts.append(prompt)
    
    return prompts

openai.api_key = st.secrets["OPENAI_API_KEY"]


API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
headers = {"Authorization": f"""Bearer {st.secrets["HUGGING_FACE_API_TOKEN"]}"""}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.content

def generate_images(prompts):
    images =[]
    for prompt in prompts:
        image_bytes = query({ "inputs": f"{prompt}",})
        images.append(image_bytes)
    
    return images


def download_and_save_images(images):
    i = 1
    output_directory = "./images/"

    # Create the 'images' directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for image in images:
        try:
            output_filename = f"image_{i}.png"

            # Open the image using PIL
            img = Image.open(BytesIO(image))

            # Save the image as PNG in the 'images' directory
            img.save(os.path.join(output_directory, output_filename), 'PNG')

            print(f"Image saved as {output_filename}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        i += 1

def encode_image_to_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
#from diffusers import StableDiffusionPipeline
# import torch

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

#function to generate AI based images using OpenAI Dall-E

def display_example():
    story = """
    Once upon a time, in the kingdom of Enchantia, there lived a beautiful princess named Fiona. Fiona had long golden hair, sparkling blue eyes, and a heart filled with love for one thing in particular - cats. She adored everything about them, from their soft fur to their playful nature.

    Every day, Fiona would spend her time in the royal gardens, surrounded by a multitude of cats. They would purr and rub against her legs, making her giggle with joy. She would name each cat and spend hours playing and cuddling with them.

    One sunny morning, while Fiona was feeding her feline friends, she discovered a tiny, fluffy kitten hiding in the flower bushes. The poor little creature had been abandoned and was all alone. Fiona's heart ached with sadness for this little kitten.

    Without a second thought, Fiona scooped up the kitten and held her close. She could feel the tiny heartbeat and saw the fear in the kitten's eyes. Determined to provide a loving home, Fiona carried the kitten to the castle, seeking assistance from her parents, the king, and queen.

    When the king and queen saw the tearful princess holding the kitten, their hearts melted. They gave their approval for Fiona to keep the little furball and adopted her as a member of the royal household. Fiona named the kitten Daisy, and from that day on, they became inseparable.

    Daisy and Fiona spent their days exploring the castle corridors, chasing butterflies, and playing hide-and-seek. Daisy grew stronger and healthier under Fiona's loving care. The bond between them was so strong that they could communicate without words.

    One evening, a terrible storm swept through the kingdom. Thunder roared, and lightning streaked across the sky, filling the air with a sense of danger. Fiona, who was afraid of storms herself, found comfort in Daisy's presence. As Fiona clung to her precious feline friend, she whispered, "Don't be afraid, Daisy. I'll protect you, just like you protect me."

    As the storm raged on, the windows shook, and the rain poured heavily. Suddenly, a blinding bolt of lightning struck the castle, causing a fire to ignite in the tower. Panic flooded the kingdom, and people ran in all directions, seeking safety.

    Fiona, with Daisy in her arms, knew she had to do something. Filled with bravery and love, she ran towards the tower, saving those who were trapped. Her heart raced

    """
    key_scenes = ["As Fiona clung to her precious feline friend, she whispered,  Don't be afraid, Daisy.",
    'As the storm raged on, the windows shook, and the rain poured heavily.',
    'Daisy and Fiona spent their days exploring the castle corridors, chasing butterflies, and playing hide-and-seek.',
    'Determined to provide a loving home, Fiona carried the kitten to the castle, seeking assistance from her parents, the king, and queen.',
    'Fiona had long golden hair, sparkling blue eyes, and a heart filled with love for one thing in particular - cats.']

    images_paths = ['./images/image_1.png',
    './images/image_2.png',
    './images/image_3.png',
    './images/image_4.png',
    './images/image_5.png']
    

    #images_paths
    #key_scenes
    #story
        
    markdown_text = ""

    # Iterate through key scenes and images
    for scene, image_path in zip(key_scenes, images_paths):
        # Split the text at the key scene
        parts = story.split(scene, 1)
        markdown_text += parts[0]
        
        # Encode the image
        base64_image = encode_image_to_base64(image_path)

        # Insert the image tag
        markdown_text += f'<img src="data:image/png;base64,{base64_image}" style="width: 50%; margin-left: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 0.5px; transition: transform 0.3s ease, box-shadow 0.3s ease;">'

        # Add the scene text back
        markdown_text += scene

        # Update the story_text to the remaining part after the key scene
        story_text = parts[1] if len(parts) > 1 else ''

    # Add any remaining text after the last image
    markdown_text += story_text
    st.markdown(markdown_text, unsafe_allow_html=True)

def generate_images_using_openai(text):
    response = openai.Image.create(prompt= text, n=1, size="512x512")
    image_url = response['data'][0]['url']
    return image_url


#function to generate AI based images using Huggingface Diffusers
def generate_images_using_huggingface_diffusers(text):
    #pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    prompt = text
    image = pipe(prompt).images[0] 
    return image

#Streamlit Code
st.sidebar.info("🤖 Application settings 🤖")
sd1, sd2 = st.sidebar.columns(2)
lm = sd1.selectbox("Selec tmodel text for generation", ["GPT", "Lama", "Mistral"])
text2speech = st.sidebar.radio("Text to speech 👇", ["Actve", "Inactve"], horizontal=True)
st.sidebar.info("🏰 Fairy Tail  settings 🏰")
image_model = sd2.selectbox("Select model for image generation", ["Huggingface Diffusers","OpenJourney", "DALL-E"])
sd1, sd2 = st.sidebar.columns(2)
gender = sd1.radio("Select gender ", ["Boy", "Girl", "Diverse"], horizontal=True)
child_name = sd2.text_input(label="Enter child's name ",placeholder="Optional")
age = st.sidebar.select_slider(
    "Select kid's age",
    options=[1,2,3,4,5,6,7,8,9,10,11,12],value=5)
#text2speech_yes = sd1.checkbox( "Text to speech - actve")
#text2speech_no = sd2.checkbox( "Text to speech - inactve")

characters = st.sidebar.text_input(label="Which characters you want to be included ?", placeholder="Shrek, Cat in boots  ... ")
mood = st.sidebar.text_input(
    label="Mood (e.g. inspirational, funny, serious) (optional)",
    placeholder="inspirational",
)
client = OpenAI()
input_prompt = None

app_mode =option_menu(
        menu_title=None,
        options=['Main screen','About this app'],
        icons=['bi-house-fill','bi-info-square-fill'],
        orientation="horizontal"
    )

def generate_story(input_prompt,gender,age,characters,mood ):
    response = client.chat.completions.create(
  #model="gpt-4-1106-preview",
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": f"""You are a fairy tale teller;\nYou should generate a story based on a thses instructions:{input_prompt}.\nThe story should be no more than 500 words;\n Child's gender is {gender}, childs's age is {age}.\n 
      Make sure to use these characters {characters}. The mood of the story should be {mood}"""
    }
  ],
  temperature=1,
  max_tokens=1024,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
    content  = response.choices[0].message.content
    return content

if app_mode == 'Main screen':
    st.subheader("This is a Fairy Tale Generation App that uses AI to generates text and images from text prompt.")
    input_prompt = st.text_area(label="Enter a fairy tale description for generation", placeholder="A fairy tail about princess Freya ... ")

    if 'story_generated' not in st.session_state:
        st.session_state.story_generated = False


    if input_prompt is not None:
        if st.button("Generate Fairy Tail"):
            if gender and input_prompt and age and mood and characters:
                with st.spinner('Wait for it...'):
    
                    story = generate_story(input_prompt,gender,age,characters,mood )
                    key_scenes = extract_key_scenes(story)
                    prompts = create_descriptive_prompt(key_scenes)
                    images = generate_images(prompts)
                    download_and_save_images(images)
                    image_directory = "./images/"

                    # Initialize an empty list to store image paths
                    images_paths = []

                    # Check if the directory exists
                    if os.path.exists(image_directory) and os.path.isdir(image_directory):
                        # List all files in the directory
                        image_files = os.listdir(image_directory)

                        # Filter only image files (you can customize this to include specific file extensions)
                        image_files = [file for file in image_files if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]

                        # Create full paths for the image files and add them to the 'images' list
                        images_paths = [os.path.join(image_directory, file) for file in image_files]
                    else:
                        print(f"The directory '{image_directory}' does not exist.")

                    markdown_text = ""

                    # Iterate through key scenes and images
                    for scene, image_path in zip(key_scenes, images_paths):
                        # Split the text at the key scene
                        parts = story.split(scene, 1)
                        markdown_text += parts[0]
                        
                        # Encode the image
                        base64_image = encode_image_to_base64(image_path)

                        # Insert the image tag
                        markdown_text += f'<img src="data:image/png;base64,{base64_image}" style="width: 50%; margin-left: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 0.5px; transition: transform 0.3s ease, box-shadow 0.3s ease;">'

                        # Add the scene text back
                        markdown_text += scene

                        # Update the story_text to the remaining part after the key scene
                        story_text = parts[1] if len(parts) > 1 else ''

                    # Add any remaining text after the last image
                    markdown_text += story_text
                st.success("The story was generated ✅")
                st.markdown(markdown_text, unsafe_allow_html=True)
                #message = st.chat_message("assistant")
                #message.write(generate_story(input_prompt,gender,age,characters,mood ))
                #display_example()
                st.session_state.story_generated = True
                st.balloons()
                
                
            else:
                st.error("Some data is missing, check input options")
    if st.session_state.story_generated:
        if st.button("Delete the story",key="deleteButton"):
            st.session_state.story_generated = False
            st.write("The story has been deleted. ✅")
    
#     st.markdown(f"""
#         <p>Once upon a time, in the kingdom of Enchantia, there lived a beautiful princess named Fiona. Fiona had long golden hair, sparkling blue eyes, and a heart filled with love for one thing in particular - cats. She adored everything about them, from their soft fur to their playful nature.</p>
# <p>Every day, Fiona would spend her time in the royal gardens, surrounded by a multitude of cats. They would purr and rub against her legs, making her giggle with joy. She would name each cat and spend hours playing and cuddling with them.</p>
# <p>One sunny morning, while Fiona was feeding her feline friends, she discovered a tiny, fluffy kitten hiding in the flower bushes. The poor little creature had been abandoned and was all alone. Fiona's heart ached with sadness for this little kitten.</p>
# <p>Without a second thought, Fiona scooped up the kitten and held her close. She could feel the tiny heartbeat and saw the fear in the kitten's eyes. Determined to provide a loving home, Fiona carried the kitten to the castle, seeking assistance from her parents, the king, and queen.</p>
# <p>When the king and queen saw the tearful princess holding the kitten, their hearts melted. They gave their approval for Fiona to keep the little furball and adopted her as a member of the royal household. Fiona named the kitten Daisy, and from that day on, they became inseparable.</p>
# <p>Daisy and Fiona spent their days exploring the castle corridors, chasing butterflies, and playing hide-and-seek. Daisy grew stronger and healthier under Fiona's loving care. The bond between them was so strong that they could communicate without words.</p>
# <p>One evening, a terrible storm swept through the kingdom. Thunder roared, and lightning streaked across the sky, filling the air with a sense of danger. Fiona, who was afraid of storms herself, found comfort in Daisy's presence. As Fiona clung to her precious feline friend, she whispered, "Don't be afraid, Daisy. I'll protect you, just like you protect me."</p>
# <p>As the storm raged on, the windows shook, and the rain poured heavily. Suddenly, a blinding bolt of lightning struck the castle, causing a fire to ignite in the tower. Panic flooded the kingdom, and people ran in all directions, seeking safety.</p>
# <p>Fiona, with Daisy in her arms, knew she had to do something. Filled with bravery and love, she ran towards the tower, saving those who were trapped. Her heart raced</p>

# <img src="data:images/png;base64,{base64.b64encode(open('././images/image_1.png', "rb").read()).decode()}" 
#          style=
#          "width: 30%; margin-left: 20px;
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                 border-radius: 0.5px;
#                 transition: transform 0.3s ease, box-shadow 0.3s ease;">                  
# <img src="data:images/png;base64,{base64.b64encode(open('././images/image_2.png', "rb").read()).decode()}" 
#          style=
#          "width: 30%; margin-left: 20px;
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                 border-radius: 0.5px;
#                 transition: transform 0.3s ease, box-shadow 0.3s ease;">                  
# <img src="data:images/png;base64,{base64.b64encode(open('././images/image_3.png', "rb").read()).decode()}" 
#          style=
#          "width: 30%; margin-left: 20px;
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                 border-radius: 0.5px;
#                 transition: transform 0.3s ease, box-shadow 0.3s ease;">                  
# <img src="data:images/png;base64,{base64.b64encode(open('././images/image_4.png', "rb").read()).decode()}" 
#          style=
#          "width: 30%; margin-left: 20px;
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                 border-radius: 0.5px;
#                 transition: transform 0.3s ease, box-shadow 0.3s ease;">                  
# <img src="data:images/png;base64,{base64.b64encode(open('././images/image_5.png', "rb").read()).decode()}" 
#          style=
#          "width: 30%; margin-left: 20px;
#                 box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                 border-radius: 0.5px;
#                 transition: transform 0.3s ease, box-shadow 0.3s ease;">                  

#         """, unsafe_allow_html=True)
    
            #image_url = generate_images_using_openai(input_prompt)
            #st.image(image_url, caption="Generated by DALL-E")

# if choice == "Home":
#     st.title("AI Fairy Tale Generation App")
#     with st.expander("About the App"):
#         st.write("This is a Fairy Tale Generation App that uses AI to generates text and images from text prompt.")

# elif choice == "DALL-E":
#     st.subheader("Image generation using Open AI's DALL-E")
#     input_prompt = st.text_input("Enter your text prompt")
#     if input_prompt is not None:
#         if st.button("Generate Image"):
#             image_url = generate_images_using_openai(input_prompt)
#             st.image(image_url, caption="Generated by DALL-E")

# elif choice == "Huggingface Diffusers":
#     st.subheader("Image generation using Huggingface Diffusers")
#     input_prompt = st.text_input("Enter your text prompt")
#     if input_prompt is not None:
#         if st.button("Generate Image"):
#             image_output = generate_images_using_huggingface_diffusers(input_prompt)
#             st.info("Generating image.....")
#             st.success("Image Generated Successfully")
#             st.image(image_output, caption="Generated by Huggingface Diffusers")
