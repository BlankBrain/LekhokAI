'use client';

import React, { useState, FormEvent } from 'react';
import StoryInput from '@/components/story/StoryInput';
import StoryDisplay from '@/components/story/StoryDisplay';
import ImageDisplay from '@/components/story/ImageDisplay';

export default function HomePage() {
  const [storyIdea, setStoryIdea] = useState('');
  const [character, setCharacter] = useState('himu'); // Placeholder, will fetch from backend
  const [story, setStory] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [loading, setLoading] = useState(false);

  // Placeholder for API call
  const handleGenerate = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setStory('');
    setImagePrompt('');
    // TODO: Replace with real API call
    setTimeout(() => {
      setStory('Generated story will appear here.');
      setImagePrompt('Generated image prompt will appear here.');
      setLoading(false);
    }, 1200);
  };

  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Story Generator</h1>
      <form onSubmit={handleGenerate} className="space-y-4 bg-white/10 p-6 rounded-lg shadow">
        <label className="block font-medium">Story Idea</label>
        <textarea
          className="w-full p-2 rounded border border-gray-300 focus:outline-none focus:ring"
          rows={4}
          value={storyIdea}
          onChange={e => setStoryIdea(e.target.value)}
          placeholder="Describe your story idea..."
          required
        />
        <label className="block font-medium mt-4">Character</label>
        <select
          className="w-full p-2 rounded border border-gray-300"
          value={character}
          onChange={e => setCharacter(e.target.value)}
        >
          <option value="himu">হিমু (Himu)</option>
          {/* TODO: Populate from backend */}
        </select>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded font-semibold hover:bg-blue-700 transition"
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Story'}
        </button>
      </form>
      <section className="mt-8">
        <h2 className="text-xl font-semibold mb-2">Generated Story</h2>
        <div className="bg-gray-100 p-4 rounded min-h-[80px]">{story}</div>
      </section>
      <section className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Image Prompt</h2>
        <div className="bg-gray-100 p-4 rounded min-h-[60px]">{imagePrompt}</div>
      </section>
    </main>
  );
} 