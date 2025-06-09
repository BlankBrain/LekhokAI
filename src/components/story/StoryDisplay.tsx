interface StoryDisplayProps {
  story: string;
}

export default function StoryDisplay({ story }: StoryDisplayProps) {
  return (
    <div className="prose prose-indigo max-w-none">
      <div className="whitespace-pre-wrap text-gray-700">{story}</div>
    </div>
  );
} 