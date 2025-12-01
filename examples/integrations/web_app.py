#!/usr/bin/env python3
"""
Web Application Integration Example

This example demonstrates how to integrate the Venice AI SDK into a web application
using Flask. It includes chat, image generation, and audio synthesis features.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import base64
import json
from pathlib import Path
from venice_sdk import VeniceClient
from venice_sdk.errors import VeniceAPIError, UnauthorizedError


app = Flask(__name__)

# Environment-based configuration
ENVIRONMENT = os.getenv('FLASK_ENV', os.getenv('ENVIRONMENT', 'development')).lower()
IS_PRODUCTION = ENVIRONMENT in ('production', 'prod')

# Secret key configuration
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ValueError(
            "SECRET_KEY must be set for production deployment. "
            "Set it as an environment variable: export SECRET_KEY='your-secret-key'"
        )
    else:
        # Development: use random key
        SECRET_KEY = os.urandom(24)
        print("⚠️  WARNING: Using random SECRET_KEY for development. Set SECRET_KEY environment variable for production.")

app.secret_key = SECRET_KEY

# Initialize Venice AI client
client = VeniceClient()

# Create uploads directory
UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat completion endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', 'llama-3.3-70b')
        stream = data.get('stream', False)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        messages = [{"role": "user", "content": message}]
        
        if stream:
            # Streaming response
            def generate():
                for chunk in client.chat.complete_stream(
                    messages=messages,
                    model=model,
                    temperature=0.7
                ):
                    if chunk.startswith("data: "):
                        data_content = chunk[6:].strip()
                        if data_content == "[DONE]":
                            break
                        
                        try:
                            chunk_data = json.loads(data_content)
                            if "choices" in chunk_data and chunk_data["choices"]:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield f"data: {json.dumps({'content': delta['content']})}\n\n"
                        except json.JSONDecodeError:
                            pass
                
                yield "data: [DONE]\n\n"
            
            return app.response_class(
                generate(),
                mimetype='text/plain'
            )
        else:
            # Non-streaming response
            response = client.chat.complete(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=500
            )
            
            return jsonify({
                'response': response.choices[0].message.content,
                'model': model
            })
    
    except UnauthorizedError:
        return jsonify({'error': 'Authentication failed'}), 401
    except VeniceAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Image generation endpoint."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model = data.get('model', 'dall-e-3')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate image
        result = client.images.generate(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            response_format="b64_json"
        )
        
        if result.b64_json:
            # Return base64 encoded image
            return jsonify({
                'image': f"data:image/png;base64,{result.b64_json}",
                'model': model,
                'size': size
            })
        else:
            return jsonify({'error': 'No image generated'}), 500
    
    except VeniceAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/synthesize-speech', methods=['POST'])
def synthesize_speech():
    """Text-to-speech endpoint."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        voice = data.get('voice', 'alloy')
        format = data.get('format', 'mp3')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Generate audio
        audio = client.audio.speech(
            input_text=text,
            voice=voice,
            response_format=format
        )
        
        # Save to temporary file
        temp_path = UPLOAD_FOLDER / f"speech_{hash(text)}.{format}"
        audio.save(temp_path)
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"speech.{format}",
            mimetype=f"audio/{format}"
        )
    
    except VeniceAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/embeddings', methods=['POST'])
