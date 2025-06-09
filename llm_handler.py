import google.generativeai as genai
from typing import Dict, Any, Optional, Tuple, NamedTuple
import logging
import os
import base64
import requests
import time
from dotenv import load_dotenv

class GenerationResult(NamedTuple):
    """Result of story and image prompt generation."""
    story: str
    image_prompt: str
    model_name: str
    input_tokens: int
    output_tokens: int

class ImageGenerationResult(NamedTuple):
    """Result of image generation."""
    image_data: str
    model_name: str
    prompt_used: str
    generation_time_ms: float

class LLMHandler:
    def __init__(self, config_loader):
        """Initialize the LLM handler.
        
        Args:
            config_loader: Instance of ConfigLoader for accessing configuration
        """
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.api_key = None
        self.current_model_name = None
        self._initialize_model()
        
    def _initialize_model(self) -> bool:
        """Initialize the Gemini model.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get API key from environment variable or prompt user
            load_dotenv()
            self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            print("Loaded Gemini API key:", self.api_key)
            if not self.api_key:
                self.logger.error("No API key provided")
                return False
                
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Get model configuration
            self.current_model_name = self.config_loader.get_config('model_name', 'gemini-1.5-flash-latest')
            temperature = self.config_loader.get_config('llm.temperature', 0.7)
            top_p = self.config_loader.get_config('llm.top_p', 0.95)
            top_k = self.config_loader.get_config('llm.top_k', 40)
            max_output_tokens = self.config_loader.get_config('max_output_tokens', 2500)
            
            # Initialize model with safety settings
            self.model = genai.GenerativeModel(
                self.current_model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_output_tokens=max_output_tokens
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": self.config_loader.get_config('safety.harassment_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": self.config_loader.get_config('safety.hate_speech_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": self.config_loader.get_config('safety.sexually_explicit_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": self.config_loader.get_config('safety.dangerous_content_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    }
                ]
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Gemini model: {e}")
            return False
            
    def generate_story_and_image_prompt(
        self,
        user_story_prompt: str,
        persona_context: str,
        image_prompt_guidelines: str,
        character_name: str
    ) -> GenerationResult:
        """Generate a story and image prompt using the Gemini model.
        
        Args:
            user_story_prompt (str): User's story idea
            persona_context (str): Relevant persona context
            image_prompt_guidelines (str): Guidelines for image prompt generation
            character_name (str): Name of the character being used
            
        Returns:
            GenerationResult: Named tuple with story, image_prompt, model_name, and token counts
        """
        if not self.model:
            return GenerationResult(
                story="Error: Model not initialized", 
                image_prompt="Error: Model not initialized",
                model_name=self.current_model_name or "unknown",
                input_tokens=0,
                output_tokens=0
            )
            
        try:
            prompt = f"""**আপনার ভূমিকা (Your Role):**
আপনি "{character_name}" এর পারসোনা ধারণকারী একজন অত্যন্ত প্রতিভাবান এবং সৃজনশীল গল্পকার। আপনার লেখার প্রতিটি শব্দে যেন {character_name} এর নির্লিপ্ততা, পর্যবেক্ষণ ক্ষমতা, কৌতুকবোধ এবং দার্শনিক দৃষ্টিভঙ্গি ফুটে ওঠে।

**কঠোর নির্দেশাবলী (Strict Instructions):**

