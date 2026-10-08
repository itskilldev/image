
import streamlit as st
import base64
from io import BytesIO
from google import genai
from PIL import Image

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide",
)

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
    color: #888;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🎨 AI Image Generator</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Create images from your prompts</div>',
    unsafe_allow_html=True,
)

# API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

with st.sidebar:
    st.header("⚙️ Settings")

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
    )

    image_size = st.selectbox(
        "Image Size",
        ["1K", "2K", "4K"],
    )

    st.info("Generation runs through the Gemini API.")

prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "A realistic road through green mountains, "
        "natural daylight, professional photography..."
    ),
    height=150,
)

if st.button(
    "✨ Generate Image",
    type="primary",
    use_container_width=True,
):
    if not prompt.strip():
        st.warning("Please enter an image prompt.")
    else:
        try:
            with st.spinner("Generating image..."):
                # First test the basic generation request.
                # Apply image settings after basic generation works.
                interaction = client.interactions.create(
                    model="gemini-3.1-flash-image",
                    input=prompt.strip(),
                    response_format={
                        "type": "image",
                        "aspect_ratio": aspect_ratio,
                        "image_size": image_size,
                    },
                )

                output = getattr(
                    interaction, "output_image", None
                )

                if not output or not output.data:
                    st.error("The API returned no image.")
                    output_text = getattr(
                        interaction, "output_text", None
                    )
                    if output_text:
                        st.write(output_text)
                else:
                    raw = base64.b64decode(output.data)
                    image = Image.open(BytesIO(raw)).convert("RGB")
                    st.session_state["generated_image"] = image

        except Exception as exc:
            st.error(
                f"Generation failed: {type(exc).__name__}: {exc}"
            )

if "generated_image" in st.session_state:
    image = st.session_state["generated_image"]

    st.subheader("Generated Image")
    st.image(image, use_container_width=True)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)

    st.download_button(
        "⬇️ Download Image",
        data=buffer.getvalue(),
        file_name="generated_image.jpg",
        mime="image/jpeg",
        use_container_width=True,
    )
