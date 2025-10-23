import { action } from "./_generated/server";
import { v } from "convex/values";

// We use the raw fetch API for these specific models for the requested output format (buffer/base64).
// No need to import the entire GoogleGenAI client object here.

// Helper to convert base64 audio data to ArrayBuffer
function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

// Helper to handle API calls with exponential backoff
async function fetchWithRetry(url: string, options: RequestInit, retries = 5, delay = 1000): Promise<Response> {
  try {
    const response = await fetch(url, options);
    if (response.status === 429 && retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries - 1, delay * 2);
    }
    return response;
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return fetchWithRetry(url, options, retries - 1, delay * 2);
    }
    throw error;
  }
}

export const generateAudioAction = action({
  args: { input: v.string(), voice: v.string() },
  handler: async (_, { voice, input }) => {
    // NOTE: We assume the environment variable is now named GEMINI_API_KEY
    const apiKey = process.env.GEMINI_API_KEY; 
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=${apiKey}`;

    const payload = {
        contents: [{ parts: [{ text: input }] }],
        generationConfig: {
            responseModalities: ["AUDIO"],
            speechConfig: {
                voiceConfig: {
                    prebuiltVoiceConfig: { voiceName: voice } // Use the 'voice' argument dynamically
                }
            }
        },
        model: "gemini-2.5-flash-preview-tts"
    };

    const response = await fetchWithRetry(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    const part = result?.candidates?.[0]?.content?.parts?.[0];
    const audioData = part?.inlineData?.data;

    if (!audioData) {
      console.error("Gemini TTS Error:", result);
      throw new Error("Failed to generate audio from Gemini.");
    }
    
    // The API returns raw PCM audio data, which we convert to an ArrayBuffer
    return base64ToArrayBuffer(audioData);
  },
});

export const generateThumbnailAction = action({
  args: { prompt: v.string() },
  handler: async (_, { prompt }) => {
    // NOTE: We use Imagen 3.0 for high-quality image generation
    const apiKey = process.env.GEMINI_API_KEY;
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key=${apiKey}`;

    const payload = {
        instances: [{ prompt: prompt }],
        parameters: { "sampleCount": 1 }
    };

    const response = await fetchWithRetry(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    const base64Data = result?.predictions?.[0]?.bytesBase64Encoded;

    if (!base64Data) {
      console.error("Gemini Image Gen Error:", result);
      throw new Error('Error generating thumbnail via Imagen.');
    }

    // Return the image data as an ArrayBuffer
    return base64ToArrayBuffer(base64Data);
  }
})


















// import { action } from "./_generated/server";
// import { v } from "convex/values";

// // import  from "./gemini";

// import { GoogleGenAI } from "@google/genai";

// const gemini = new GoogleGenAI({
//   apiKey: process.env.GEMINI_API_KEY,
// })

// export const generateAudioAction = action({
//   args: { input: v.string(), voice: v.string() },
//   handler: async (_, { voice, input }) => {
//     const mp3 = await gemini.audio.speech.create({
//       model: "tts-1",
//       voice: voice as GoogleGenAI['voice'],
//       input,
//     });

//     const buffer = await mp3.arrayBuffer();
    
//     return buffer;
//   },
// });

// export const generateThumbnailAction = action({
//   args: { prompt: v.string() },
//   handler: async (_, { prompt }) => {
//     const response = await ai.models.generateContent({
//       model: 'dall-e-3',
//       prompt,
//       size: '1024x1024',
//       quality: 'standard',
//       n: 1,
//     })

//     const url = response.data[0].url;

//     if(!url) {
//       throw new Error('Error generating thumbnail');
//     }

//     const imageResponse = await fetch(url);
//     const buffer = await imageResponse.arrayBuffer();
//     return buffer;
//   }
// })