1.  **গল্পের মূল কেন্দ্রবিন্দু (Core Focus of the Story):** আপনার গল্পের প্রধান উপজীব্য হবে ব্যবহারকারীর দেওয়া "গল্পের মূল ধারণা" (User's Story Idea)। এই ধারণাকে কেন্দ্র করেই সম্পূর্ণ নতুন একটি গল্প তৈরি করুন।
2.  **{character_name} এর চরিত্রায়ণ ({character_name}'s Characterization):** প্রদত্ত "প্রাসঙ্গিক তথ্য ({character_name} এর পারসোনা)" অংশ থেকে {character_name} এর চারিত্রিক বৈশিষ্ট্য, মানসিক গঠন, জীবনদর্শন, আচরণ এবং বাচনভঙ্গি গভীরভাবে আত্মস্থ করুন। গল্পে {character_name} এর প্রতিটি কথা, কাজ এবং চিন্তা যেন তার পারসোনার সাথে সম্পূর্ণ সঙ্গতিপূর্ণ হয়।
3.  **সংলাপ ও বর্ণনা (Dialogue and Narrative):** গল্পটি {character_name} এর নিজস্ব জবানিতে (first-person narrative) অথবা এমনভাবে লিখুন যেন পাঠক {character_name} এর চিন্তার জগতের অংশ হয়ে যায়।
4.  **কপি করবেন না (Strictly No Copying):** "প্রাসঙ্গিক তথ্য ({character_name} এর পারসোনা)" বা "ইমেজ প্রম্পট তৈরির নির্দেশিকা" থেকে কোনো বাক্য, অনুচ্ছেদ বা গল্পের অংশ সরাসরি আপনার নতুন গল্প বা ইমেজ প্রম্পটে **কপি করা যাবে না**। এগুলো শুধুমাত্র ধারণা ও ভঙ্গি বোঝার জন্য। আপনাকে একটি **সম্পূর্ণ মৌলিক ও নতুন** গল্প এবং তার জন্য একটি **সম্পূর্ণ মৌলিক ও নতুন** ইমেজ প্রম্পট তৈরি করতে হবে।
5.  **সমন্বয় (Integration):** ব্যবহারকারীর দেওয়া "গল্পের মূল ধারণা"র সাথে {character_name} এর পারসোনা ও তার জগৎকে সৃজনশীলভাবে সমন্বয় ঘটান।
6.  **ভাষা (Language):** গল্পটি অবশ্যই প্রাঞ্জল, সাহিত্যিক মানসম্পন্ন বাংলায় লিখতে হবে।
7.  **অপ্রাসঙ্গিকতা পরিহার (Avoid Irrelevance):** যদি গল্প তৈরির মতো যথেষ্ট উপাদান না থাকে, তবে একটি সংক্ষিপ্ত, {character_name} সুলভ রহস্যময় মন্তব্য করুন।

---
**প্রাসঙ্গিক তথ্য ({character_name} এর পারসোনা, লেখার সাধারণ ধরণ, টাইমলাইন ইত্যাদি):**
{persona_context}
---

**ইমেজ প্রম্পট তৈরির নির্দেশিকা (Guidelines for Image Prompt Generation):**
{image_prompt_guidelines}
---

**গল্পের মূল ধারণা (User's Story Idea - এই অংশটির উপর বিশেষভাবে নজর দিন এবং এটিকে কেন্দ্র করে সম্পূর্ণ নতুন একটি "{character_name}" গল্প তৈরি করুন):**
{user_story_prompt}
---

**আপনার কাজ (Your Task):**

**প্রথম ধাপ:** উপরের কঠোর নির্দেশাবলী এবং {character_name} এর পারসোনা অনুসরণ করে, "গল্পের মূল ধারণা" টিকে কেন্দ্র করে একটি সম্পূর্ণ নতুন, বিস্তারিত, সৃজনশীল এবং সাহিত্যমান সমৃদ্ধ বাংলা গল্প তৈরি করুন।

**দ্বিতীয় ধাপ:** গল্পটি তৈরি করার পর, গল্পের বিষয়বস্তু, চরিত্র, পরিবেশ, এবং আবেগের উপর ভিত্তি করে, প্রদত্ত "ইমেজ প্রম্পট তৈরির নির্দেশিকা" অনুসরণ করে, সেই গল্পের জন্য একটি **অত্যন্ত বিস্তারিত এবং সৃজনশীল "ইমেজ জেনারেশন প্রম্পট"** তৈরি করুন। এই ইমেজ প্রম্পটটি এমনভাবে লিখুন যেন এটি একটি ভিজ্যুয়াল আর্টিস্টকে (এআই) গল্পের মূল দৃশ্যপট ফুটিয়ে তুলতে সাহায্য করে। এই ইমেজ প্রম্পটটি অবশ্যই "গল্পের জন্য ইমেজ জেনারেশন প্রম্পট (অতি বিস্তারিত):" এই শিরোনাম দিয়ে শুরু করতে হবে এবং এটি হবে আপনার উত্তরের **শেষ অংশ**।

অনুগ্রহ করে গল্প এবং তারপর ইমেজ জেনারেশন প্রম্পটটি নিচে দিন।
"""
            
            response = self.model.generate_content(prompt)
            
            if not response.parts:
                return GenerationResult(
                    story="Error: No response from model", 
                    image_prompt="Error: No response from model",
                    model_name=self.current_model_name or "unknown",
                    input_tokens=0,
                    output_tokens=0
                )
                
            generated_text = response.text
            
            # Extract token usage information
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
            
            story_part = ""
            image_prompt_part = ""
            
            # Split the response into story and image prompt
            image_prompt_marker = "গল্পের জন্য ইমেজ জেনারেশন প্রম্পট (অতি বিস্তারিত):"
            if image_prompt_marker in generated_text:
                parts = generated_text.split(image_prompt_marker, 1)
                story_part = parts[0].strip()
                if len(parts) > 1:
                    image_prompt_part = parts[1].strip()
            else:
                story_part = generated_text.strip()
                image_prompt_part = "Error: Could not find image prompt section"
                
            return GenerationResult(
                story=story_part,
                image_prompt=image_prompt_part,
                model_name=self.current_model_name or "unknown",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            self.logger.error(error_msg)
            return GenerationResult(
                story=error_msg, 
                image_prompt=error_msg,
                model_name=self.current_model_name or "unknown",
                input_tokens=0,
                output_tokens=0
            ) 

    def reinitialize_with_new_api_key(self) -> bool:
        """Reinitialize the LLM handler with a new API key from environment.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Reload environment variables to get updated API key
            load_dotenv(override=True)  # override=True forces reload
            new_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            
            if not new_api_key:
                self.logger.error("No API key found in environment")
                return False
                
            if new_api_key == self.api_key:
                self.logger.info("API key unchanged, no reinitalization needed")
                return True
                
            self.logger.info("Reinitializing LLM handler with new API key")
            self.api_key = new_api_key
            
            # Reconfigure Gemini with new API key
            genai.configure(api_key=self.api_key)
            
            # Reinitialize model (this will use the new API key)
            model_name = self.config_loader.get_config('model_name', 'gemini-1.5-flash-latest')
            temperature = self.config_loader.get_config('llm.temperature', 0.7)
            top_p = self.config_loader.get_config('llm.top_p', 0.95)
            top_k = self.config_loader.get_config('llm.top_k', 40)
            max_output_tokens = self.config_loader.get_config('max_output_tokens', 2500)
            
            self.current_model_name = model_name
            self.model = genai.GenerativeModel(
                model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_output_tokens=max_output_tokens
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": self.config_loader.get_config('safety.harassment_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": self.config_loader.get_config('safety.hate_speech_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": self.config_loader.get_config('safety.sexually_explicit_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": self.config_loader.get_config('safety.dangerous_content_threshold', "BLOCK_MEDIUM_AND_ABOVE")
                    }
                ]
            )
            
            self.logger.info("LLM handler successfully reinitialized with new API key")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reinitializing LLM handler: {e}")
            return False

    def generate_image(self, prompt: str, quality: str = "high", size: str = "1024x1024") -> ImageGenerationResult:
        """Generate an image using Pollinations.ai with Flux.1-dev model.
        
        Args:
            prompt (str): The image generation prompt
            quality (str): Quality setting (standard, high, ultra)
            size (str): Image size (512x512, 1024x1024, 1024x1792)
            
        Returns:
            ImageGenerationResult: Named tuple with image data and metadata
        """
        start_time = time.time()
        
        try:
            # Enhanced prompt processing for better quality with Flux.1-dev
            enhanced_prompt = self._enhance_flux_prompt(prompt, quality)
            self.logger.info(f"Generating image with Pollinations.ai Flux.1-dev: {enhanced_prompt[:100]}...")
            self.logger.info(f"Settings: quality={quality}, size={size}")
            
            # Try Pollinations.ai with Flux.1-dev model
            image_data = self._generate_with_pollinations_flux(enhanced_prompt, quality, size)
            
            if image_data:
                generation_time = (time.time() - start_time) * 1000
                self.logger.info(f"Successfully generated image using Pollinations.ai Flux.1-dev")
                
                return ImageGenerationResult(
                    image_data=image_data,
                    model_name="pollinations-flux-1-dev",
                    prompt_used=enhanced_prompt,
                    generation_time_ms=generation_time
                )
            
            # Fallback to enhanced placeholder if service fails
            return self._generate_enhanced_placeholder(prompt, quality, size, start_time)
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            return self._generate_enhanced_placeholder(prompt, quality, size, start_time)

    def _enhance_flux_prompt(self, prompt: str, quality: str) -> str:
        """Enhance prompts specifically for Flux.1-dev model for better results."""
        
        # Quality-specific enhancements for Flux.1-dev
        quality_terms = {
            "standard": "detailed, clear, well-composed",
            "high": "high quality, detailed, professional, sharp focus, 8k resolution",
            "ultra": "masterpiece, ultra high quality, extremely detailed, professional photography, 8k resolution, award-winning, cinematic masterpiece, hyperrealistic, perfect composition"
        }
        
        # Flux.1-dev specific style enhancements based on quality
        if quality == "ultra":
            flux_enhancers = [
                "photorealistic",
                "cinematic lighting", 
                "detailed textures",
                "vibrant colors",
                "sharp focus",
                "professional composition",
                "studio lighting",
                "perfect exposure",
                "highly detailed"
            ]
        elif quality == "high":
            flux_enhancers = [
                "photorealistic",
                "cinematic lighting", 
                "detailed textures",
                "vibrant colors",
                "sharp focus",
                "professional composition"
            ]
        else:
            flux_enhancers = [
                "photorealistic",
                "good lighting", 
                "detailed",
                "clear focus"
            ]
        
        # Build enhanced prompt
        enhanced = f"{quality_terms.get(quality, quality_terms['high'])}, "
        
        # Add more enhancers for ultra quality
        if quality == "ultra":
            enhanced += f"{', '.join(flux_enhancers[:6])}, "
        else:
            enhanced += f"{', '.join(flux_enhancers[:3])}, "
            
        enhanced += prompt
        
        # Add quality-specific endings
        if quality == "ultra":
            enhanced += ", highly detailed, best quality, professional grade, museum quality"
        elif quality == "high":
            enhanced += ", highly detailed, best quality"
        else:
            enhanced += ", detailed, good quality"
        
        return enhanced

    def _generate_with_pollinations_flux(self, prompt: str, quality: str, size: str) -> Optional[str]:
        """Generate image using Pollinations.ai with Flux.1-dev model."""
        try:
            # Pollinations.ai API with Flux.1-dev model
            # Parse size for API
            width, height = size.split('x')
            
            # Pollinations.ai endpoint with Flux.1-dev
            url = "https://image.pollinations.ai/prompt/"
            
            # URL encode the prompt and add Flux.1-dev specific parameters
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Construct the full URL with Flux.1-dev parameters
            full_url = f"{url}{encoded_prompt}?model=flux&width={width}&height={height}&enhance=true"
            
            # Add quality-specific parameters
            if quality == "ultra":
                full_url += "&steps=50&cfg=7.5"
            elif quality == "high": 
                full_url += "&steps=30&cfg=7.0"
            else:
                full_url += "&steps=20&cfg=6.5"
            
            self.logger.info(f"Calling Pollinations.ai Flux.1-dev API: {full_url[:150]}...")
            
            # Make request with timeout
            response = requests.get(full_url, timeout=60)
            
            if response.status_code == 200:
                # Convert image to base64
                image_data = base64.b64encode(response.content).decode('utf-8')
                self.logger.info(f"Pollinations.ai Flux.1-dev response: {len(image_data)} characters")
                return image_data
            else:
                self.logger.error(f"Pollinations.ai Flux.1-dev API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Pollinations.ai Flux.1-dev generation failed: {str(e)}")
            return None

    def _generate_enhanced_placeholder(self, prompt: str, quality: str, size: str, start_time: float) -> ImageGenerationResult:
        """Generate an enhanced placeholder with AI-generated description when real generation fails."""
        try:
            # Use Gemini to generate a detailed visual description
            description_prompt = f"Create a detailed, vivid description of this image concept: {prompt}. Describe colors, lighting, composition, mood, and visual details in 2-3 sentences."
            
            if self.model:
                response = self.model.generate_content(description_prompt)
                ai_description = response.text.strip()
            else:
                ai_description = f"A detailed visualization of: {prompt}"
            
            # Create enhanced placeholder image data (SVG with gradient and details)
            width, height = size.split('x')
            
            # Generate a beautiful gradient placeholder with AI description
            placeholder_svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect width="100%" height="100%" fill="url(#grad)"/>
                <text x="50%" y="40%" text-anchor="middle" fill="white" font-family="Arial" font-size="24" font-weight="bold">🎨 Flux.1-dev Image</text>
                <text x="50%" y="55%" text-anchor="middle" fill="white" font-family="Arial" font-size="16">Generated with AI Enhancement</text>
                <text x="50%" y="75%" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-family="Arial" font-size="12">Powered by Pollinations.ai</text>
            </svg>'''
            
            # Convert SVG to base64
            placeholder_data = base64.b64encode(placeholder_svg.encode('utf-8')).decode('utf-8')
            
            generation_time = (time.time() - start_time) * 1000
            
            return ImageGenerationResult(
                image_data=placeholder_data,
                model_name="pollinations-flux-1-dev-enhanced-placeholder", 
                prompt_used=f"Enhanced: {ai_description}",
                generation_time_ms=generation_time
            )
            
        except Exception as e:
            self.logger.error(f"Enhanced placeholder generation failed: {str(e)}")
            # Simple fallback
            generation_time = (time.time() - start_time) * 1000
            simple_placeholder = base64.b64encode(b'<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#667eea"/><text x="50%" y="50%" text-anchor="middle" fill="white" font-size="20">Flux.1-dev Image</text></svg>').decode('utf-8')
            
            return ImageGenerationResult(
                image_data=simple_placeholder,
                model_name="pollinations-flux-1-dev-fallback",
                prompt_used=prompt,
                generation_time_ms=generation_time
            )

    def _generate_with_pollinations_enhanced(self, prompt: str, size: str, quality: str) -> tuple[str, str]:
        """Disabled - not using Pollinations.ai anymore."""
        return None, None

    def _generate_with_leonardo(self, prompt: str, size: str, quality: str) -> tuple[str, str]:
        """Disabled - not using Leonardo.ai anymore.""" 
        return None, None

    def _generate_with_huggingface_enhanced(self, prompt: str, size: str, quality: str) -> tuple[str, str]:
        """Disabled - not using Hugging Face anymore."""
        return None, None

    def _generate_with_stability_ai(self, prompt: str, size: str, quality: str) -> tuple[str, str]:
        """Disabled - not using Stability AI anymore."""
        return None, None

    def _generate_placeholder_image(self, prompt: str, size: str) -> tuple[str, str]:
        """Generate an enhanced placeholder image with text."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Parse size
            width, height = map(int, size.split('x')) if 'x' in size else (1024, 1024)
            
            # Create image
            img = Image.new('RGB', (width, height), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font, fallback to default
            try:
                font_size = min(width, height) // 20
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Add text
            text_lines = [
                "🎨 AI Image Generation",
                "",
                f"Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}",
                "",
                f"Size: {size}",
                "",
                "⚠️ Using placeholder",
                "Configure API keys for real generation"
            ]
            
            # Calculate text positioning
            y_offset = height // 4
            line_height = font_size + 10 if hasattr(font, 'size') else 20
            
            for line in text_lines:
                if line:  # Skip empty lines
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2
                    draw.text((x, y_offset), line, fill='#666666', font=font)
                y_offset += line_height
            
            # Add border
            draw.rectangle([0, 0, width-1, height-1], outline='#cccccc', width=2)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_data, "enhanced-placeholder"
            
        except Exception as e:
            self.logger.warning(f"Enhanced placeholder generation failed: {e}")
            # Fallback to simple placeholder
            simple_placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            return simple_placeholder, "simple-placeholder" 