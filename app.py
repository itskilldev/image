import streamlit as st
import base64
from io import BytesIO
from google import genai
from PIL import Image


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #777;
    margin-bottom: 30px;
}

.generate-button {
    width: 100%;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# API KEY
# --------------------------------------------------

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()


# --------------------------------------------------
# GEMINI CLIENT
# --------------------------------------------------

client = genai.Client(api_key=API_KEY)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🎨 AI Image Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Create images from natural-language prompts</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        [
            "1:1",
            "16:9",
            "9:16",
            "4:3",
            "3:4"
        ]
    )

    image_size = st.selectbox(
        "Image Size",
        [
            "1K",
            "2K"
        ],
        index=0
    )

    st.divider()

    st.info(
        "Image generation is performed through the Gemini API. "
        "Your Streamlit server does not load a local diffusion model."
    )


# --------------------------------------------------
# PROMPT
# --------------------------------------------------

prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "Example: A photorealistic portrait of a young woman "
        "wearing an elegant traditional outfit, natural lighting, "
        "professional photography, detailed skin texture, "
        "shallow depth of field"
    ),
    height=150
)


# --------------------------------------------------
# GENERATE BUTTON
# --------------------------------------------------

generate = st.button(
    "✨ Generate Image",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# IMAGE GENERATION
# --------------------------------------------------

if generate:

    if not prompt.strip():
        st.warning("Please enter a prompt first.")
        st.stop()

    with st.spinner("Generating your image..."):

        try:

            interaction = client.interactions.create(
                model="gemini-3.1-flash-image",
                input=prompt,
                response_format={
                    "type": "image",
                    "mime_type": "image/png",
                    "aspect_ratio": aspect_ratio,
                    "image_size": image_size
                }
            )

            if interaction.output_image:

                image_data = base64.b64decode(
                    interaction.output_image.data
                )

                image = Image.open(
                    BytesIO(image_data)
                )

                st.session_state["generated_image"] = image

            else:

                st.error(
                    "The API did not return an image."
                )

        except Exception as e:

            st.error(
                f"Image generation failed: {str(e)}"
            )


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

if "generated_image" in st.session_state:

    st.subheader("Generated Image")

    image = st.session_state["generated_image"]

    st.image(
        image,
        use_container_width=True
    )

    # Convert image to PNG bytes
    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    st.download_button(
        label="⬇️ Download Image",
        data=buffer.getvalue(),
        file_name="generated_image.png",
        mime="image/png",
        use_container_width=True
    )