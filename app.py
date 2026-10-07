
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
            "2K",
            "4K"
        ],
        index=0
    )

    st.divider()

    st.info(
        "Images are generated through the Gemini API. "
        "The image-generation model does not run locally on your CPU."
    )


# --------------------------------------------------
# PROMPT
# --------------------------------------------------

prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "Example: A photorealistic portrait of a woman "
        "wearing an elegant traditional outfit, natural lighting, "
        "professional photography, realistic details, "
        "shallow depth of field."
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
                    "mime_type": "image/jpeg",
                    "aspect_ratio": aspect_ratio,
                    "image_size": image_size
                }
            )

            # Check whether an image was returned
            if interaction.output_image:

                # Decode Base64 image
                image_data = base64.b64decode(
                    interaction.output_image.data
                )

                # Open image
                image = Image.open(
                    BytesIO(image_data)
                )

                # Store in session
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
# DISPLAY GENERATED IMAGE
# --------------------------------------------------

if "generated_image" in st.session_state:

    st.subheader("Generated Image")

    image = st.session_state["generated_image"]

    st.image(
        image,
        use_container_width=True
    )


    # --------------------------------------------------
    # DOWNLOAD IMAGE
    # --------------------------------------------------

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=95
    )

    st.download_button(
        label="⬇️ Download Image",
        data=buffer.getvalue(),
        file_name="generated_image.jpg",
        mime="image/jpeg",
        use_container_width=True
    )
```