def generate_embeddings():
    """Embeddings generation endpoint."""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        model = data.get('model', 'text-embedding-bge-m3')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Texts array is required'}), 400
        
        # Generate embeddings
        embeddings = client.embeddings.generate(texts, model=model)
        
        # Convert to serializable format
        embeddings_data = []
        for i, embedding in enumerate(embeddings):
            embeddings_data.append({
                'index': i,
                'text': texts[i],
                'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding),
                'dimension': len(embedding)
            })
        
        return jsonify({
            'embeddings': embeddings_data,
            'model': model,
            'count': len(embeddings)
        })
    
    except VeniceAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models."""
    try:
        models = client.models.list()
        
        # Categorize models
        chat_models = []
        image_models = []
        audio_models = []
        embedding_models = []
        
        for model in models:
            model_id = model.get('id', '')
            model_spec = model.get('model_spec', {})
            model_type = model_spec.get('type', 'unknown')
            
            if 'chat' in model_id.lower() or 'llm' in model_id.lower():
                chat_models.append({
                    'id': model_id,
                    'name': model_spec.get('name', model_id),
                    'type': model_type
                })
            elif 'dall' in model_id.lower() or 'image' in model_id.lower():
                image_models.append({
                    'id': model_id,
                    'name': model_spec.get('name', model_id),
                    'type': model_type
                })
            elif 'tts' in model_id.lower() or 'audio' in model_id.lower():
                audio_models.append({
                    'id': model_id,
                    'name': model_spec.get('name', model_id),
                    'type': model_type
                })
            elif 'embedding' in model_id.lower():
                embedding_models.append({
                    'id': model_id,
                    'name': model_spec.get('name', model_id),
                    'type': model_type
                })
        
        return jsonify({
            'chat_models': chat_models,
            'image_models': image_models,
            'audio_models': audio_models,
            'embedding_models': embedding_models
        })
    
    except VeniceAPIError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/account', methods=['GET'])
def get_account_info():
    """Get account information (admin only)."""
    try:
        # Get account summary
        summary = client.account.get_account_summary()
        
        return jsonify({
            'summary': summary,
            'has_admin_access': 'api_keys' in summary
        })
    
    except UnauthorizedError:
        return jsonify({'error': 'Admin API key required'}), 401
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# HTML Templates
def create_templates():
    """Create HTML templates for the web app."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Main template
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Venice AI Web App</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .section h2 {
            color: #555;
            margin-top: 0;
        }
        input, textarea, select, button {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .response {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
            white-space: pre-wrap;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .image-result {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin-top: 10px;
        }
        .loading {
            display: none;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Venice AI Web Application</h1>
        
        <!-- Chat Section -->
        <div class="section">
            <h2>💬 Chat</h2>
            <textarea id="chatMessage" placeholder="Enter your message..." rows="3"></textarea>
            <select id="chatModel">
                <option value="llama-3.3-70b">Llama 3.3 70B</option>
                <option value="llama-3.3-8b">Llama 3.3 8B</option>
                <option value="gpt-4o-mini">GPT-4o Mini</option>
            </select>
            <button onclick="sendChat()">Send Message</button>
            <div id="chatResponse" class="response" style="display: none;"></div>
            <div id="chatLoading" class="loading">Sending message...</div>
        </div>
        
        <!-- Image Generation Section -->
        <div class="section">
            <h2>🎨 Image Generation</h2>
            <input type="text" id="imagePrompt" placeholder="Describe the image you want to generate...">
            <select id="imageModel">
                <option value="dall-e-3">DALL-E 3</option>
                <option value="stable-diffusion-3.5">Stable Diffusion 3.5</option>
            </select>
            <select id="imageSize">
                <option value="1024x1024">1024x1024</option>
                <option value="1792x1024">1792x1024</option>
                <option value="1024x1792">1024x1792</option>
            </select>
            <button onclick="generateImage()">Generate Image</button>
            <div id="imageResponse" class="response" style="display: none;"></div>
            <div id="imageLoading" class="loading">Generating image...</div>
        </div>
        
        <!-- Audio Synthesis Section -->
        <div class="section">
            <h2>🎵 Text-to-Speech</h2>
            <textarea id="audioText" placeholder="Enter text to convert to speech..." rows="3"></textarea>
            <select id="audioVoice">
                <option value="alloy">Alloy</option>
                <option value="echo">Echo</option>
                <option value="fable">Fable</option>
                <option value="onyx">Onyx</option>
                <option value="nova">Nova</option>
                <option value="shimmer">Shimmer</option>
            </select>
            <button onclick="synthesizeSpeech()">Generate Speech</button>
            <div id="audioResponse" class="response" style="display: none;"></div>
            <div id="audioLoading" class="loading">Generating speech...</div>
        </div>
        
        <!-- Embeddings Section -->
        <div class="section">
            <h2>🔗 Text Embeddings</h2>
            <textarea id="embeddingTexts" placeholder="Enter texts (one per line)..." rows="4"></textarea>
            <button onclick="generateEmbeddings()">Generate Embeddings</button>
            <div id="embeddingResponse" class="response" style="display: none;"></div>
            <div id="embeddingLoading" class="loading">Generating embeddings...</div>
        </div>
    </div>

    <script>
        async function sendChat() {
            const message = document.getElementById('chatMessage').value;
            const model = document.getElementById('chatModel').value;
            const responseDiv = document.getElementById('chatResponse');
            const loadingDiv = document.getElementById('chatLoading');
            
            if (!message.trim()) {
                showError(responseDiv, 'Please enter a message');
                return;
            }
            
            showLoading(loadingDiv);
            hideResponse(responseDiv);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message, model })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showSuccess(responseDiv, data.response);
                } else {
                    showError(responseDiv, data.error);
                }
            } catch (error) {
                showError(responseDiv, 'Network error: ' + error.message);
            } finally {
                hideLoading(loadingDiv);
            }
        }
        
        async function generateImage() {
            const prompt = document.getElementById('imagePrompt').value;
            const model = document.getElementById('imageModel').value;
            const size = document.getElementById('imageSize').value;
            const responseDiv = document.getElementById('imageResponse');
            const loadingDiv = document.getElementById('imageLoading');
            
            if (!prompt.trim()) {
                showError(responseDiv, 'Please enter a prompt');
                return;
            }
            
            showLoading(loadingDiv);
            hideResponse(responseDiv);
            
            try {
                const response = await fetch('/api/generate-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt, model, size })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const img = document.createElement('img');
                    img.src = data.image;
                    img.className = 'image-result';
                    responseDiv.innerHTML = '';
                    responseDiv.appendChild(img);
                    showResponse(responseDiv);
                } else {
                    showError(responseDiv, data.error);
                }
            } catch (error) {
                showError(responseDiv, 'Network error: ' + error.message);
            } finally {
                hideLoading(loadingDiv);
            }
        }
        
        async function synthesizeSpeech() {
            const text = document.getElementById('audioText').value;
            const voice = document.getElementById('audioVoice').value;
            const responseDiv = document.getElementById('audioResponse');
            const loadingDiv = document.getElementById('audioLoading');
            
            if (!text.trim()) {
                showError(responseDiv, 'Please enter text');
                return;
            }
            
            showLoading(loadingDiv);
            hideResponse(responseDiv);
            
            try {
                const response = await fetch('/api/synthesize-speech', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text, voice })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const audio = document.createElement('audio');
                    audio.controls = true;
                    audio.src = url;
                    responseDiv.innerHTML = '';
                    responseDiv.appendChild(audio);
                    showSuccess(responseDiv, 'Audio generated successfully!');
                } else {
                    const data = await response.json();
                    showError(responseDiv, data.error);
                }
            } catch (error) {
                showError(responseDiv, 'Network error: ' + error.message);
            } finally {
                hideLoading(loadingDiv);
            }
        }
        
        async function generateEmbeddings() {
            const texts = document.getElementById('embeddingTexts').value.split('\\n').filter(t => t.trim());
            const responseDiv = document.getElementById('embeddingResponse');
            const loadingDiv = document.getElementById('embeddingLoading');
            
            if (texts.length === 0) {
                showError(responseDiv, 'Please enter at least one text');
                return;
            }
            
            showLoading(loadingDiv);
            hideResponse(responseDiv);
            
            try {
                const response = await fetch('/api/embeddings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ texts })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    let result = `Generated ${data.count} embeddings:\\n\\n`;
                    data.embeddings.forEach((emb, i) => {
                        result += `${i + 1}. "${emb.text}"\\n`;
                        result += `   Dimension: ${emb.dimension}\\n\\n`;
                    });
                    showSuccess(responseDiv, result);
                } else {
                    showError(responseDiv, data.error);
                }
            } catch (error) {
                showError(responseDiv, 'Network error: ' + error.message);
            } finally {
                hideLoading(loadingDiv);
            }
        }
        
        function showLoading(element) {
            element.style.display = 'block';
        }
        
        function hideLoading(element) {
            element.style.display = 'none';
        }
        
        function showResponse(element) {
            element.style.display = 'block';
        }
        
        function hideResponse(element) {
            element.style.display = 'none';
        }
        
        function showSuccess(element, message) {
            element.className = 'response success';
            element.textContent = message;
            showResponse(element);
        }
        
        function showError(element, message) {
            element.className = 'response error';
            element.textContent = message;
            showResponse(element);
        }
    </script>
