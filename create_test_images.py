import google.generativeai as genai
import os
from PIL import Image
import io
import sys

def generate_image_from_prompt(prompt, model_name):
    """Generates an image from a text prompt using a specified model."""
    try:
        model = genai.GenerativeModel(model_name)
        # This is a speculative API call, as the model names and API behavior
        # for direct image generation in this manner are not standard.
        response = model.generate_content(prompt)

        # The response structure for image data is also speculative.
        # We check for common patterns where image data might be found.
        if hasattr(response, 'parts') and response.parts and hasattr(response.parts[0], 'blob') and response.parts[0].blob.mime_type.startswith('image/'):
            return response.parts[0].blob.data, None
        
        if hasattr(response, 'candidates') and response.candidates:
            content = response.candidates[0].content
            if content.parts:
                part = content.parts[0]
                if hasattr(part, 'blob') and part.blob.mime_type.startswith('image/'):
                    return part.blob.data, None
                if hasattr(part, 'text'):
                    return None, f"Model returned text instead of an image: '{part.text[:100]}...'"

        return None, "No image data found in the model's response."

    except Exception as e:
        return None, str(e)

def process_scene(scene_prompt, output_path, primary_model, fallback_model):
    """Tries to generate and save an image using a primary and a fallback model."""
    all_errors = []
    image_bytes = None
    
    # Try primary model
    image_bytes, error_msg = generate_image_from_prompt(scene_prompt, primary_model)
    if error_msg:
        all_errors.append(f"Primary model ({primary_model}) failed: {error_msg}")

    # If primary fails, try fallback
    if not image_bytes:
        image_bytes, error_msg = generate_image_from_prompt(scene_prompt, fallback_model)
        if error_msg:
            all_errors.append(f"Fallback model ({fallback_model}) failed: {error_msg}")
    
    if not image_bytes:
        print(f"Error creating file '{os.path.abspath(output_path)}': Could not generate image.")
        for err in all_errors:
            print(f"- {err}")
        return

    try:
        # Save the image to the specified path
        img = Image.open(io.BytesIO(image_bytes))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, 'PNG')
        
        file_size = os.path.getsize(output_path)
        print(f"RESULT: {os.path.abspath(output_path)} ({file_size} bytes)")

    except Exception as e:
        print(f"Error saving file to '{output_path}': {e}")


def main():
    """Main function to configure API and run image generation."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: The GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Google AI SDK: {e}", file=sys.stderr)
        sys.exit(1)

    # Define prompts, paths, and models as per the request
    negative_prompt = "No watermark, no text, no binary code, no letters, no signatures."
    
    prompt_a = f"a magical glowing golden pocket watch swinging gently, deep lavender misty background, cinematic soft light, hypnosis theme. {negative_prompt}"
    path_a = "D:/Entertainments/DevEnvironment/autovideo/assets/images/test_a.png"

    prompt_b = f"a cheerful cartoon stage magician pulling a fluffy white rabbit out of a black top hat, colorful confetti falling, bright theater stage. {negative_prompt}"
    path_b = "D:/Entertainments/DevEnvironment/autovideo/assets/images/test_b.png"
    
    primary_model_name = "gemini-2.5-flash-image"
    fallback_model_name = "gemini-2.0-flash-preview-image-generation"

    process_scene(prompt_a, path_a, primary_model_name, fallback_model_name)
    process_scene(prompt_b, path_b, primary_model_name, fallback_model_name)

if __name__ == "__main__":
    main()
