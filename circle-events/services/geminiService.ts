
import { GoogleGenAI, Type } from "@google/genai";

// GeminiService provides AI features for event management and voice commands
export class GeminiService {
  /**
   * Processes natural language commands from the voice assistant.
   * Returns structured instructions for the app to execute.
   */
  async processVoiceCommand(command: string) {
    try {
      // Create a fresh instance to ensure the most up-to-date API key is used
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: command,
        config: {
          systemInstruction: `You are an AI assistant for "Circle Events", a premium event platform. 
          Your goal is to parse user voice commands and decide the action.
          Return a JSON object with:
          - action: "search", "navigate", or "unknown"
          - query: extracted search terms (if search)
          - destination: page name like "explore", "host", "attending" (if navigate)
          - message: a natural language confirmation of what you're doing.`,
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              action: { type: Type.STRING },
              query: { type: Type.STRING },
              destination: { type: Type.STRING },
              message: { type: Type.STRING },
            },
            required: ['action', 'message']
          }
        }
      });
      // response.text is a property, not a method
      const jsonStr = response.text?.trim() || '{}';
      return JSON.parse(jsonStr);
    } catch (error) {
      console.error("Gemini Command Processing Error:", error);
      return { action: 'unknown', message: "Sorry, I couldn't understand that command." };
    }
  }

  /**
   * Generates a high-quality, professional event description from user ideas.
   * Uses Gemini 3 Pro for advanced creative writing capability.
   */
  async generateEventDescription(brief: string) {
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `Generate a professional, compelling event description based on these details: ${brief}`,
        config: {
          systemInstruction: "You write high-end, engaging event copy for a premium SaaS platform. Be concise but evocative."
        }
      });
      // response.text is a property, not a method
      return response.text || brief;
    } catch (error) {
      console.error("Gemini Content Gen Error:", error);
      return brief;
    }
  }
}

export const gemini = new GeminiService();
