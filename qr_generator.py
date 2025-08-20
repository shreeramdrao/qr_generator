import streamlit as st
import qrcode
from PIL import Image
import io
import validators
from urllib.parse import urlparse

# Set page configuration
st.set_page_config(
    page_title="URL to QR Code Generator",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def validate_url(url):
    """Validate if the provided string is a valid URL"""
    if not url:
        return False, "Please enter a URL"
    
    # Add http:// if no scheme is provided
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Validate URL format
    if validators.url(url):
        return True, url
    else:
        return False, "Please enter a valid URL"

def generate_qr_code(url, error_correction_level='M', border_size=4, box_size=10):
    """Generate QR code for the given URL"""
    try:
        # Set error correction level
        error_correction_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,  # ~7%
            'M': qrcode.constants.ERROR_CORRECT_M,  # ~15%
            'Q': qrcode.constants.ERROR_CORRECT_Q,  # ~25%
            'H': qrcode.constants.ERROR_CORRECT_H   # ~30%
        }
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Controls size (1 is smallest)
            error_correction=error_correction_map[error_correction_level],
            box_size=box_size,
            border=border_size,
        )
        
        # Add data and generate QR code
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        return qr_image, None
    
    except Exception as e:
        return None, f"Error generating QR code: {str(e)}"

def convert_image_to_bytes(image):
    """Convert PIL image to bytes for download"""
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer.getvalue()

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">🔗 URL to QR Code Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Convert any URL into a QR code instantly</p>', unsafe_allow_html=True)
    
    # URL input section
    st.markdown("### 📝 Enter URL")
    url_input = st.text_input(
        "URL",
        placeholder="https://example.com or example.com",
        help="Enter any website URL. The http:// will be added automatically if missing.",
        label_visibility="collapsed"
    )
    
    # Advanced options in expander
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            error_correction = st.selectbox(
                "Error Correction Level",
                options=['L', 'M', 'Q', 'H'],
                index=1,
                help="Higher levels can recover from more damage but create larger QR codes"
            )
            
            box_size = st.slider(
                "Box Size",
                min_value=5,
                max_value=20,
                value=10,
                help="Size of each box in the QR code"
            )
        
        with col2:
            border_size = st.slider(
                "Border Size",
                min_value=1,
                max_value=10,
                value=4,
                help="Size of the border around the QR code"
            )
    
    # Generate button
    if st.button("🔄 Generate QR Code", type="primary", use_container_width=True):
        if url_input:
            # Validate URL
            is_valid, processed_url = validate_url(url_input.strip())
            
            if is_valid:
                # Generate QR code
                with st.spinner("Generating QR code..."):
                    qr_image, error = generate_qr_code(
                        processed_url, 
                        error_correction, 
                        border_size, 
                        box_size
                    )
                
                if qr_image and not error:
                    # Success message
                    st.markdown(
                        f'<div class="success-message">✅ QR code generated successfully for: <strong>{processed_url}</strong></div>',
                        unsafe_allow_html=True
                    )
                    
                    # Convert image to bytes for display and download
                    img_bytes = convert_image_to_bytes(qr_image)
                    
                    # Display QR code
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(img_bytes, caption="Generated QR Code", use_column_width=True)
                    
                    # Download button - using the same bytes
                    
                    # Create filename based on URL
                    parsed_url = urlparse(processed_url)
                    filename = f"qr_code_{parsed_url.netloc.replace('.', '_')}.png"
                    
                    st.download_button(
                        label="📥 Download QR Code",
                        data=img_bytes,
                        file_name=filename,
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # QR Code info
                    st.markdown("### ℹ️ QR Code Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Error Correction", error_correction)
                    with col2:
                        st.metric("Box Size", box_size)
                    with col3:
                        st.metric("Border Size", border_size)
                
                else:
                    st.markdown(
                        f'<div class="error-message">❌ {error}</div>',
                        unsafe_allow_html=True
                    )
            
            else:
                st.markdown(
                    f'<div class="error-message">❌ {processed_url}</div>',
                    unsafe_allow_html=True
                )
        
        else:
            st.markdown(
                '<div class="error-message">❌ Please enter a URL</div>',
                unsafe_allow_html=True
            )
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 How to Use")
    st.markdown("""
    1. **Enter URL**: Type or paste any website URL
    2. **Adjust Settings** (optional): Use advanced options to customize your QR code
    3. **Generate**: Click the generate button
    4. **Download**: Save the QR code image to your device
    
    **Error Correction Levels:**
    - **L (Low)**: ~7% - Smallest QR code
    - **M (Medium)**: ~15% - Balanced (recommended)
    - **Q (Quartile)**: ~25% - Good for noisy environments
    - **H (High)**: ~30% - Maximum error recovery
    """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">Made with ❤️ using Streamlit</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()