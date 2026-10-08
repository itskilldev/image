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
# GEMINI API KEY
# =========================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]

except Exception:
    st.error(
        "GEMINI_API_KEY is missing from Streamlit Secrets."
    )
    st.stop()


# =========================================================
# GEMINI CLIENT
# =========================================================

try:
    client = genai.Client(
        api_key=api_key
    )

except Exception as e:
    st.error(
        f"Failed to initialize Gemini client: "
        f"{type(e).__name__}: {e}"
    )
    st.stop()


# =========================================================
# SIDEBAR
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
    )

    # Start with 1K for reliable testing
    image_size = "1K"

    st.info(
        "Image generation is powered by the Gemini API."
    )

    st.caption(
        "Image size is currently fixed to 1K for faster generation."
    )


# =========================================================
# PROMPT
# =========================================================

prompt = st.text_area(
    "Describe the image you want",
    placeholder=(
        "A realistic road through green mountains, "
        "natural daylight, professional photography..."
    ),
    height=150,
)


# =========================================================
# GENERATE BUTTON
# =========================================================

if st.button(
    "✨ Generate Image",
    type="primary",
    use_container_width=True,
):

    # -----------------------------------------------------
    # CHECK PROMPT
    # -----------------------------------------------------

    if not prompt.strip():

        st.warning(
            "Please enter an image prompt."
        )

        st.stop()


    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status = st.status(
        "Starting image generation...",
        expanded=True,
    )


    try:

        # -------------------------------------------------
        # STEP 1
        # -------------------------------------------------

        status.write(
            "✅ Button clicked."
        )

        status.write(
            "⏳ Sending request to Gemini API..."
        )


        # -------------------------------------------------
        # STEP 2 - API REQUEST
        # -------------------------------------------------

        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",

            input=prompt.strip(),

            response_format={
                "type": "image",
                "aspect_ratio": aspect_ratio,
                "image_size": image_size,
            },
        )


        # -------------------------------------------------
        # STEP 3
        # -------------------------------------------------

        status.write(
            "✅ Gemini API response received."
        )


        # -------------------------------------------------
        # GET IMAGE OUTPUT
        # -------------------------------------------------

        output = getattr(
            interaction,
            "output_image",
            None,
        )


        # -------------------------------------------------
        # NO IMAGE
        # -------------------------------------------------

        if output is None:

            status.update(
                label="❌ No image returned",
                state="error",
            )

            st.error(
                "Gemini returned no output_image."
            )

            output_text = getattr(
                interaction,
                "output_text",
                None,
            )

            if output_text:

                st.write(
                    "API response:"
                )

                st.write(
                    output_text
                )

            else:

                st.write(
                    "Raw response:"
                )

                st.write(
                    interaction
                )

            st.stop()


        # -------------------------------------------------
        # CHECK IMAGE DATA
        # -------------------------------------------------

        if not getattr(
            output,
            "data",
            None,
        ):

            status.update(
                label="❌ Image data is empty",
                state="error",
            )

            st.error(
                "The API returned an empty image."
            )

            st.stop()


        # -------------------------------------------------
        # STEP 4
        # -------------------------------------------------

        status.write(
            "✅ Image data received."
        )

        status.write(
            "⏳ Decoding image..."
        )


        # -------------------------------------------------
        # BASE64 → BYTES
        # -------------------------------------------------

        raw = base64.b64decode(
            output.data
        )


        # -------------------------------------------------
        # BYTES → PIL IMAGE
        # -------------------------------------------------

        image = Image.open(
            BytesIO(raw)
        ).convert("RGB")


        # -------------------------------------------------
        # STEP 5
        # -------------------------------------------------

        status.write(
            "✅ Image decoded successfully."
        )


        # -------------------------------------------------
        # SAVE IN SESSION
        # -------------------------------------------------

        st.session_state[
            "generated_image"
        ] = image


        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        status.update(
            label="🎉 Image generated successfully!",
            state="complete",
        )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        status.update(
            label="❌ Image generation failed",
            state="error",
        )

        st.error(
            f"Error type: {type(e).__name__}"
        )

        st.error(
            f"Error message: {e}"
        )


# =========================================================
# DISPLAY GENERATED IMAGE
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

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=95,
    )

    st.download_button(
        label="⬇️ Download Image",
        data=buffer.getvalue(),
        file_name="generated_image.jpg",
        mime="image/jpeg",
        use_container_width=True,
    )
