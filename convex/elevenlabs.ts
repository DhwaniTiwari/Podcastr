"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";
import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
import { Readable } from 'stream';

// NOTE: The ElevenLabsClient is initialized inside the handler to ensure the 
// ELEVEN_LABS_API_KEY secret is loaded by the Convex Node.js environment.

// Helper to convert the Web ReadableStream returned by the Eleven Labs SDK 
// to an ArrayBuffer suitable for Convex storage.
async function streamToArrayBuffer(stream: ReadableStream<Uint8Array>): Promise<ArrayBuffer> {
    const reader = stream.getReader();
    const chunks: Buffer[] = [];
    
    // Convert Web ReadableStream to Node.js Readable
    const nodeReadable = new Readable({
        async read() {
            const { done, value } = await reader.read();
            if (done) {
                this.push(null);
            } else {
                this.push(value);
            }
        },
    });

    // Collect all chunks from the Node.js Readable stream
    return new Promise((resolve, reject) => {
        nodeReadable.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
        nodeReadable.on('error', reject);
        nodeReadable.on('end', () => {
            const buffer = Buffer.concat(chunks);
            // slice is needed to return the underlying ArrayBuffer
            resolve(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.length));
        });
    });
}

// -------------------------------------------------------------------------
// CONVEX ACTION TO GENERATE AUDIO
// -------------------------------------------------------------------------

export const generateAudioAction = action({
    // 'voice' holds the Eleven Labs Voice ID, 'input' holds the text prompt.
    args: { input: v.string(), voice: v.string() }, 
    handler: async (_, { voice, input }) => {
        
        // ⭐ FIX: Initialize the client INSIDE the handler
        const elevenlabs = new ElevenLabsClient({
            apiKey: process.env.ELEVENLABS_API_KEY, 
        });
        
        // This call sends the voice ID (voice) and the text prompt (input) to Eleven Labs.
        const audioStream = await elevenlabs.textToSpeech.convert(voice, { 
            text: input,
            modelId: 'eleven_multilingual_v2', 
            outputFormat: 'mp3_44100_128', 
        });

        // Convert the stream into an ArrayBuffer for Convex storage
        const audioArrayBuffer = await streamToArrayBuffer(audioStream);

        if (audioArrayBuffer.byteLength === 0) {
            throw new Error("Failed to generate audio from Eleven Labs: empty response.");
        }
        
        return audioArrayBuffer;
    },
});