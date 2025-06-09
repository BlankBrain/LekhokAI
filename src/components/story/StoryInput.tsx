import { useState } from 'react';

interface StoryInputProps {
  onGenerate: (storyIdea: string) => void;
  isGenerating: boolean;
}

export default function StoryInput({ onGenerate, isGenerating }: StoryInputProps) {
  const [storyIdea, setStoryIdea] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (storyIdea.trim()) {
      onGenerate(storyIdea);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="story-idea" className="block text-sm font-medium text-gray-700">
          Story Idea
        </label>
        <div className="mt-1">
          <textarea
            id="story-idea"
            name="story-idea"
            rows={4}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter your story idea here..."
            value={storyIdea}
            onChange={(e) => setStoryIdea(e.target.value)}
            disabled={isGenerating}
          />
        </div>
      </div>
      <div>
        <button
          type="submit"
          disabled={isGenerating || !storyIdea.trim()}
          className="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isGenerating ? 'Generating...' : 'Generate Story'}
        </button>
      </div>
    </form>
  );
} 