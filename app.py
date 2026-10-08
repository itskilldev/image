import streamlit as st
import base64
from io import BytesIO
from google import genai
from PIL import Image


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎨 AI Image Generator</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Create images from your prompts</div>',
    unsafe_allow_html=True,
)


# =========================================================
# GET API KEY
# =========================================================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]

except Exception:
    st.error(
        "GEMINI_API_KEY is missing from Streamlit Secrets."
    )
    st.stop()


# =========================================================
# CREATE GEMINI CLIENT
# =========================================================

try:
    client = genai.Client(
        api_key=API_KEY
    )

except Exception as e:
    st.error(
        f"Gemini client error: {type(e).__name__}: {e}"
    )
    st.stop()


# =========================================================
# SIDEBAR SETTINGS
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        [
            "1:1",
            "16:9",
            "9:16",
            "4:3",
            "3:4",
        ],
        index=0,
    )

    st.info(
        "Powered by Gemini 3.1 Flash Image"
    )

    st.caption(
        "Generation quality: 1K"
    )


# =========================================================
# PROMPT
# =========================================================

prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "A realistic photograph of a beautiful "
        "mountain landscape during golden hour, "
        "natural lighting, highly detailed, "
        "professional photography"
    ),
    height=150,
)


# =========================================================
# GENERATE BUTTON
# =========================================================

generate = st.button(
    "✨ Generate Image",
    type="primary",
    use_container_width=True,
)


if generate:

    # -----------------------------------------------------
    # VALIDATE PROMPT
    # -----------------------------------------------------

    if not prompt.strip():

        st.warning(
            "Please enter an image prompt."
        )

        st.stop()


    # -----------------------------------------------------
    # GENERATION STATUS
    # -----------------------------------------------------

    with st.status(
        "Generating image...",
        expanded=True,
    ) as status:

        try:

            status.write(
                "Connecting to Gemini API..."
            )


            # -------------------------------------------------
            # GEMINI IMAGE GENERATION
            # -------------------------------------------------

            response = client.interactions.create(
                model="gemini-3.1-flash-image",
                input=prompt.strip(),
                response_format={
                    "type": "image",
                    "aspect_ratio": aspect_ratio,
                    "image_size": "1K",
                },
            )


            status.write(
                "Gemini response received."
            )


            # -------------------------------------------------
            # GET IMAGE
            # -------------------------------------------------

            output_image = getattr(
                response,
                "output_image",
                None,
            )


            if output_image is None:

                status.update(
                    label="❌ No image returned",
                    state="error",
                )

                output_text = getattr(
                    response,
                    "output_text",
                    None,
                )

                if output_text:
                    st.write(output_text)

                else:
                    st.write(response)

                st.stop()


            if not output_image.data:

                status.update(
                    label="❌ Empty image response",
                    state="error",
                )

                st.stop()


            # -------------------------------------------------
            # DECODE BASE64 IMAGE
            # -------------------------------------------------

            status.write(
                "Processing generated image..."
            )

            image_bytes = base64.b64decode(
                output_image.data
            )


            # -------------------------------------------------
            # CREATE PIL IMAGE
            # -------------------------------------------------

            image = Image.open(
                BytesIO(image_bytes)
            ).convert("RGB")


            # -------------------------------------------------
            # SAVE IMAGE IN SESSION
            # -------------------------------------------------

            st.session_state[
                "generated_image"
            ] = image


            status.update(
                label="✅ Image generated successfully!",
                state="complete",
            )


        except Exception as e:

            status.update(
                label="❌ Generation failed",
                state="error",
            )

            st.error(
                f"{type(e).__name__}: {e}"
            )


# =========================================================
# DISPLAY IMAGE
# =========================================================

if "generated_image" in st.session_state:

    image = st.session_state[
        "generated_image"
    ]


    st.divider()

    st.subheader(
        "🖼️ Generated Image"
    )


    st.image(
        image,
        use_container_width=True,
    )


    # =====================================================
    # DOWNLOAD
    # =====================================================

    download_buffer = BytesIO()

    image.save(
        download_buffer,
        format="JPEG",
        quality=95,
    )


    st.download_button(
        label="⬇️ Download Image",
        data=download_buffer.getvalue(),
        file_name="generated_image.jpg",
        mime="image/jpeg",
        use_container_width=True,
    )