</body>
</html>
    """
    
    (templates_dir / "index.html").write_text(index_html)


def validate_production_config():
    """Validate configuration for production deployment."""
    warnings = []
    errors = []
    
    # Check debug mode
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    if IS_PRODUCTION and debug_mode:
        errors.append(
            "DEBUG mode is enabled in production! This is a security risk. "
            "Set FLASK_DEBUG=false or remove it from environment variables."
        )
    
    # Check host configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    if IS_PRODUCTION and host == '0.0.0.0':
        warnings.append(
            "Host is set to '0.0.0.0' which allows connections from any IP. "
            "In production, consider using a specific host or a reverse proxy."
        )
    
    # Check secret key
    if IS_PRODUCTION and not os.getenv('SECRET_KEY'):
        errors.append(
            "SECRET_KEY is not set! This is required for production. "
            "Set it as an environment variable: export SECRET_KEY='your-secret-key'"
        )
    elif IS_PRODUCTION and os.getenv('SECRET_KEY') == 'dev-secret-key':
        errors.append(
            "SECRET_KEY is set to 'dev-secret-key' which is not suitable for production! "
            "Use a strong, randomly generated secret key."
        )
    
    # Display warnings and errors
    if warnings:
        print("\n⚠️  PRODUCTION WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if errors:
        print("\n❌ PRODUCTION CONFIGURATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        print("\n⚠️  The application will not start in production with these errors.")
        raise ValueError("Production configuration validation failed. See errors above.")
    
    if IS_PRODUCTION and not warnings and not errors:
        print("✅ Production configuration validated successfully")


def main():
    """Run the web application."""
    print("🌐 Starting Venice AI Web Application...")
    print(f"📋 Environment: {ENVIRONMENT}")
    
    # Validate production configuration
    if IS_PRODUCTION:
        validate_production_config()
    
    # Create templates
    create_templates()
    
    # Check for API key
    if not os.getenv("VENICE_API_KEY"):
        print("❌ Error: VENICE_API_KEY environment variable not set")
        print("Please set your API key: export VENICE_API_KEY='your-key-here'")
        return
    
    print("✅ API key found")
    print("🚀 Starting Flask server...")
    
    # Configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'true' if not IS_PRODUCTION else 'false').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0' if not IS_PRODUCTION else '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    if IS_PRODUCTION and debug_mode:
        print("⚠️  WARNING: DEBUG mode is enabled in production! This is a security risk.")
        print("   Set FLASK_DEBUG=false to disable debug mode.")
    
    if IS_PRODUCTION and host == '0.0.0.0':
        print("⚠️  WARNING: Host is set to '0.0.0.0' which allows connections from any IP.")
        print("   Consider using a specific host or a reverse proxy in production.")
    
    print(f"📱 Open your browser to: http://{host}:{port}")
    
    # Run the Flask app
    app.run(debug=debug_mode, host=host, port=port)


if __name__ == "__main__":
    main()
